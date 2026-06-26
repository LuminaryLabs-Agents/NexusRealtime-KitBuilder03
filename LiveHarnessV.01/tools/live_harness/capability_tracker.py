from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import harness_root, read_json, write_json, ledger, utc_id


def update(capsules: list[dict[str, Any]], run_dir: Path) -> dict[str, Any]:
    path = harness_root() / "state" / "capability-ledger.json"
    state = read_json(path, {"version": 1, "capabilities": []})
    capabilities = list(state.get("capabilities", []))
    by_id = {item.get("id"): item for item in capabilities if isinstance(item, dict)}
    for capsule in capsules:
        for cap in capsule.get("features_promoted_to_memory", []):
            item = by_id.get(cap) or {"id": cap, "status": "candidate", "evidence": []}
            item.setdefault("evidence", []).append(f"{capsule.get('game_id')} score={capsule.get('score')}")
            if cap == "static.output.contract" and capsule.get("score", 0) >= 70:
                item["status"] = "stable"
            by_id[cap] = item
    state["capabilities"] = sorted(by_id.values(), key=lambda x: x.get("id", ""))
    state["updated_at"] = utc_id()
    write_json(path, state)
    write_json(run_dir / "learning" / "capability-update.json", state)
    ledger("capability-ledger.jsonl", {"time": utc_id(), "event": "capabilities.updated", "count": len(state["capabilities"])})
    return state
