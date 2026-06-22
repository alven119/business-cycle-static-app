"""Shadow model contract loaders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


SHADOW_MODEL_SPEC_PATH = Path("specs/audits/book_faithful_shadow_model_v2.yaml")


def load_shadow_model_spec(path: str | Path = SHADOW_MODEL_SPEC_PATH) -> dict[str, Any]:
    """Load the QA5 shadow model metadata."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_model_v2"
    ]

