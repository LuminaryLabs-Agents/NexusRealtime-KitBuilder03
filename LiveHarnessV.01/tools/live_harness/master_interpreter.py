from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from .common import harness_root, write_json, write_text, ledger, utc_id
from .product_brief import make_brief, sanitize_public_text


ARCHITECTURE_CONTRACT = {
    "runtime_rule": "Runtime executes deterministic ticks, events, resources, components, systems, surfaces, and sequences.",
    "kit_rule": "Kits and Domain Service Kits own reusable gameplay meaning, validation, commands, events, and durable state.",
    "sequence_rule": "Sequences own authored flow, tutorial order, mission pacing, objective beats, and player-facing orchestration.",
    "renderer_rule": "Renderer and host present state and map input into domain commands; they must not own gameplay truth.",
    "dsk_rule": "No meaningful gameplay interaction should bypass a DSK-shaped command/event boundary."
}

SUCCESS_GATES = [
    "public-output membrane passes",
    "GameHost exposes useful state",
    "major interactions have command/event trace",
    "renderer does not own gameplay truth",
    "JS syntax and HTML smoke checks pass",
    "launcher manifest remains valid",
]

NON_GOALS = [
    "Do not build a dashboard about model providers or private workflow metadata.",
    "Do not expose provider, secret, workflow, or prompt-run control-plane data in public app files.",
    "Do not put all gameplay meaning in renderer, pointer, or keyboard handlers.",
    "Do not advance a stage only because files exist; advance when alignment and gates pass.",
]

DEFAULT_LOOPBACK_POLICY = {
    "public_output_bleed": "10-product-brief",
    "renderer_owns_gameplay": "30-domain-map",
    "missing_debug_host": "40-prototype",
    "missing_domain_trace": "40-prototype",
    "tool_failure": "70-repair",
    "low_score": "60-learning-purge"
}


def _goal_id(title: str, raw_prompt: str) -> str:
    base = sanitize_public_text(title).lower().replace(" ", "-") or "project"
    digest = hashlib.sha256(raw_prompt.encode("utf-8")).hexdigest()[:8]
    return f"{base}-{digest}"


def _primary_verbs(public_goal: str, features: list[str]) -> list[str]:
    text = (public_goal + " " + " ".join(features)).lower()
    verbs: list[str] = []
    for word in ["move", "inspect", "place", "remove", "select", "build", "break", "craft", "collect", "explore", "author", "validate"]:
        if word in text:
            verbs.append(word)
    return verbs or ["inspect", "validate", "iterate"]


def _target_capabilities(public_goal: str, features: list[str]) -> list[str]:
    text = (public_goal + " " + " ".join(features)).lower()
    caps = ["product-brief membrane", "debug-host-state", "top-ten rolling gallery"]
    if "voxel" in text or "block" in text or "minecraft" in text:
        caps += ["voxel host", "build-break-domain-service-kit trace", "inventory-domain-service-kit state", "movement-control-kit state"]
    if "dsk" in text or "domain" in text:
        caps += ["domain bubble contract", "command-event membrane", "idempotency ledger"]
    if "sequence" in text or "gate" in text:
        caps += ["sequence gate workflow", "stage gate transition"]
    return list(dict.fromkeys(caps))


