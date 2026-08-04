from __future__ import annotations

import json
from pathlib import Path
import re


IMPORT_RE = re.compile(r'import\s+(\w+)\s+from\s+"\./([a-z0-9]+)\.json";')
ARRAY_ITEM_RE = re.compile(r"\b(\w+)\s+as\s+SchoolData")


def _identifier(slug: str) -> str:
    parts = [part for part in re.split(r"[^a-zA-Z0-9]+", slug) if part]
    if not parts:
        raise ValueError(f"Cannot generate an import identifier for {slug!r}")
    value = parts[0].lower() + "".join(part[:1].upper() + part[1:] for part in parts[1:])
    if value[0].isdigit():
        value = f"school{value}"
    return f"{value}Data"


def generate_registry(
    *,
    data_dir: Path = Path("src/data/schools"),
    check: bool = False,
) -> dict[str, object]:
    index_path = data_dir / "index.ts"
    source = index_path.read_text(encoding="utf-8")
    json_files = [
        path
        for path in data_dir.glob("*.json")
        if path.name not in {"generated-registry.json", "metadata.json"}
    ]
    datasets: dict[str, dict[str, object]] = {}
    for path in json_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        slug = payload.get("slug")
        name = payload.get("name")
        if not isinstance(slug, str) or not isinstance(name, str):
            raise ValueError(f"{path} must contain string name and slug fields.")
        if slug != path.stem:
            raise ValueError(f"Dataset slug {slug!r} does not match filename {path.stem!r}.")
        datasets[slug] = payload

    existing_imports = {slug: identifier for identifier, slug in IMPORT_RE.findall(source)}
    identifiers = {slug: existing_imports.get(slug, _identifier(slug)) for slug in datasets}

    import_matches = list(IMPORT_RE.finditer(source))
    if not import_matches:
        raise ValueError(f"{index_path} contains no generated school JSON imports.")
    import_start = import_matches[0].start()
    import_end = import_matches[-1].end()
    imports = "\n".join(
        f'import {identifiers[slug]} from "./{slug}.json";'
        for slug in sorted(datasets, key=lambda item: str(datasets[item]["name"]).lower())
    )
    source = source[:import_start] + imports + source[import_end:]

    array_start = source.index("export const allSchools: SchoolData[] = [")
    array_end = source.index("\n];", array_start) + len("\n];")
    old_array = source[array_start:array_end]
    reverse_existing = {identifier: slug for slug, identifier in existing_imports.items()}
    ordered_slugs: list[str] = []
    for identifier in ARRAY_ITEM_RE.findall(old_array):
        slug = reverse_existing.get(identifier)
        if slug in datasets and slug not in ordered_slugs:
            ordered_slugs.append(slug)
    ordered_slugs.extend(
        slug
        for slug in sorted(datasets, key=lambda item: str(datasets[item]["name"]).lower())
        if slug not in ordered_slugs
    )
    array = "export const allSchools: SchoolData[] = [\n" + "\n".join(
        f"  {identifiers[slug]} as SchoolData," for slug in ordered_slugs
    ) + "\n];"
    generated = source[:array_start] + array + source[array_end:]
    changed = generated != index_path.read_text(encoding="utf-8")
    if changed and not check:
        index_path.write_text(generated, encoding="utf-8")
    return {"school_count": len(datasets), "changed": changed, "check": check}
