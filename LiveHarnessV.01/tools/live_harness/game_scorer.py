from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import repo_root, harness_root, write_json, ledger, utc_id
from .product_brief import sanitize_public_text

HARD_PUBLIC_TERMS = ["NVIDIA", "OpenAI", "chat.completions", "reasoning_budget", "nemotron", "workflow_dispatch"]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def score_entry(entry: dict[str, Any]) -> dict[str, Any]:
    repo = repo_root()
    folder = repo / entry.get("folder", "")
    files = entry.get("files", {})
    tool_score = 0
    playability = 0
    capability = 0
    debuggability = 0
    novelty = 8
    size_sanity = 5

    if files.get("index.html") and files.get("game.js"):
        playability += 10
    if files.get("style.css"):
        playability += 4
    if files.get("README.md"):
        playability += 3
    if entry.get("url"):
        playability += 3

    js = _read_text(folder / "game.js") if folder.exists() else ""
    html = _read_text(folder / "index.html") if folder.exists() else ""
    readme = _read_text(folder / "README.md") if folder.exists() else ""
    manifest_text = str(entry.get("prompt", "")) + " " + str(entry.get("summary", ""))
    combined_raw = js + "\n" + html + "\n" + readme + "\n" + manifest_text
    combined = combined_raw.lower()
    control_hits = [term for term in HARD_PUBLIC_TERMS if term.lower() in combined]

    if "window.gamehost" in combined or "getstate" in combined:
        debuggability += 10
    elif "debug" in combined or "ledger" in combined:
        debuggability += 6
    if "kit" in combined:
        capability += 6
    if "dsk" in combined or "domain service" in combined:
        capability += 6
    if "sequence" in combined:
        capability += 5
    if "show_advanced" in combined or "ask_orchestrator" in combined or "ask_slot" in combined:
        capability += 5
    if "ledger" in combined:
        capability += 3
    if "voxel" in combined or "minecraft" in combined or "block" in combined:
        capability += 4
    if files.get("index.html"):
        tool_score += 10
    if files.get("game.js"):
        tool_score += 10
    if entry.get("exists"):
        tool_score += 10
    if len(js) > 350000:
        size_sanity = 1
    total = min(100, tool_score + min(playability, 20) + min(capability, 25) + min(debuggability, 10) + novelty + size_sanity)
    if control_hits:
        total = min(total, 35)
    if total >= 70:
        fate = "keep_active"
    elif total >= 55:
        fate = "repair_candidate"
    else:
        fate = "purge_after_capsule"
    scored = dict(entry)
    scored.update({
        "title": sanitize_public_text(str(entry.get("title") or entry.get("id"))),
        "prompt": sanitize_public_text(str(entry.get("prompt", ""))),
        "summary": sanitize_public_text(str(entry.get("summary") or entry.get("prompt") or "")),
        "score": total,
        "score_breakdown": {
            "tools": tool_score,
            "playability": min(playability, 20),
            "capability_contribution": min(capability, 25),
            "debuggability": min(debuggability, 10),
            "novelty": novelty,
            "size_sanity": size_sanity,
            "control_plane_hits": len(control_hits),
        },
        "control_plane_bleed": control_hits,
        "fate": fate,
        "last_scored_at": utc_id(),
    })
    return scored


def score_all(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [score_entry(entry) for entry in entries]
    write_json(harness_root() / "state" / "gallery-index.json", {"version": 1, "updated_at": utc_id(), "games": scored})
    for item in scored:
        ledger("capability-ledger.jsonl", {"time": utc_id(), "event": "game.scored", "game_id": item.get("id"), "score": item.get("score"), "fate": item.get("fate"), "control_plane_hits": len(item.get("control_plane_bleed", []))})
    return scored
