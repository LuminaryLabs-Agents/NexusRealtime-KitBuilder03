from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json


def add(run_dir: Path, item: dict[str, Any]) -> dict[str, Any]:
    item.setdefault("id", "context")
    write_json(run_dir / "injections" / (item["id"] + ".json"), item)
    return item


def active() -> list[dict[str, Any]]:
    return []
