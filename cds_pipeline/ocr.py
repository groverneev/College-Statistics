from __future__ import annotations

import base64
from dataclasses import dataclass, field
import importlib.util
import json
import os
from pathlib import Path
import re
from typing import Any, Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class OcrResult:
    text: str
    method: str
    confidence: float | None = None
    blocks: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


class OcrProvider(Protocol):
    name: str

    def extract_page(self, image_path: Path) -> OcrResult: ...


def _data_url(image_path: Path) -> str:
    suffix = image_path.suffix.lower()
    mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


class PaddleOcrProvider:
    name = "paddleocr-vl-1.6"

    def __init__(self) -> None:
        try:
            from paddleocr import PaddleOCRVL  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "PaddleOCR-VL is not installed. Use a Python 3.12 environment and run: "
                "python -m pip install paddlepaddle paddleocr"
            ) from exc
        self._pipeline = PaddleOCRVL(pipeline_version="v1.6")

    def extract_page(self, image_path: Path) -> OcrResult:
        results = list(self._pipeline.predict(str(image_path)))
        if not results:
            raise RuntimeError(f"PaddleOCR-VL returned no result for {image_path}")
        result = results[0]
        payload = result.json
        markdown = result.markdown
        text = str(markdown.get("markdown_texts", "")) if isinstance(markdown, dict) else str(markdown)
        blocks = payload.get("parsing_res_list", []) if isinstance(payload, dict) else []
        return OcrResult(text=text, method=self.name, blocks=blocks, raw=payload)


_REFERENCE_TAG_RE = re.compile(r"<\|/?ref\|>")
_DETECTION_TAG_RE = re.compile(r"<\|det\|>.*?<\|/det\|>", re.DOTALL)


def _clean_unlimited_ocr_text(text: str) -> str:
    """Remove grounding metadata without deleting the recognized content."""
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        # Unlimited-OCR emits detection coordinates before the corresponding text.
        line = _DETECTION_TAG_RE.sub("", line)
        line = _REFERENCE_TAG_RE.sub("", line)
        cleaned_lines.append(line.rstrip())
    return "\n".join(cleaned_lines).strip()


class UnlimitedOcrProvider:
    name = "unlimited-ocr"

    def __init__(self, *, base_url: str | None = None) -> None:
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("The Unlimited-OCR adapter requires: pip install openai") from exc
        self._client = OpenAI(
            api_key=os.environ.get("CDS_UNLIMITED_OCR_API_KEY", "EMPTY"),
            base_url=base_url or os.environ.get("CDS_UNLIMITED_OCR_URL", "http://127.0.0.1:8000/v1"),
            timeout=1200,
        )
        self._model = os.environ.get("CDS_UNLIMITED_OCR_MODEL", "baidu/Unlimited-OCR")

    def extract_page(self, image_path: Path) -> OcrResult:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "<image>document parsing."},
                        {"type": "image_url", "image_url": {"url": _data_url(image_path)}},
                    ],
                }
            ],
            max_tokens=16384,
            temperature=0,
            extra_body={
                "skip_special_tokens": False,
                "vllm_xargs": {"ngram_size": 35, "window_size": 128},
            },
        )
        raw_text = response.choices[0].message.content or ""
        clean_text = _clean_unlimited_ocr_text(raw_text)
        return OcrResult(text=clean_text, method=self.name, raw={"grounded_text": raw_text})


