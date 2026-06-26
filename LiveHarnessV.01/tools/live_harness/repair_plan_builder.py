from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, ledger, utc_id
from .loopback_router import route_validation_failure


def build_repair_plan(run_dir: Path, loop_index: int, validation: dict[str, Any]) -> dict[str, Any]:
    route = route_validation_failure(validation)
    plan = {
        "schema": "liveharness.repair-plan.v1",
        "loop_index": loop_index,
        "created_at": utc_id(),
        "route": route,
        "required_fix": validation.get("failed_filters", []),
        "instructions": [
            "Repair only the targeted failure root cause.",
            "Preserve the master interpretation and public-output membrane.",
            "Write repaired output back to the sandbox, not directly to docs/.",
        ],
    }
    write_json(run_dir / "loops" / f"repair-plan-{loop_index:03d}.json", plan)
    ledger("build-ledger.jsonl", {"time": utc_id(), "event": "repair.plan.created", "loop_index": loop_index, "target": route.get("target"), "failed": validation.get("failed_filters", [])})
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a repair plan from validation summary.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--loop-index", type=int, default=1)
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "massive-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    validation = read_json(run_dir / "validation" / "validation-summary.json", {})
    print(json.dumps(build_repair_plan(run_dir, args.loop_index, validation), indent=2))


if __name__ == "__main__":
    main()
