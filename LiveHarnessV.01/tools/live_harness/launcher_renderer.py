from __future__ import annotations

from pathlib import Path
from typing import Any
import html
import json

from .common import repo_root, write_json, utc_id, ledger


def render(scored: list[dict[str, Any]], purge_plan: dict[str, Any], run_dir: Path) -> None:
    repo = repo_root()
    docs = repo / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    hidden = {d.get("game_id") for d in purge_plan.get("decisions", []) if d.get("safe_to_apply", False)}
    active = [g for g in scored if g.get("id") not in hidden]
    active = sorted(active, key=lambda g: int(g.get("score", 0) or 0), reverse=True)[:10]
    manifest = []
    for game in active:
        manifest.append({
            "id": game.get("id"),
            "title": game.get("title") or game.get("id"),
            "prompt": game.get("prompt", ""),
            "url": game.get("url") or f"games/{game.get('id')}/",
            "score": game.get("score"),
            "status": "active",
            "visibility": "public"
        })
    (docs / "games.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    cards = []
    for idx, game in enumerate(manifest, start=1):
        title = html.escape(str(game.get("title")))
        prompt = html.escape(str(game.get("prompt", ""))[:260])
        url = html.escape(str(game.get("url")))
        cards.append(f"<article class='game-card'><div class='rank'>#{idx:02d}</div><div><h2>{title}</h2><p>{prompt}</p><p class='score'>Score {game.get('score', 0)}</p><a class='play' href='{url}'>Play build</a></div></article>")
    latest_url = html.escape(str(manifest[0]["url"])) if manifest else "#"
    index = "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>NexusRealtime KitBuilder03</title><link rel='stylesheet' href='./launcher.css'></head><body><main class='shell'><section class='hero'><p class='eyebrow'>LiveHarnessV.01 rolling frontier</p><h1>KitBuilder03 Active Builds</h1><p class='lede'>The harness keeps the best ten builds, compresses lessons from weaker runs, and carries capabilities forward.</p><a class='primary' href='" + latest_url + "'>Play top build</a><a class='secondary' href='./cleanup.html'>Review cleanup ledger</a></section><section class='ladder'>" + (''.join(cards) if cards else '<p>No active builds yet.</p>') + "</section></main></body></html>"
    css = ":root{color-scheme:dark;font-family:system-ui,sans-serif}body{margin:0;background:#060912;color:#eef5ff}.shell{width:min(1120px,calc(100% - 32px));margin:auto;padding:48px 0}.hero,.game-card,.cleanup-card{border:1px solid rgba(126,255,176,.22);background:rgba(10,18,32,.86);border-radius:28px;padding:24px;margin:16px 0}.eyebrow{color:#9fffc0;text-transform:uppercase;letter-spacing:.16em;font-weight:900}.lede{max-width:760px;color:#cbd7ea;font-size:18px}.primary,.secondary,.play{display:inline-flex;margin:10px 10px 0 0;padding:11px 15px;border-radius:999px;text-decoration:none;font-weight:900}.primary,.play{background:#bfffd2;color:#06110b}.secondary{border:1px solid rgba(255,255,255,.2);color:#eef5ff}.game-card{display:grid;grid-template-columns:74px 1fr;gap:18px}.rank{font-size:28px;font-weight:1000;color:#bfffd2}.score{color:#9fffc0;font-weight:900}table{border-collapse:collapse;width:100%;margin-top:16px}td,th{border:1px solid rgba(255,255,255,.18);padding:8px;text-align:left}th{background:rgba(191,255,210,.14)}"
    (docs / "index.html").write_text(index + "\n", encoding="utf-8")
    (docs / "launcher.css").write_text(css + "\n", encoding="utf-8")
    rows = []
    for decision in purge_plan.get("decisions", []):
        rows.append("<tr><td>" + html.escape(str(decision.get("game_id"))) + "</td><td>" + str(decision.get("score")) + "</td><td>" + html.escape(str(decision.get("decision"))) + "</td><td>" + html.escape('; '.join(decision.get("reason", []))) + "</td></tr>")
    cleanup = "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LiveHarness Cleanup</title><link rel='stylesheet' href='./launcher.css'></head><body><main class='shell'><section class='hero'><p class='eyebrow'>Cleanup and Learning</p><h1>Rolling Gallery Plan</h1><p class='lede'>Max active games: " + str(purge_plan.get('summary', {}).get('max_active_games', 10)) + ". Decisions are logged before public visibility changes.</p><a class='secondary' href='./index.html'>Back to launcher</a></section><section class='cleanup-card'><h2>Plan</h2><table><thead><tr><th>Game</th><th>Score</th><th>Decision</th><th>Reason</th></tr></thead><tbody>" + (''.join(rows) if rows else '<tr><td colspan="4">No cleanup decisions.</td></tr>') + "</tbody></table></section></main></body></html>"
    (docs / "cleanup.html").write_text(cleanup + "\n", encoding="utf-8")
    write_json(run_dir / "purge" / "rendered-launcher.json", {"active_count": len(active), "rendered_at": utc_id()})
    ledger("project-ledger.jsonl", {"time": utc_id(), "event": "launcher.rendered", "active_count": len(active)})
