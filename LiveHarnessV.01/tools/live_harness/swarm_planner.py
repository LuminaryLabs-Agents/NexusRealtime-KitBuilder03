from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, read_json, write_json, ledger, utc_id
from .master_interpreter import build_master_interpretation

WORKER_SPECS = [
    ("01", "product-brief", "Product Brief Worker", "Refine public title, goal, feature list, and non-goals."),
    ("02", "runtime-contract", "Runtime Contract Worker", "Define tick loop, command queue, event bus, snapshot, and state contract."),
    ("03", "domain-map", "DSK Boundary Worker", "Define domain bubbles, commands, events, owned state, invariants, and should-not-own rules."),
    ("04", "world-data", "World Data Worker", "Define terrain, chunks, blocks, biomes, and level descriptors."),
    ("05", "three-renderer", "Three.js Renderer Worker", "Define Three.js scene, chunk meshes, materials, camera, and renderer boundary."),
    ("06", "movement", "Movement Worker", "Define movement state, input intent, movement events, and camera relation."),
    ("07", "build-break-dsk", "Build/Break DSK Worker", "Define build.place.request and block.break.request command/event flow."),
    ("08", "inventory-dsk", "Inventory DSK Worker", "Define block palette, selected block, inventory state, and transaction ledger."),
    ("09", "sequence-objective", "Sequence Worker", "Define objective flow, tutorial beats, gates, and progression state."),
    ("10", "ui-hud", "UI/HUD Worker", "Define concise HUD, status, controls, and public copy."),
    ("11", "debug-host", "Debug Host Worker", "Define window.GameHost.getState() and snapshot/debug surfaces."),
    ("12", "tests", "Tool/Test Worker", "Define smoke tests, syntax checks, and GameHost/domain trace expectations."),
    ("13", "performance", "Performance Worker", "Define file count, instancing, chunk budget, and draw budget."),
    ("14", "content-polish", "Content Polish Worker", "Define names, theme, readable copy, biome and feedback polish."),
    ("15", "self-alignment-review", "Self-Alignment Worker", "Review output against master interpretation and gate policy."),
    ("16", "repair-strategy", "Repair Worker", "Route failures to the right loopback target and repair slot."),
]

MUST_RETURN = {
    "summary": "string",
    "provides": ["string"],
    "requires": ["string"],
    "owned_state": ["string"],
    "commands": ["string"],
    "events": ["string"],
    "invariants": ["string"],
    "file_plan": [{"path": "string", "purpose": "string"}],
    "risks": ["string"],
}


def _load_prompt(run_dir: Path) -> str:
    prompt_doc = run_dir / "input" / "prompt.md"
    return prompt_doc.read_text(encoding="utf-8", errors="replace") if prompt_doc.exists() else ""


def plan_swarm(run_dir: Path, run_id: str, max_workers: int = 16, loop_index: int = 1) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_prompt = _load_prompt(run_dir)
    master_path = run_dir / "input" / "master-interpretation.json"
    if master_path.exists():
        master = read_json(master_path, {})
    else:
        master = build_master_interpretation(raw_prompt, run_dir, str(run_dir / "input" / "prompt.md"))["master"]
    workers: list[dict[str, Any]] = []
    specs = WORKER_SPECS[:max_workers]
    for number, slot, label, task in specs:
        worker_id = f"worker-{number}-{slot}"
        contract = {
            "schema": "liveharness.worker-contract.v1",
            "worker_id": worker_id,
            "slot_id": slot,
            "label": label,
            "critical": slot in {"runtime-contract", "domain-map", "three-renderer", "build-break-dsk", "debug-host", "tests"},
            "goal_ref": "input/master-interpretation.json",
            "goal_ast_node": "product.architecture" if slot not in {"product-brief", "ui-hud"} else "product.user_experience",
            "task": task,
            "input_context": {
                "canonical_goal": master.get("canonical_goal"),
                "public_product_intent": master.get("public_product_intent", {}),
                "architecture_contract": master.get("architecture_contract", {}),
                "target_capabilities": master.get("target_capabilities", []),
                "loop_index": loop_index,
            },
            "must_return": MUST_RETURN,
        }
        worker_dir = run_dir / "swarm" / worker_id
        write_json(worker_dir / "request.json", contract)
        workers.append(contract)
    plan = {
        "schema": "liveharness.swarm-plan.v1",
        "run_id": run_id,
        "loop_index": loop_index,
        "created_at": utc_id(),
        "max_workers": len(workers),
        "workers": workers,
        "policy_ref": "state/swarm-policy.json",
    }
    write_json(run_dir / "swarm" / "swarm-plan.json", plan)
    ledger("build-ledger.jsonl", {"time": utc_id(), "event": "swarm.plan.created", "run_id": run_id, "workers": len(workers), "loop_index": loop_index})
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a LiveHarness massive-build swarm plan.")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--loop-index", type=int, default=1)
    args = parser.parse_args()
    run_id = args.run_id or utc_id()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / run_id
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(plan_swarm(run_dir, run_id, args.workers, args.loop_index), indent=2))


if __name__ == "__main__":
    main()
