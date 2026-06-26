from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, ledger, utc_id

DEFAULT_ACTION_AST = {
    "schema": "liveharness.action-ast.v1",
    "stage_id": "40-prototype",
    "nodes": [
        {"node_id": "read_master_interpretation", "allowed_actions": ["READ_ARTIFACT", "THINK"]},
        {"node_id": "align_goal", "allowed_actions": ["ALIGN_GOAL", "THINK"]},
        {"node_id": "draft_or_inspect_output", "allowed_actions": ["PLAN", "READ_ARTIFACT", "WRITE_SET_PROPOSE"]},
        {"node_id": "gate_boundary_action", "allowed_actions": ["ASK_GATE", "APPLY_WRITE_SET"]},
        {"node_id": "run_tools", "allowed_actions": ["RUN_TOOL"]},
        {"node_id": "self_review", "allowed_actions": ["SELF_REVIEW", "LOOPBACK", "FINAL_REPORT"]}
    ],
    "turn_policy": {
        "max_consecutive_think_actions": 3,
        "max_alignment_rounds_before_action": 2,
        "must_act_after_plan": True,
        "must_validate_after_write": True,
        "must_self_review_before_stage_advance": True
    }
}


def ensure_action_ast(run_dir: Path, stage_id: str = "40-prototype") -> dict[str, Any]:
    path = run_dir / "input" / "action-ast.json"
    ast = read_json(path, {}) if path.exists() else dict(DEFAULT_ACTION_AST)
    ast["stage_id"] = stage_id
    write_json(path, ast)
    ledger("stage-ledger.jsonl", {"time": utc_id(), "event": "action_ast.ready", "stage_id": stage_id, "path": str(path)})
    return ast


def next_node(ast: dict[str, Any], completed_nodes: list[str]) -> dict[str, Any] | None:
    for node in ast.get("nodes", []):
        if node.get("node_id") not in completed_nodes:
            return node
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or inspect a LiveHarness action AST.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--stage", default="40-prototype")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "action-ast-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(ensure_action_ast(run_dir, args.stage), indent=2))


if __name__ == "__main__":
    main()
