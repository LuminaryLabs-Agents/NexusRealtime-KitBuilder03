from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, write_text, ledger, utc_id
from .repo_import_resolver import build_import_map, resolve_import
from .kit_registry_builder import build_kit_registry

REFERENCE_PRIORITY = [
    "nexusrealtime.domain-service-kit",
    "nexusrealtime.sequence-node",
    "nexusrealtime.procedural-world",
    "protokit.world-terrain-pattern",
    "protokit.render-descriptor-pattern",
    "protokit.action-input-kit",
]


def _load_capsules(run_dir: Path) -> list[dict[str, Any]]:
    capsules: list[dict[str, Any]] = []
    for cap_file in sorted((run_dir / "intake").glob("*/capability-capsules.json")):
        data = read_json(cap_file, {"capsules": []})
        for cap in data.get("capsules", []):
            if isinstance(cap, dict):
                capsules.append(cap)
    return capsules


def fuse(run_dir: Path) -> dict[str, Any]:
    fused_dir = run_dir / "intake" / "fused"
    fused_dir.mkdir(parents=True, exist_ok=True)
    capsules = _load_capsules(run_dir)
    by_id: dict[str, dict[str, Any]] = {}
    for cap in capsules:
        cap_id = str(cap.get("capability_id", "unknown"))
        existing = by_id.get(cap_id)
        if not existing or float(cap.get("confidence", 0)) > float(existing.get("confidence", 0)):
            by_id[cap_id] = cap
    capabilities = list(by_id.values())
    selected = []
    for cap_id in REFERENCE_PRIORITY:
        if cap_id in by_id:
            cap = by_id[cap_id]
            resolved = resolve_import(cap)
            selected.append({**cap, "resolved_import": resolved})
    import_map = build_import_map(selected)
    reference_patterns = [cap.get("capability_id") for cap in selected if cap.get("classification") in {"reference_pattern", "validation_source"}]
    runtime_dependencies = [cap.get("capability_id") for cap in selected if cap.get("resolved_import", {}).get("safe_to_import")]
    validation_rules = [
        "renderer must consume descriptors/state and not own gameplay state",
        "input adapter should route platform input into domain command requests",
        "world patch or chunk lifecycle should be separate from renderer mesh construction",
        "domain actions must expose command identifiers and event traces",
        "Sequence or objective flow should be represented as data and events"
    ]
    kit_registry = build_kit_registry(run_dir)
    integration = {
        "schema": "liveharness.integration-plan.v1",
        "mode": "reference-plus-local-fallback",
        "runtime_dependencies": runtime_dependencies,
        "reference_patterns": reference_patterns,
        "local_fallbacks": ["src/world/chunkStore.js", "src/host/inputAdapter.js", "src/domains/buildBreakDomain.js"],
        "import_map": import_map.get("imports", {}),
        "kit_registry_ref": "intake/fused/kit-registry.json",
        "adapter_contracts_ref": "intake/fused/adapter-contracts.json",
        "proof_tasks_ref": "intake/fused/proof-tasks.json",
        "kit_count": len(kit_registry.get("kits", [])),
        "validation_rules": validation_rules,
        "trusted_as_instruction": False,
        "created_at": utc_id()
    }
    capability_map = {"schema": "liveharness.fused-capability-map.v1", "capabilities": capabilities, "selected": selected, "kit_registry_ref": "intake/fused/kit-registry.json", "updated_at": utc_id()}
    write_json(fused_dir / "fused-capability-map.json", capability_map)
    write_json(fused_dir / "selected-kits.json", {"selected": selected})
    write_json(fused_dir / "integration-plan.json", integration)
    write_json(fused_dir / "import-map.json", import_map)
    write_json(fused_dir / "validation-rules.json", {"rules": validation_rules})
    write_json(fused_dir / "reference-pack.json", {"references": selected})
    write_json(fused_dir / "build-constraints.json", {"constraints": validation_rules, "trusted_as_instruction": False})
    write_text(fused_dir / "reference-pack.md", "# Fused Repo Capability Pack\n\n" + "\n".join(f"- {cap.get('capability_id')}: {cap.get('summary')}" for cap in selected) + "\n")
    write_json(harness_root() / "state" / "repo-capability-index.json", {"version": 1, "updated_at": utc_id(), "capabilities": capabilities})
    ledger("context-ledger.jsonl", {"time": utc_id(), "event": "intake.fused", "capabilities": len(capabilities), "selected": len(selected), "kits": len(kit_registry.get("kits", []))})
    return integration


def main() -> None:
    parser = argparse.ArgumentParser(description="Fuse source intake reports into a build-ready capability map.")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "intake-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(fuse(run_dir), indent=2))


if __name__ == "__main__":
    main()
