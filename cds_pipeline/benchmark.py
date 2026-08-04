from __future__ import annotations

from pathlib import Path
import time
from typing import Any

from .extractor import extract_packet_local
from .models import SectionPacket
from .native import extract_packet_native
from .utils import read_json


def _values_match(actual: object, expected: object) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) < 1e-9
    return actual == expected


def benchmark_local_models(
    packet_dir: str | Path,
    gold_path: str | Path,
    *,
    models: list[str],
) -> dict[str, Any]:
    root = Path(packet_dir)
    gold = read_json(Path(gold_path))
    expected_domains = gold.get("domains", {})
    results: list[dict[str, Any]] = []

    for model in models:
        model_started = time.perf_counter()
        expected_count = 0
        exact_count = 0
        evidence_valid_count = 0
        domain_results: list[dict[str, Any]] = []
        model_calls = 0
        for domain, expected_values in expected_domains.items():
            packet_path = root / f"{domain}.json"
            expected_count += len(expected_values)
            if not packet_path.exists():
                domain_results.append({"domain": domain, "error": f"Missing {packet_path}"})
                continue
            packet = SectionPacket.model_validate(read_json(packet_path))
            started = time.perf_counter()
            native_extraction, native_complete = extract_packet_native(packet)
            try:
                if native_complete:
                    extraction = native_extraction
                    provider = "native"
                else:
                    model_calls += 1
                    extraction = extract_packet_local(packet, model=model)
                    native_paths = {
                        observation.path for observation in native_extraction.observations
                    }
                    extraction.observations = native_extraction.observations + [
                        observation
                        for observation in extraction.observations
                        if observation.path not in native_paths
                    ]
                    provider = model
            except Exception as exc:
                domain_results.append({"domain": domain, "error": str(exc)})
                continue
            actual = {
                observation.path: observation.value
                for observation in extraction.observations
                if observation.value is not None
            }
            verified_paths = {
                observation.path
                for observation in extraction.observations
                if observation.value is not None
                and observation.evidence
                and not observation.review_required
            }
            incorrect: list[dict[str, object]] = []
            missing: list[str] = []
            domain_exact = 0
            domain_evidence_valid = 0
            for path, expected in expected_values.items():
                if path not in actual:
                    missing.append(path)
                    continue
                if _values_match(actual[path], expected):
                    domain_exact += 1
                    if path in verified_paths:
                        domain_evidence_valid += 1
                else:
                    incorrect.append(
                        {"path": path, "expected": expected, "actual": actual[path]}
                    )
            exact_count += domain_exact
            evidence_valid_count += domain_evidence_valid
            domain_results.append(
                {
                    "domain": domain,
                    "provider": provider,
                    "seconds": round(time.perf_counter() - started, 2),
                    "expected": len(expected_values),
                    "exact": domain_exact,
                    "evidence_valid": domain_evidence_valid,
                    "missing": missing,
                    "incorrect": incorrect,
                }
            )
        results.append(
            {
                "model": model,
                "seconds": round(time.perf_counter() - model_started, 2),
                "expected": expected_count,
                "exact": exact_count,
                "evidence_valid": evidence_valid_count,
                "model_calls": model_calls,
                "exact_rate": round(exact_count / expected_count, 4) if expected_count else 0,
                "publishable_rate": (
                    round(evidence_valid_count / expected_count, 4) if expected_count else 0
                ),
                "domains": domain_results,
            }
        )
    return {
        "gold": str(Path(gold_path).resolve()),
        "packet_dir": str(root.resolve()),
        "results": results,
    }
