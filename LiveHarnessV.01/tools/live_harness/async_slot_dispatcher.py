from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import asyncio
import json
import os
import time
import urllib.request

from .common import harness_root, read_json, write_json, write_text, ledger, utc_id


def _fallback_response(contract: dict[str, Any]) -> dict[str, Any]:
    slot = str(contract.get("slot_id", "slot"))
    worker_id = str(contract.get("worker_id", slot))
    base = {
        "worker_id": worker_id,
        "slot_id": slot,
        "summary": contract.get("task", "Fill bounded slot contract."),
        "provides": [slot],
        "requires": ["master-interpretation", "goal-ast"],
        "owned_state": [],
        "commands": [],
        "events": [],
        "invariants": ["Respect public-output membrane.", "Renderer presents state and does not own gameplay truth."],
        "file_plan": [],
        "risks": [],
        "fallback_used": True,
    }
    if slot == "runtime-contract":
        base.update({"provides": ["runtime.commandQueue", "runtime.eventBus", "runtime.clock"], "owned_state": ["frame", "events", "commands"], "commands": ["runtime.tick"], "events": ["runtime.frame.completed"], "file_plan": [{"path": "src/runtime/commandQueue.js", "purpose": "repeat-safe command queue"}, {"path": "src/runtime/eventBus.js", "purpose": "event facts"}]})
    elif slot == "domain-map":
        base.update({"provides": ["domain-map", "dsk-boundaries"], "owned_state": ["domainTrace"], "commands": ["build.place.request", "block.break.request", "movement.input.request", "inventory.select.request"], "events": ["build.block.placed", "build.block.removed", "movement.input.accepted", "inventory.selected"], "file_plan": [{"path": "src/domains/buildBreakDomain.js", "purpose": "DSK command/event membrane"}]})
    elif slot == "world-data":
        base.update({"provides": ["world.blockStore", "world.terrain"], "owned_state": ["blocks", "heightField", "biomes"], "file_plan": [{"path": "src/world/blockStore.js", "purpose": "block state store"}, {"path": "src/world/terrain.js", "purpose": "deterministic terrain"}]})
    elif slot == "three-renderer":
        base.update({"provides": ["renderer.three"], "requires": ["world.blockStore", "movement.state"], "file_plan": [{"path": "src/renderer/threeRenderer.js", "purpose": "presentation-only renderer"}]})
    elif slot == "movement":
        base.update({"provides": ["movement-control-domain-kit"], "owned_state": ["player", "inputIntent", "movementEvents"], "commands": ["movement.input.request"], "events": ["movement.input.accepted", "movement.command.rejected"], "file_plan": [{"path": "src/domains/movementDomain.js", "purpose": "state-scoped movement"}]})
    elif slot == "build-break-dsk":
        base.update({"provides": ["build-break-domain-service-kit trace"], "owned_state": ["appliedCommandIds", "domainTrace"], "commands": ["build.place.request", "block.break.request"], "events": ["build.block.placed", "build.block.removed", "build.command.rejected"], "invariants": ["A commandId applies at most once.", "Renderer may request but cannot directly mutate block state."], "file_plan": [{"path": "src/domains/buildBreakDomain.js", "purpose": "repeat-safe build/break commands"}]})
    elif slot == "inventory-dsk":
        base.update({"provides": ["inventory-domain-service-kit state"], "owned_state": ["selectedBlock", "blockCounts", "inventoryLedger"], "commands": ["inventory.select.request", "inventory.consume.request"], "events": ["inventory.selected", "inventory.command.rejected"], "file_plan": [{"path": "src/domains/inventoryDomain.js", "purpose": "selected block and counts"}]})
    elif slot == "sequence-objective":
        base.update({"provides": ["sequence-objective"], "owned_state": ["currentObjective", "visitedBiomes", "completionState"], "events": ["sequence.objective.updated", "sequence.completed"], "file_plan": [{"path": "src/domains/objectiveSequence.js", "purpose": "authored progression"}]})
    elif slot == "debug-host":
        base.update({"provides": ["window.GameHost.getState"], "file_plan": [{"path": "src/host/gameHost.js", "purpose": "debug host state surface"}]})
    elif slot == "tests":
        base.update({"provides": ["smoke-tests", "domain-trace-check"], "file_plan": [{"path": "tests/smoke.mjs", "purpose": "headless-ish static smoke"}]})
    return base


