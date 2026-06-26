from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, ledger, utc_id

REQUIRED = ["worker_id", "slot_id", "summary", "provides"]


def validate_result(data: dict[str, Any]) -> dict[str, Any]:
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append(f"missing {key}")
    if not isinstance(data.get("provides", []), list):
        errors.append("provides must be a list")
    return {"ok": not errors, "errors": errors}


def validate_slots(run_dir: Path) -> dict[str, Any]:
    swarm_dir = run_dir / "swarm"
    results = []
    for worker_dir in sorted(p for p in swarm_dir.glob("worker-*") if p.is_dir()):
        data = read_json(worker_dir / "response.json", {})
        validation = validate_result(data)
        status = read_json(worker_dir / "status.json", {})
        status["schema_valid"] = validation["ok"]
        status["schema_errors"] = validation["errors"]
        write_json(worker_dir / "status.json", status)
        results.append({"worker_id": worker_dir.name, "slot_id": data.get("slot_id"), "ok": validation["ok"], "errors": validation["errors"]})
    summary = {
        "schema": "liveharness.slot-validation-summary.v1",
        "workers_total": len(results),
        "workers_valid": sum(1 for r in results if r["ok"]),
        "workers_invalid": sum(1 for r in results if not r["ok"]),
        "results": results,
        "ok": all(r["ok"] for r in results) if results else False,
        "completed_at": utc_id(),
    }
    write_json(run_dir / "swarm" / "validation-summary.json", summary)
    ledger("validation-ledger.jsonl", {"time": utc_id(), "event": "slots.validated", "ok": summary["ok"], "valid": summary["workers_valid"], "invalid": summary["workers_invalid"]})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LiveHarness slot responses.")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "swarm-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(validate_slots(run_dir), indent=2))


if __name__ == "__main__":
    main()
