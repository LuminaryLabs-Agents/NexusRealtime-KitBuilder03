from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, repo_root, read_json, write_json, write_text, ledger, utc_id
from .gate_adapter import review_action

ALLOWED_ROOTS = ["docs/", "generated/", "src/", "LiveHarnessV.01/runs/", "LiveHarnessV.01/state/", "LiveHarnessV.01/archive/"]


def _allowed(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("/")
    return not (".." in Path(normalized).parts) and any(normalized.startswith(root) for root in ALLOWED_ROOTS)


def apply_write_set(write_set: dict[str, Any], run_dir: Path, require_gate: bool = True) -> dict[str, Any]:
    files = write_set.get("files", [])
    paths = [str(item.get("path", "")) for item in files if isinstance(item, dict)]
    action = {"type": "APPLY_WRITE_SET", "input": write_set.get("write_set_id", "write-set"), "paths": paths}
    gate = review_action(action, run_dir) if require_gate else {"decision": "allow"}
    if gate.get("decision") != "allow":
        result = {"ok": False, "gate": gate, "applied": []}
        write_json(run_dir / "write-sets" / "rejected" / f"{write_set.get('write_set_id','write-set')}.json", {"write_set": write_set, "result": result})
        return result
    applied: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", ""))
        content = str(item.get("content", ""))
        if not _allowed(path):
            result = {"ok": False, "error": f"blocked path {path}", "applied": applied}
            write_json(run_dir / "write-sets" / "rejected" / f"{write_set.get('write_set_id','write-set')}.json", {"write_set": write_set, "result": result})
            return result
        target = repo_root() / path
        write_text(target, content)
        applied.append(path)
    result = {"ok": True, "gate": gate, "applied": applied, "applied_at": utc_id()}
    write_json(run_dir / "write-sets" / "applied" / f"{write_set.get('write_set_id','write-set')}.json", {"write_set": write_set, "result": result})
    ledger("artifact-ledger.jsonl", {"time": utc_id(), "event": "write_set.applied", "write_set_id": write_set.get("write_set_id"), "files": applied})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a validated LiveHarness write-set.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--write-set", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "write-set-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    write_set_path = Path(args.write_set)
    if not write_set_path.is_absolute():
        write_set_path = harness_root() / write_set_path
    print(json.dumps(apply_write_set(read_json(write_set_path, {}), run_dir), indent=2))


if __name__ == "__main__":
    main()