def build_master_interpretation(raw_prompt: str, run_dir: Path, raw_goal_ref: str = "") -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    for child in ["input", "interpretation", "monitor", "turns", "self-alignment", "write-sets/proposed", "write-sets/applied", "write-sets/rejected", "gates"]:
        (run_dir / child).mkdir(parents=True, exist_ok=True)

    brief = make_brief(raw_prompt)
    goal_id = _goal_id(brief.public_title, raw_prompt)
    verbs = _primary_verbs(brief.public_goal, brief.product_features)
    target_capabilities = _target_capabilities(brief.public_goal, brief.product_features)
    master = {
        "schema": "liveharness.master-interpretation.v1",
        "goal_id": goal_id,
        "goal_version": 1,
        "raw_goal_ref": raw_goal_ref,
        "canonical_goal": brief.public_goal,
        "public_product_intent": {
            "title": brief.public_title,
            "player_or_user_goal": brief.public_goal,
            "primary_verbs": verbs,
            "target_artifact": "playable browser experiment or designer-facing kit tool"
        },
        "private_harness_intent": {
            "preserve_run_logs": True,
            "run_deterministic_tools": True,
            "commit_artifacts": True,
            "update_capability_memory": True,
            "purge_to_top_ten": True
        },
        "architecture_contract": ARCHITECTURE_CONTRACT,
        "success_gates": SUCCESS_GATES,
        "non_goals": NON_GOALS,
        "target_capabilities": target_capabilities,
        "loopback_policy": DEFAULT_LOOPBACK_POLICY,
        "product_brief": brief.to_dict(),
        "locked_at": utc_id()
    }

    critique = {
        "schema": "liveharness.interpretation-critique.v1",
        "goal_id": goal_id,
        "checks": [
            {"id": "product-plane-separated", "ok": True, "summary": "Public product intent is separated from private harness notes."},
            {"id": "architecture-contract-present", "ok": True, "summary": "Runtime/Kits/Sequences/Renderer/DSK rules are explicit."},
            {"id": "anti-drift-present", "ok": True, "summary": "Non-goals block public control-plane metadata and renderer-owned gameplay."},
            {"id": "gate-policy-present", "ok": True, "summary": "Success gates and loopbacks are defined before output is advanced."}
        ],
        "decision": "lock_after_reconcile"
    }

    reconcile = {
        "schema": "liveharness.interpretation-reconcile.v1",
        "goal_id": goal_id,
        "summary": "Locked the master interpretation for this run. All turn actions must reference this interpretation version.",
        "locked_interpretation_ref": "input/master-interpretation.json"
    }

    goal_ast = {
        "schema": "liveharness.goal-ast.v1",
        "goal_id": goal_id,
        "root": {"id": "goal", "type": "MASTER_GOAL", "text": brief.public_goal},
        "children": [
            {
                "id": "product",
                "type": "PRODUCT_PLANE",
                "children": [
                    {"id": "user_experience", "type": "USER_EXPERIENCE", "must": brief.product_features or [brief.public_goal]},
                    {"id": "architecture", "type": "NEXUS_ARCHITECTURE", "must": list(ARCHITECTURE_CONTRACT.values())}
                ]
            },
            {
                "id": "harness",
                "type": "HARNESS_PLANE",
                "children": [
                    {"id": "logs", "type": "OBSERVABILITY", "must": ["write run logs", "write tool results", "write self-alignment turns"]},
                    {"id": "learning", "type": "FAIL_FORWARD", "must": ["score output", "capsule weak builds", "update capability memory", "keep gallery capped"]}
                ]
            },
            {"id": "anti_goals", "type": "FORBIDDEN_DRIFT", "must_not": NON_GOALS}
        ]
    }

    write_json(run_dir / "interpretation" / "001-interpret-goal.json", master)
    write_json(run_dir / "interpretation" / "002-critique-interpretation.json", critique)
    write_json(run_dir / "interpretation" / "003-reconcile-interpretation.json", reconcile)
    write_json(run_dir / "interpretation" / "locked-master-interpretation.json", master)
    write_json(run_dir / "input" / "master-interpretation.json", master)
    write_json(run_dir / "input" / "goal-ast.json", goal_ast)
    write_json(run_dir / "input" / "product-brief.json", brief.to_dict())
    write_text(run_dir / "monitor" / "active-plan.md", "# Active Plan\n\n1. Interpret and lock the goal.\n2. Generate or revise one bounded prototype artifact.\n3. Self-align against gates before advancement.\n")
    write_json(run_dir / "monitor" / "think-list.json", {"version": 1, "items": []})
    write_text(run_dir / "monitor" / "monitor-log.md", "# Monitor Log\n\n- Master interpretation locked.\n")
    ledger("alignment-ledger.jsonl", {"time": utc_id(), "event": "master_interpretation.locked", "goal_id": goal_id, "run_dir": str(run_dir)})
    return {"master": master, "goal_ast": goal_ast, "brief": brief.to_dict()}


def main() -> None:
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Create a LiveHarness master interpretation and goal AST.")
    parser.add_argument("--run-dir", default=os.environ.get("LIVEHARNESS_RUN_DIR", ""))
    parser.add_argument("--prompt-file", default="")
    args = parser.parse_args()
    harness = harness_root()
    run_dir = Path(args.run_dir) if args.run_dir else harness / "runs" / (os.environ.get("LIVEHARNESS_RUN_ID") or utc_id())
    if not run_dir.is_absolute():
        run_dir = harness / run_dir
    raw = os.environ.get("GAME_PROMPT", "")
    raw_ref = "env:GAME_PROMPT"
    if args.prompt_file:
        p = Path(args.prompt_file)
        if p.exists():
            raw = p.read_text(encoding="utf-8", errors="replace")
            raw_ref = str(p)
    if not raw:
        prompt_doc = run_dir / "input" / "prompt.md"
        raw = prompt_doc.read_text(encoding="utf-8", errors="replace") if prompt_doc.exists() else ""
        raw_ref = str(prompt_doc)
    print(json.dumps(build_master_interpretation(raw, run_dir, raw_ref)["master"], indent=2))


if __name__ == "__main__":
    main()
