from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import harness_root, repo_root, read_json, write_json, ledger, utc_id
from .learning_compressor import capsule_for


def apply(plan: dict[str, Any], scored: list[dict[str, Any]], run_dir: Path) -> dict[str, Any]:
    repo = repo_root()
    harness = harness_root()
    by_id = {str(item.get("id")): item for item in scored}
    state_path = harness / "state" / "purge-state.json"
    state = read_json(state_path, {"version": 1, "applied_commands": []})
    applied = set(state.get("applied_commands", []))
    hidden: list[str] = []
    archived: list[str] = []
    planned_paths: list[str] = []
    for decision in plan.get("decisions", []):
        game_id = str(decision.get("game_id"))
        if not game_id or not decision.get("safe_to_apply", False):
            continue
        command_id = f"prune-game:{game_id}:v1"
        if command_id in applied:
            continue
        entry = by_id.get(game_id, {"id": game_id})
        capsule = capsule_for(entry, "pruned")
        capsule["prune_command_id"] = command_id
        capsule["folder_retention"] = "hidden_from_manifest; file removal is applied by a later hardened janitor stage"
        capsule_path = harness / "archive" / "game-capsules" / f"{game_id}.json"
        write_json(capsule_path, capsule)
        archived.append(str(capsule_path.relative_to(harness)))
        planned_paths.append(str(entry.get("folder", f"docs/games/{game_id}")))
        hidden.append(game_id)
        applied.add(command_id)
        ledger("purge-ledger.jsonl", {"time": utc_id(), "event": "game.hidden_after_capsule", "game_id": game_id, "command_id": command_id, "capsule": str(capsule_path.relative_to(harness))})
    state["applied_commands"] = sorted(applied)
    state["updated_at"] = utc_id()
    write_json(state_path, state)
    manifest_path = repo / "docs" / "games.json"
    manifest = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = []
    hidden_ids = set(hidden)
    manifest = [item for item in manifest if str(item.get("id")) not in hidden_ids]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    result = {"hidden_game_ids": hidden, "capsules": archived, "planned_file_prune_paths": planned_paths, "applied_commands": sorted(applied)}
    write_json(run_dir / "purge" / "purge-result.json", result)
    return result
