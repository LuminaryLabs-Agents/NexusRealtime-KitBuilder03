from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import re

from .common import harness_root, read_json, write_json, ledger, utc_id
from .product_brief import sanitize_public_text
from .voxel_composition_files_v4 import build_voxel_composition_files


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "build"


def _collect_slots(run_dir: Path) -> list[dict[str, Any]]:
    out = []
    for worker_dir in sorted((run_dir / "swarm").glob("worker-*")):
        if worker_dir.is_dir():
            data = read_json(worker_dir / "response.json", {})
            if data:
                out.append(data)
    return out


def _write_kit_resolution(run_dir: Path) -> None:
    out = run_dir / "kit-resolution"
    out.mkdir(parents=True, exist_ok=True)
    required = [
        {"id": "runtime", "preferred": "nexusrealtime.createRealtimeGame", "fallback": "src/runtime/localRuntime.js"},
        {"id": "input", "preferred": "protokit.action-input-kit", "fallback": "src/host/inputAdapter.js"},
        {"id": "world-loader", "preferred": "protokit.world-patch-kit", "fallback": "src/world/worldLoader.js"},
        {"id": "terrain", "preferred": "protokit.terrain-sampler-kit", "fallback": "src/world/chunkStore.js"},
        {"id": "domain-service", "preferred": "nexusrealtime.domain-service-kit", "fallback": "src/domains/buildBreakDomain.js"}
    ]
    plan = {"schema": "liveharness.kit-resolution-plan.v1", "mode": "import-map-with-local-fallback", "composition_order": ["nexusrealtime.core", "protokit.action-input-kit", "protokit.world-patch-kit", "protokit.terrain-sampler-kit", "local.fallbacks"], "required_capabilities": required, "fallbacks_required": True, "rules": ["html remains bounded shell", "prefer module import when safe", "fallbacks must be present", "renderer consumes state only"], "created_at": utc_id()}
    write_json(out / "kit-resolution-plan.json", plan)
    write_json(out / "selected-runtime-imports.json", {"schema": "liveharness.selected-runtime-imports.v1", "imports": {"@nexus/core": "approved", "@protokits/action-input": "approved", "three": "approved"}})
    write_json(out / "selected-protokits.json", {"schema": "liveharness.selected-protokits.v1", "items": required[1:4]})
    write_json(out / "fallback-plan.json", {"schema": "liveharness.fallback-plan.v1", "fallbacks": {item["id"]: item["fallback"] for item in required}})
    write_json(out / "composition-tree.json", {"schema": "liveharness.composition-tree.v1", "root": "src/boot.js", "children": required})
    write_json(out / "kit-resolution-report.json", {"schema": "liveharness.kit-resolution-report.v1", "ok": True, "mode": "import-map-with-local-fallback", "completed_at": utc_id()})


def _append_repo_integration_file(files: list[dict[str, str]], candidate_id: str, run_dir: Path) -> None:
    integration = read_json(run_dir / "intake" / "fused" / "integration-plan.json", {})
    payload = {"mode": "import-map-with-local-fallback", "references": integration.get("reference_patterns", []), "localFallbacks": integration.get("local_fallbacks", []), "validationRules": integration.get("validation_rules", []), "trustedAsInstruction": False}
    files.append({"path": f"docs/games/{candidate_id}/src/integration/repoCapabilities.js", "kind": "repo_integration", "content": "export const repoCapabilities = " + json.dumps(payload, indent=2) + ";\n"})


def reconcile(run_dir: Path, run_id: str) -> dict[str, Any]:
    _write_kit_resolution(run_dir)
    slots = _collect_slots(run_dir)
    master = read_json(run_dir / "input" / "master-interpretation.json", {})
    product = master.get("public_product_intent", {})
    title = sanitize_public_text(str(product.get("title") or "Composition Host Voxel Lab"))
    summary = sanitize_public_text(str(master.get("canonical_goal") or "Build a composition-first voxel world that proves kit resolution and local fallbacks."))
    candidate_id = f"{slugify(run_id)}-voxel-dsk"
    files = build_voxel_composition_files(candidate_id, title, summary)
    _append_repo_integration_file(files, candidate_id, run_dir)
    write_set = {"schema": "liveharness.reconciled-write-set.v1", "write_set_id": f"write-set:{candidate_id}", "candidate_id": candidate_id, "summary": summary, "title": title, "files": files, "source_slots": [str(slot.get("slot_id")) for slot in slots], "expected_gates": ["thin_html_filter", "import_map_filter", "kit_resolution_filter", "fallback_compatibility_filter", "repo_capability_usage_filter", "module-graph-filter", "dsk-boundary-filter", "renderer-boundary-filter", "gamehost-filter", "syntax-filter"], "created_at": utc_id()}
    write_json(run_dir / "write-sets" / "proposed" / "reconciled-write-set.json", write_set)
    write_json(run_dir / "write-sets" / "final-write-set.json", write_set)
    ledger("artifact-ledger.jsonl", {"time": utc_id(), "event": "write_set.reconciled", "candidate_id": candidate_id, "files": len(files), "version": "v4-composition"})
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
