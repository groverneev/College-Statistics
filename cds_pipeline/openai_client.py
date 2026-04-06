from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
_ENV_LOADED = False


class OpenAIVisionClient:
    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        _load_local_env()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for vision extraction.")

        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency guard
            raise RuntimeError(f"OpenAI SDK unavailable: {exc}") from exc

        self._client = OpenAI(api_key=self.api_key)

    def classify_page(
        self,
        *,
        page_number: int,
        image_bytes: bytes,
        section_aliases: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        aliases = section_aliases or {}
        alias_lines = [f"- {section}: {', '.join(values)}" for section, values in sorted(aliases.items()) if values]
        alias_text = "\n".join(alias_lines) or "- none"
        prompt = (
            "You are reviewing a single Common Data Set PDF page image. "
            "Identify which CDS sections from this fixed list are meaningfully present on the page: "
            "B1, B2, C1, C9, F1, G1, H2. "
            "Do not guess. Only return sections that are visibly present on this page.\n\n"
            f"Known school-specific aliases:\n{alias_text}\n\n"
            f"Current page number: {page_number}\n"
            "Return JSON with this shape: "
            '{"page": <int>, "sections": [{"section": "C1", "confidence": 0.97}]}.'
        )
        schema = {
            "name": "page_classification",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "page": {"type": "integer"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "section": {"type": "string", "enum": ["B1", "B2", "C1", "C9", "F1", "G1", "H2"]},
                                "confidence": {"type": "number"},
                            },
                            "required": ["section", "confidence"],
                        },
                    },
                },
                "required": ["page", "sections"],
            },
        }
        return self._json_chat(prompt=prompt, image_bytes=image_bytes, schema=schema)

    def extract_section(
        self,
        *,
        section: str,
        page_number: int,
        image_bytes: bytes,
        section_prompt: str,
        allowed_fields: list[str],
    ) -> dict[str, Any]:
        fields = ", ".join(allowed_fields)
        prompt = (
            "You are extracting machine-readable data from a single Common Data Set page image. "
            "Read the page visually. Do not invent values. "
            "Only return fields that are explicitly supported by visible text or numbers on this page.\n\n"
            f"Section: {section}\n"
            f"Page number: {page_number}\n"
            f"Extraction guidance: {section_prompt}\n"
            f"Allowed output field paths: {fields}\n\n"
            "Return JSON with this shape: "
            '{"section":"C1","page":1,"candidates":[{"field":"admissions.applied","value":"12345","confidence":0.94,'
            '"evidence_label":"Applicants"}],"notes":[]}.'
        )
        schema = {
            "name": f"extract_{section.lower()}",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "section": {"type": "string"},
                    "page": {"type": "integer"},
                    "candidates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "field": {"type": "string", "enum": allowed_fields},
                                "value": {"type": ["string", "number"]},
                                "confidence": {"type": "number"},
                                "evidence_label": {"type": "string"},
                            },
                            "required": ["field", "value", "confidence", "evidence_label"],
                        },
                    },
                    "notes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["section", "page", "candidates", "notes"],
            },
        }
        return self._json_chat(prompt=prompt, image_bytes=image_bytes, schema=schema)

    def _json_chat(self, *, prompt: str, image_bytes: bytes, schema: dict[str, Any]) -> dict[str, Any]:
        data_url = _image_bytes_to_data_url(image_bytes)
        response = self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": "Return only schema-valid JSON. Never add commentary outside JSON."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            response_format={"type": "json_schema", "json_schema": schema},
        )
        return _parse_json_response(response)


def _image_bytes_to_data_url(image_bytes: bytes) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _parse_json_response(response: Any) -> dict[str, Any]:
    choice = response.choices[0]
    message = choice.message
    content = getattr(message, "content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
        content = "".join(parts)
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("OpenAI response did not include JSON content.")
    return json.loads(content)


def _load_local_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True

    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env.local"
    if not env_path.exists():
        return

    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    load_dotenv(env_path, override=False)
