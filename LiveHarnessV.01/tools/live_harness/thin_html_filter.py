from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import tool_result


def check(candidate_dir: Path) -> dict[str, Any]:
    html = candidate_dir / "index.html"
    if not html.exists():
        return tool_result("thin_html_filter", False, "index.html missing", errors=["index.html missing"])
    text = html.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    errors = []
    if len(lines) > 120:
        errors.append(f"index.html too long: {len(lines)} lines")
    if text.count("<script") > 2:
        errors.append("too many script tags for bounded shell")
    if 'type="module" src="./src/boot.js"' not in text and "type='module' src='./src/boot.js'" not in text:
        errors.append("missing boot module script")
    if "function " in text or "requestAnimationFrame" in text or "GameHost" in text:
        errors.append("html contains gameplay/runtime logic")
    if "prompt" in text.lower() or "workflow" in text.lower() or "orchestrator" in text.lower():
        errors.append("html contains control-plane language")
    return tool_result("thin_html_filter", not errors, "Thin HTML shell passed" if not errors else "Thin HTML shell failed", errors=errors, data={"line_count": len(lines)})


if __name__ == "__main__":
    import sys
    print(json.dumps(check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")), indent=2))
