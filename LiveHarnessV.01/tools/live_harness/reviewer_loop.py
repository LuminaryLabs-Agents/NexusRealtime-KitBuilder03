from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json, ledger, utc_id


def review(run_dir: Path, tools: dict[str, Any]) -> dict[str, Any]:
    ok = bool(tools.get("ok"))
    out = {"approve": ok, "summary": "Review approved generated output." if ok else "Review found tool failures.", "issues": [] if ok else ["One or more tools failed."], "recommended_action": "MARK_COMPLETE" if ok else "REPAIR"}
    write_json(run_dir / "review" / "review.json", out)
    write_json(run_dir / "review" / "review.md", {"summary": out["summary"]})
    ledger("review-ledger.jsonl", {"time": utc_id(), "approve": ok, "summary": out["summary"]})
    return out
