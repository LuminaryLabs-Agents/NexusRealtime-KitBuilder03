from __future__ import annotations

from pathlib import Path

from .common import result


def run(context: dict | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    html_files = list(Path("docs").rglob("*.html")) if Path("docs").exists() else []
    if not html_files:
        return result("html_smoke_check", False, "No HTML files found", ["docs contains no HTML files"])
    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if "<html" not in text or "</html>" not in text:
            errors.append(f"{path} is not a complete HTML document")
        if path.name == "index.html" and "docs/games" in str(path.parent).replace("\\", "/"):
            if "style.css" not in text:
                errors.append(f"{path} does not reference style.css")
            if "game.js" not in text:
                errors.append(f"{path} does not reference game.js")
    if len(html_files) == 1:
        warnings.append("Only one HTML file found")
    ok = not errors
    return result("html_smoke_check", ok, "HTML smoke check passed" if ok else "HTML smoke check failed", errors, warnings, {"html_files": [str(p) for p in html_files]})
