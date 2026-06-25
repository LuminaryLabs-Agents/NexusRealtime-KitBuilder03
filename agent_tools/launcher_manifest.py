from __future__ import annotations

from pathlib import Path

from .common import load_json, result


def run(context: dict | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    docs = Path("docs")
    index = docs / "index.html"
    manifest_path = docs / "games.json"
    if not index.exists():
        errors.append("docs/index.html is missing")
    if not manifest_path.exists():
        errors.append("docs/games.json is missing")
        manifest = []
    else:
        manifest = load_json(manifest_path, [])
        if not isinstance(manifest, list):
            errors.append("docs/games.json must be a list")
            manifest = []
    for item in manifest:
        if not isinstance(item, dict):
            errors.append("manifest entry is not an object")
            continue
        url = str(item.get("url") or "")
        game_id = str(item.get("id") or "")
        if url.startswith("games/"):
            folder = docs / url.strip("/")
        elif game_id:
            folder = docs / "games" / game_id
        else:
            errors.append("manifest entry has neither url nor id")
            continue
        if not folder.exists():
            errors.append(f"manifest points to missing folder: {folder}")
            continue
        for name in ("index.html", "style.css", "game.js"):
            if not (folder / name).exists():
                errors.append(f"{folder}/{name} is missing")
    if not manifest:
        warnings.append("games.json has no game entries yet")
    ok = not errors
    return result("launcher_manifest_check", ok, "Launcher manifest passed" if ok else "Launcher manifest failed", errors, warnings, {"entries": len(manifest)})