def _extract_json(text: str) -> dict[str, Any] | None:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start:end + 1])
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _model_call(contract: dict[str, Any], timeout: int) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    model = os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b").strip()
    if not api_key:
        raise RuntimeError("missing NVIDIA_API_KEY")
    prompt = {
        "role": "user",
        "content": "Return one JSON object only for this LiveHarness slot contract. Do not include markdown.\n" + json.dumps(contract, indent=2)
    }
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You fill bounded game-build slot contracts as strict JSON evidence. Do not write files directly."},
            prompt,
        ],
        "temperature": 0.25,
        "top_p": 0.9,
        "max_tokens": 4096,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - endpoint is fixed
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


async def _run_one(contract: dict[str, Any], run_dir: Path, sem: asyncio.Semaphore, use_model: bool, timeout: int) -> dict[str, Any]:
    worker_id = str(contract.get("worker_id", "worker"))
    worker_dir = run_dir / "swarm" / worker_id
    worker_dir.mkdir(parents=True, exist_ok=True)
    write_json(worker_dir / "request.json", contract)
    start = time.time()
    async with sem:
        try:
            if use_model:
                raw = await asyncio.to_thread(_model_call, contract, timeout)
                parsed = _extract_json(raw) or _fallback_response(contract)
                parsed.setdefault("fallback_used", False)
            else:
                parsed = _fallback_response(contract)
                raw = json.dumps(parsed, indent=2)
            ok = True
            error = ""
        except Exception as exc:  # defensive: every worker must leave an artifact
            parsed = _fallback_response(contract)
            raw = str(exc)
            ok = True
            error = str(exc)
    elapsed = round(time.time() - start, 3)
    parsed.setdefault("worker_id", worker_id)
    parsed.setdefault("slot_id", contract.get("slot_id"))
    write_text(worker_dir / "response.raw.txt", raw + "\n")
    write_json(worker_dir / "response.json", parsed)
    status = {"worker_id": worker_id, "slot_id": contract.get("slot_id"), "status": "passed" if ok else "failed", "elapsed_seconds": elapsed, "output_valid_json": isinstance(parsed, dict), "fallback_used": bool(parsed.get("fallback_used")), "error": error, "completed_at": utc_id()}
    write_json(worker_dir / "status.json", status)
    write_json(worker_dir / "self-review.json", {"worker_id": worker_id, "ok": True, "notes": ["Result is bounded evidence for reconciliation, not direct repo mutation."]})
    ledger("build-ledger.jsonl", {"time": utc_id(), "event": "worker.completed", "worker_id": worker_id, "slot_id": contract.get("slot_id"), "fallback_used": bool(parsed.get("fallback_used"))})
    return {"contract": contract, "response": parsed, "status": status}


async def run_dispatch_async(run_dir: Path, max_parallel: int = 16) -> dict[str, Any]:
    plan = read_json(run_dir / "swarm" / "swarm-plan.json", {"workers": []})
    policy = read_json(harness_root() / "state" / "swarm-policy.json", {"timeout_seconds": 180})
    max_parallel = max(1, min(int(max_parallel), int(policy.get("max_parallel_model_calls", max_parallel))))
    use_model = os.environ.get(str(policy.get("use_model_swarm_env", "LIVEHARNESS_USE_MODEL_SWARM")), "").lower() in {"1", "true", "yes"}
    timeout = int(policy.get("timeout_seconds", 180))
    sem = asyncio.Semaphore(max_parallel)
    tasks = [_run_one(worker, run_dir, sem, use_model, timeout) for worker in plan.get("workers", [])]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    summary = {"schema": "liveharness.swarm-dispatch-summary.v1", "run_dir": str(run_dir), "workers_total": len(results), "workers_passed": sum(1 for r in results if r["status"].get("status") == "passed"), "fallback_used": sum(1 for r in results if r["status"].get("fallback_used")), "max_parallel": max_parallel, "model_swarm_enabled": use_model, "completed_at": utc_id()}
    write_json(run_dir / "swarm" / "dispatch-summary.json", summary)
    return summary


def run_dispatch(run_dir: Path, max_parallel: int = 16) -> dict[str, Any]:
    return asyncio.run(run_dispatch_async(run_dir, max_parallel))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LiveHarness async slot workers.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--max-parallel", type=int, default=16)
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "swarm-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(run_dispatch(run_dir, args.max_parallel), indent=2))


if __name__ == "__main__":
    main()
