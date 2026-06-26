from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json, ledger, utc_id


def fill(run_dir: Path, slot_id: str, slot_type: str, patch: dict[str, Any]) -> dict[str, Any]:
    out = {"slot_id": slot_id, "status": "filled", "summary": f"Filled {slot_id}", "patch": patch, "risks": [], "requested_tools": []}
    write_json(run_dir / "slots" / f"{slot_id}.response.json", out)
    ledger("action-ledger.jsonl", {"time": utc_id(), "agent_id": slot_id, "move": "FILL_SLOT"})
    return out
