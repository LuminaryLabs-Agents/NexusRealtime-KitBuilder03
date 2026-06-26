from __future__ import annotations

import argparse
from pathlib import Path

from .common import harness_root, utc_id
from .repo_context import collect
from .context_injector import inject_from_run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--prompt", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / utc_id()
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    collect(run_dir, args.prompt)
    inject_from_run(run_dir)


if __name__ == "__main__":
    main()
