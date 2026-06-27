from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from .common import harness_root, write_json, utc_id
from .game_spec_harness import build_specs
from .massive_build_loop_v3 import run_massive_build


def run_batch(run_dir: Path, theme_file: str = "", count: int = 10, max_workers: int = 16, max_loops: int = 2, max_parallel: int = 16) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_specs(run_dir, theme_file, count)
    results = []
    for index, spec in enumerate(manifest["specs"], start=1):
        prompt_path = run_dir / spec["prompt_file"]
        prompt = prompt_path.read_text(encoding="utf-8", errors="replace")
        child_id = f"{run_dir.name}-game-{index:02d}-{spec['spec_id']}"
        child_dir = run_dir / "children" / child_id
        status = run_massive_build(child_id, child_dir, prompt, str(prompt_path.relative_to(run_dir)), max_workers, max_loops, max_parallel)
        results.append({"spec_id": spec["spec_id"], "title": spec["title"], "run_id": child_id, "status": status})
    batch_status = {"schema": "liveharness.ten-game-batch-status.v1", "run_id": run_dir.name, "count": len(results), "results": results, "completed_at": utc_id()}
    write_json(run_dir / "ten-game-batch-status.json", batch_status)
    return batch_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ten GameSpec variants through LiveHarness.")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--theme-file", default="")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--max-workers", type=int, default=16)
    parser.add_argument("--max-loops", type=int, default=2)
    parser.add_argument("--max-parallel", type=int, default=16)
    args = parser.parse_args()
    run_id = args.run_id or utc_id() + "-ten-game-batch"
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / run_id
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(run_batch(run_dir, args.theme_file, args.count, args.max_workers, args.max_loops, args.max_parallel), indent=2))


if __name__ == "__main__":
    main()
