from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import os

from .common import harness_root, read_json, write_json, utc_id

DEFAULTS = {
    "low": {"game_count": 3, "expansion_turns": 1, "reconciliation_passes": 1, "goal_alignment_rounds": 1, "build_loops": 1, "max_workers": 8, "max_parallel": 8},
    "standard": {"game_count": 10, "expansion_turns": 2, "reconciliation_passes": 2, "goal_alignment_rounds": 2, "build_loops": 2, "max_workers": 16, "max_parallel": 16},
    "high": {"game_count": 10, "expansion_turns": 3, "reconciliation_passes": 3, "goal_alignment_rounds": 3, "build_loops": 3, "max_workers": 20, "max_parallel": 16},
    "deep": {"game_count": 10, "expansion_turns": 4, "reconciliation_passes": 4, "goal_alignment_rounds": 4, "build_loops": 4, "max_workers": 24, "max_parallel": 16},
    "extreme": {"game_count": 10, "expansion_turns": 6, "reconciliation_passes": 6, "goal_alignment_rounds": 6, "build_loops": 6, "max_workers": 32, "max_parallel": 16}
}


def load_profiles() -> dict[str, Any]:
    path = harness_root() / "state" / "power-profiles.json"
    data = read_json(path, {"default_profile": "standard", "profiles": DEFAULTS})
    profiles = data.get("profiles") if isinstance(data.get("profiles"), dict) else DEFAULTS
    return {"default_profile": data.get("default_profile", "standard"), "profiles": profiles}


def resolve_power(profile_name: str = "", overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    data = load_profiles()
    name = profile_name or os.environ.get("LIVEHARNESS_POWER") or str(data.get("default_profile") or "standard")
    profiles = data["profiles"]
    if name not in profiles:
        name = "standard"
    plan = dict(profiles[name])
    plan["profile"] = name
    for key, value in (overrides or {}).items():
        if value is not None and value != "":
            try:
                plan[key] = int(value)
            except (TypeError, ValueError):
                plan[key] = value
    plan["schema"] = "liveharness.power-plan.v1"
    plan["created_at"] = utc_id()
    return plan


def write_power_plan(run_dir: Path, profile_name: str = "", overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = resolve_power(profile_name, overrides)
    write_json(run_dir / "power-plan.json", plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve LiveHarness build power profile.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--profile", default="")
    parser.add_argument("--count", default="")
    parser.add_argument("--max-loops", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / (utc_id() + "-power-plan")
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    print(json.dumps(write_power_plan(run_dir, args.profile, {"game_count": args.count, "build_loops": args.max_loops}), indent=2))


if __name__ == "__main__":
    main()
