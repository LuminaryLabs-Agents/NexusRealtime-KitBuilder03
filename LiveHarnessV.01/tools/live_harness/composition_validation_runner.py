from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, ledger, utc_id
from . import massive_validation_runner as base
from .thin_html_filter import check as thin_html_check
from .import_map_filter import check as import_map_check
from .kit_resolution_filter import check as kit_resolution_check
from .fallback_compatibility_filter import check as fallback_compatibility_check
from .kit_proof_filter import check as kit_proof_check


def validate_sandbox(run_dir: Path, write_set: dict[str, Any]) -> dict[str, Any]:
    summary = base.validate_sandbox(run_dir, write_set)
    candidate_id = str(write_set.get("candidate_id", "candidate"))
    candidate_dir = run_dir / "sandbox" / "docs" / "games" / candidate_id
    extra = [
        thin_html_check(candidate_dir),
        import_map_check(candidate_dir),
        kit_resolution_check(run_dir, candidate_dir),
        fallback_compatibility_check(run_dir, candidate_dir),
        kit_proof_check(run_dir, candidate_dir)
    ]
    checks = extra + summary.get("checks", [])
    failed = [check["id"] for check in checks if not check.get("ok")]
    passed = [check["id"] for check in checks if check.get("ok")]
    loopback = None
    if failed:
        loopback = {"target": "composition-repair-worker", "reason": f"{failed[0]} failed"}
    merged = {**summary, "ok": not failed, "passed_filters": passed, "failed_filters": failed, "checks": checks, "loopback": loopback, "repair_prompt": {"required_fix": failed, "target": loopback["target"] if loopback else None} if failed else None, "completed_at": utc_id()}
    write_json(run_dir / "validation" / "validation-summary.json", merged)
    for check in extra:
        write_json(run_dir / "validation" / f"{check['id']}.json", check)
    ledger("validation-ledger.jsonl", {"time": utc_id(), "event": "composition.validated", "candidate_id": candidate_id, "ok": merged["ok"], "failed": failed})
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "composition-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    write_set = read_json(run_dir / "write-sets" / "final-write-set.json", {})
    print(json.dumps(validate_sandbox(run_dir, write_set), indent=2))


if __name__ == "__main__":
    main()
