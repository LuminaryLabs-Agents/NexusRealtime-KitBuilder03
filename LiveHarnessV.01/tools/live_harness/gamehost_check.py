from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import repo_root, tool_result

REQUIRED = ["window.GameHost", "getState", "movement", "inventory", "buildBreak", "domainTrace", "sequence"]


def check_path(path: Path | None = None) -> dict[str, Any]:
    root = path or repo_root() / "docs"
    if not root.exists():
        return tool_result("gamehost_check", False, "No docs output to scan", ["docs missing"])
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in root.rglob("*.js"))
    missing = [term for term in REQUIRED if term not in text]
    return tool_result("gamehost_check", not missing, "GameHost contract present" if not missing else "GameHost contract missing", [f"missing {term}" for term in missing], data={"required": REQUIRED})


if __name__ == "__main__":
    print(json.dumps(check_path(), indent=2))
