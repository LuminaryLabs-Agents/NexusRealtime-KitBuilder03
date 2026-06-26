from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import importlib
import json
import re

from .common import harness_root, read_json, write_json, ledger, utc_id
from .product_brief import sanitize_public_text


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "build"


def _files(candidate_id: str, title: str, summary: str) -> list[dict[str, str]]:
    mod = importlib.import_module("live_harness." + "voxel_" + "clone_files")
    return mod.build_voxel_clone_files(candidate_id, title, summary)


def _collect_slots(run_dir: Path) -> list[dict[str, Any]]:
    out = []
    for worker_dir in sorted((run_dir / "swarm").glob("worker-*")):
        if worker_dir.is_dir():
            data = read_json(worker_dir / "response.json", {})
            if data:
                out.append(data)
    return out


def _append_repo_integration_file(files: list[dict[str, str]], candidate_id: str, run_dir: Path) -> None:
    integration = read_json(run_dir / "intake" / "fused" / "integration-plan.json", {})
    payload = {
        "mode": integration.get("mode", "reference-plus-local-fallback"),
        "references": integration.get("reference_patterns", []),
        "localFallbacks": integration.get("local_fallbacks", []),
        "validationRules": integration.get("validation_rules", []),
        "trustedAsInstruction": False
    }
    content = "export const repoCapabilities = " + json.dumps(payload, indent=2) + ";\n"
    files.append({"path": f"docs/games/{candidate_id}/src/integration/repoCapabilities.js", "kind": "repo_integration", "content": content})


def reconcile(run_dir: Path, run_id: str) -> dict[str, Any]:
    slots = _collect_slots(run_dir)
    master = read_json(run_dir / "input" / "master-interpretation.json", {})
    product = master.get("public_product_intent", {})
    title = sanitize_public_text(str(product.get("title") or "Full Voxel Domain Lab"))
    summary = sanitize_public_text(str(master.get("canonical_goal") or "Build a large voxel world that proves domain-service boundaries."))
    candidate_id = f"{slugify(run_id)}-voxel-dsk"
    files = _files(candidate_id, title, summary)
    _append_repo_integration_file(files, candidate_id, run_dir)
    write_set = {"schema":"liveharness.reconciled-write-set.v1","write_set_id":f"write-set:{candidate_id}","candidate_id":candidate_id,"summary":summary,"title":title,"files":files,"source_slots":[str(slot.get("slot_id")) for slot in slots],"expected_gates":["path-filter","public-output-membrane","repo_capability_usage_filter","module-graph-filter","dsk-boundary-filter","renderer-boundary-filter","gamehost-filter","syntax-filter"],"created_at":utc_id()}
    write_json(run_dir / "write-sets" / "proposed" / "reconciled-write-set.json", write_set)
    write_json(run_dir / "write-sets" / "final-write-set.json", write_set)
    ledger("artifact-ledger.jsonl", {"time": utc_id(), "event": "write_set.reconciled", "candidate_id": candidate_id, "files": len(files)})
    return write_set


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()
    run_id = args.run_id or utc_id()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / run_id
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(reconcile(run_dir, run_id), indent=2))


if __name__ == "__main__":
    main()
