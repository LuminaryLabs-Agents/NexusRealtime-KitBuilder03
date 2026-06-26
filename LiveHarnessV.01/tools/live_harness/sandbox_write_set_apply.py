from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, write_text, ledger, utc_id

ALLOWED_PUBLIC_PREFIXES = ["docs/games/"]


def _safe_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("/")
    parts = Path(normalized).parts
    if ".." in parts or normalized.startswith("/"):
        return False
    if normalized.startswith(".github/") or "/.github/" in normalized:
        return False
    if ".env" in parts or "secrets" in normalized.lower():
        return False
    return any(normalized.startswith(prefix) for prefix in ALLOWED_PUBLIC_PREFIXES)


def apply_to_sandbox(write_set: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    sandbox_root = run_dir / "sandbox"
    applied: list[str] = []
    rejected: list[str] = []
    for item in write_set.get("files", []):
        path = str(item.get("path", ""))
        content = str(item.get("content", ""))
        if not _safe_path(path):
            rejected.append(path)
            continue
        target = sandbox_root / path
        write_text(target, content)
        applied.append(str(target.relative_to(run_dir)))
    result = {"ok": not rejected, "sandbox_root": str(sandbox_root), "candidate_id": write_set.get("candidate_id"), "applied": applied, "rejected": rejected, "applied_at": utc_id()}
    write_json(run_dir / "write-sets" / "applied-to-sandbox" / "sandbox-apply-result.json", result)
    ledger("artifact-ledger.jsonl", {"time": utc_id(), "event": "write_set.applied_to_sandbox", "candidate_id": write_set.get("candidate_id"), "files": len(applied), "rejected": rejected})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a reconciled write-set into the run sandbox.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--write-set", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "sandbox-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    write_set_path = Path(args.write_set) if args.write_set else run_dir / "write-sets" / "final-write-set.json"
    if not write_set_path.is_absolute():
        write_set_path = harness_root() / write_set_path
    print(json.dumps(apply_to_sandbox(read_json(write_set_path, {}), run_dir), indent=2))


if __name__ == "__main__":
    main()
