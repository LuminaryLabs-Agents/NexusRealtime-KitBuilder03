from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import re

from .common import harness_root, repo_root, write_json, write_text, utc_id


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "idea"


def latest_idea_file(ideas_dir: Path) -> Path | None:
    files = sorted([p for p in ideas_dir.glob("*.md") if p.is_file() and not p.name.lower().startswith("readme")])
    return files[-1] if files else None


def normalize_idea(run_dir: Path, idea_file: str = "") -> dict[str, Any]:
    ideas_dir = repo_root() / "LiveHarnessV.01" / "game-ideas"
    if idea_file:
        source = Path(idea_file)
        if not source.is_absolute():
            source = repo_root() / source
    else:
        source = latest_idea_file(ideas_dir)
    if source is None or not source.exists():
        raise FileNotFoundError("No game idea file found in LiveHarnessV.01/game-ideas")

    text = source.read_text(encoding="utf-8", errors="replace").strip()
    title = source.stem
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip().replace("Idea:", "").strip() or title
            break
    idea_id = slug(source.stem)
    out_dir = run_dir / "idea-intake"
    theme_dir = run_dir / "theme-prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    theme_dir.mkdir(parents=True, exist_ok=True)
    normalized = f"""# Theme Prompt — {title}

Source idea: `{source.relative_to(repo_root())}`

{text}

## Required Harness Output

Generate 10 distinct playable browser game variants from this idea.

Every variant must include:

- a distinct title, mechanic, and world shape
- procedural world or level generation
- RPC-style command routing for important player actions
- clear command IDs and domain trace/debug state
- inventory/tool selection when appropriate
- GameHost.getState() with player, world/level state, input, events, domain/RPC trace, and renderer diagnostics
- kit-aware integration diagnostics where possible
- enough variation that the variants are not simple reskins
"""
    theme_path = theme_dir / f"{idea_id}-theme.md"
    write_text(theme_path, normalized)
    record = {
        "schema": "liveharness.idea-intake.v1",
        "idea_id": idea_id,
        "title": title,
        "source_file": str(source.relative_to(repo_root())),
        "theme_file": str(theme_path.relative_to(run_dir)),
        "created_at": utc_id()
    }
    write_json(out_dir / "idea-intake.json", record)
    write_text(out_dir / "idea-intake.md", f"# Idea Intake\n\n- Idea: {title}\n- Source: `{record['source_file']}`\n- Theme: `{record['theme_file']}`\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize the newest game idea into a GameSpec theme prompt.")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--idea-file", default="")
    args = parser.parse_args()
    run_id = utc_id() + "-idea-intake"
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / run_id
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(normalize_idea(run_dir, args.idea_file), indent=2))


if __name__ == "__main__":
    main()
