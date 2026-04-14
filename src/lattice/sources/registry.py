from __future__ import annotations

from pathlib import Path
from typing import Any

from lattice.utils import read_json


def load_source_registry(path: str | Path) -> dict[str, Any]:
    return read_json(path)


def registry_source_map(path: str | Path) -> dict[str, dict[str, Any]]:
    registry = load_source_registry(path)
    return {source["name"]: source for source in registry.get("sources", [])}

