from __future__ import annotations

from typing import Any

from .prepare import prepare_documents


def extract_documents(
    resolved_documents: list[dict[str, str]],
    *,
    explicit_config: str | None = None,
    workspace_dir: str = ".cds_pipeline",
    enable_vision: bool | None = None,
) -> dict[str, Any]:
    del enable_vision
    return prepare_documents(
        resolved_documents,
        explicit_config=explicit_config,
        workspace_dir=workspace_dir,
    )