class OllamaOcrProvider:
    name = "ollama-vision-ocr"

    def __init__(self) -> None:
        self._base_url = os.environ.get("CDS_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        self._model = os.environ.get("CDS_LOCAL_OCR_MODEL", "qwen3.5:9b")

    def extract_page(self, image_path: Path) -> OcrResult:
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Transcribe this Common Data Set page exactly as Markdown. Preserve question IDs, "
                        "headings, row labels, column headers, every number, and x/checkbox marks. Do not "
                        "summarize, calculate, or interpret."
                    ),
                    "images": [encoded],
                }
            ],
            "stream": False,
            "think": False,
            "keep_alive": os.environ.get("CDS_OLLAMA_KEEP_ALIVE", "15m"),
            "options": {
                "temperature": 0,
                "num_ctx": int(os.environ.get("CDS_OLLAMA_CONTEXT", "16384")),
            },
        }
        request = Request(
            f"{self._base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=1200) as response:
                result = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(f"Ollama OCR request failed: {exc}") from exc
        text = result.get("message", {}).get("content", "")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(f"Ollama model {self._model} returned no OCR text.")
        return OcrResult(text=text.strip(), method=f"{self.name}/{self._model}", raw=result)


class MistralOcrProvider:
    name = "mistral-ocr-4"

    def __init__(self) -> None:
        self._api_key = os.environ.get("MISTRAL_API_KEY")
        if not self._api_key:
            raise RuntimeError("Mistral OCR requires the MISTRAL_API_KEY environment variable.")
        self._model = os.environ.get("CDS_MISTRAL_OCR_MODEL", "mistral-ocr-4-0")

    def extract_page(self, image_path: Path) -> OcrResult:
        payload = {
            "model": self._model,
            "document": {"type": "image_url", "image_url": _data_url(image_path)},
            "table_format": "html",
            "include_blocks": True,
            "confidence_scores_granularity": "word",
        }
        request = Request(
            "https://api.mistral.ai/v1/ocr",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(f"Mistral OCR request failed: {exc}") from exc
        pages = result.get("pages", [])
        if not pages:
            raise RuntimeError(f"Mistral OCR returned no page for {image_path}")
        page = pages[0]
        scores = page.get("confidence_scores") or {}
        confidence = scores.get("average_page_confidence_score")
        return OcrResult(
            text=page.get("markdown", ""),
            method=self.name,
            confidence=float(confidence) if confidence is not None else None,
            blocks=page.get("blocks") or [],
            tables=page.get("tables") or [],
            raw=result,
        )


def available_ocr_providers() -> list[str]:
    providers: list[str] = []
    if os.environ.get("CDS_UNLIMITED_OCR_URL"):
        providers.append("unlimited")
    try:
        base_url = os.environ.get("CDS_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        with urlopen(f"{base_url}/api/tags", timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        model = os.environ.get("CDS_LOCAL_OCR_MODEL", "qwen3.5:9b")
        if any(item.get("name") == model for item in payload.get("models", [])):
            providers.append("ollama")
    except Exception:
        pass
    if os.environ.get("MISTRAL_API_KEY"):
        providers.append("mistral")
    if importlib.util.find_spec("paddleocr") is not None:
        providers.append("paddle")
    return providers


def create_ocr_provider(name: str) -> OcrProvider | None:
    normalized = name.lower()
    if normalized == "none":
        return None
    if normalized == "auto":
        available = available_ocr_providers()
        if not available:
            return None
        normalized = available[0]
    if normalized == "unlimited":
        return UnlimitedOcrProvider()
    if normalized == "ollama":
        return OllamaOcrProvider()
    if normalized == "mistral":
        return MistralOcrProvider()
    if normalized == "paddle":
        return PaddleOcrProvider()
    raise ValueError(f"Unknown OCR provider: {name}")


def provider_setup_help() -> list[str]:
    return [
        "Ollama OCR: install Ollama and run `ollama pull qwen3.5:9b` (zero-key fallback).",
        "Unlimited-OCR (recommended for a compatible local NVIDIA GPU): run its vLLM Docker server and set "
        "CDS_UNLIMITED_OCR_URL=http://127.0.0.1:8000/v1.",
        "PaddleOCR-VL: in Python 3.12 run `python -m pip install paddlepaddle paddleocr`.",
        "Mistral OCR 4: set MISTRAL_API_KEY; no local model installation is required.",
    ]
