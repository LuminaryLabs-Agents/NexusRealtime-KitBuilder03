from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import repo_root, tool_result

HARD_TERMS = ["NVIDIA", "OpenAI", "chat.completions", "reasoning_budget", "nemotron", "workflow_dispatch"]
SOFT_TERMS = ["LLM", "orchestrator", "workflow", "harness", "agent"]
SCAN_SUFFIXES = {".html", ".css", ".js", ".json", ".md"}


def _active_public_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in ["index.html", "cleanup.html", "games.json", "launcher.css"]:
        path = root / name
        if path.exists() and path.is_file():
            files.append(path)
    manifest_path = root / "games.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    except json.JSONDecodeError:
        manifest = []
    if isinstance(manifest, list):
        for item in manifest:
            if not isinstance(item, dict) or item.get("visibility") == "hidden":
                continue
            url = str(item.get("url", ""))
            folder = root / url.strip("/")
            if folder.exists() and folder.is_dir():
                files.extend([p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in SCAN_SUFFIXES])
    return list(dict.fromkeys(files))


def scan_docs() -> dict[str, Any]:
    root = repo_root() / "docs"
    if not root.exists():
        return tool_result("public_output_membrane_check", True, "docs/ does not exist; skipped")
    hard_hits: list[dict[str, str]] = []
    warnings: list[str] = []
    files = _active_public_files(root)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        low = text.lower()
        for term in HARD_TERMS:
            if term.lower() in low:
                hard_hits.append({"path": str(path.relative_to(repo_root())), "term": term})
        for term in SOFT_TERMS:
            if term.lower() in low:
                warnings.append(f"{path.relative_to(repo_root())}: soft term {term}")
    if hard_hits:
        return tool_result("public_output_membrane_check", False, "Control-plane terms found in active public docs output", errors=[json.dumps(x) for x in hard_hits[:50]], warnings=warnings[:50], data={"hard_hits": hard_hits, "files_scanned": len(files)})
    return tool_result("public_output_membrane_check", True, "No hard control-plane terms found in active public docs output", warnings=warnings[:50], data={"files_scanned": len(files)})


if __name__ == "__main__":
    print(json.dumps(scan_docs(), indent=2))
