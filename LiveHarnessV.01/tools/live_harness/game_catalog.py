from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import repo_root, harness_root, read_json, write_json, utc_id, ledger


def load_manifest() -> list[dict[str, Any]]:
    path = repo_root() / "docs" / "games.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def scan() -> list[dict[str, Any]]:
    repo = repo_root()
    games_root = repo / "docs" / "games"
    manifest = load_manifest()
    by_id = {str(item.get("id")): dict(item) for item in manifest if isinstance(item, dict) and item.get("id")}
    if games_root.exists():
        for folder in sorted(p for p in games_root.iterdir() if p.is_dir()):
            game_id = folder.name
            item = by_id.setdefault(game_id, {"id": game_id, "title": game_id, "url": f"games/{game_id}/"})
            item.setdefault("url", f"games/{game_id}/")
    entries: list[dict[str, Any]] = []
    for game_id, item in by_id.items():
        url = str(item.get("url") or f"games/{game_id}/")
        folder = repo / "docs" / url.strip("/")
        files = {name: (folder / name).exists() for name in ["index.html", "style.css", "game.js", "README.md"]}
        entry = dict(item)
        entry.update({
            "id": game_id,
            "folder": str(folder.relative_to(repo)) if folder.exists() else str(folder.relative_to(repo)),
            "exists": folder.exists(),
            "files": files,
            "file_count": len([p for p in folder.rglob("*") if p.is_file()]) if folder.exists() else 0,
            "status": item.get("status") or "active",
            "visibility": item.get("visibility") or "public",
        })
        entries.append(entry)
    return entries


def write_index(entries: list[dict[str, Any]]) -> dict[str, Any]:
    index = {"version": 1, "updated_at": utc_id(), "games": entries}
    write_json(harness_root() / "state" / "gallery-index.json", index)
    ledger("project-ledger.jsonl", {"time": utc_id(), "event": "gallery.indexed", "games": len(entries)})
    return index
