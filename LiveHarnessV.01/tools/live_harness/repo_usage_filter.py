from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import re

from .common import harness_root, repo_root, read_json, write_json, tool_result, ledger, utc_id

ALLOWED_REMOTE_PREFIXES = [
    "https://cdn.jsdelivr.net/gh/LuminaryLabs-Dev/NexusRealtime@",
    "https://cdn.jsdelivr.net/gh/LuminaryLabs-Agents/NexusRealtime-ProtoKits@"
]


def _scan_imports(candidate_dir: Path) -> list[str]:
    imports: list[str] = []
    pattern = re.compile(r"['\"](https://cdn\.jsdelivr\.net/gh/[^'\"]+)['\"]")
    for path in candidate_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        imports.extend(pattern.findall(text))
    return imports


def check_candidate(run_dir: Path, candidate_dir: Path | None = None) -> dict[str, Any]:
    if candidate_dir is None:
        write_set = read_json(run_dir / "write-sets" / "final-write-set.json", {})
        candidate_id = str(write_set.get("candidate_id", ""))
        candidate_dir = run_dir / "sandbox" / "docs" / "games" / candidate_id
    integration_path = run_dir / "intake" / "fused" / "integration-plan.json"
    integration = read_json(integration_path, {})
    warnings: list[str] = []
    errors: list[str] = []
    if not integration_path.exists():
        warnings.append("No fused integration plan found; repo-aware constraints were not available to this candidate.")
    imports = _scan_imports(candidate_dir) if candidate_dir.exists() else []
    for spec in imports:
        if not any(spec.startswith(prefix) for prefix in ALLOWED_REMOTE_PREFIXES):
            errors.append(f"remote import not allowlisted: {spec}")
    if integration.get("mode") == "reference-plus-local-fallback":
        for fallback in integration.get("local_fallbacks", []):
            if not (candidate_dir / fallback).exists():
                warnings.append(f"local fallback not found in candidate: {fallback}")
    result = tool_result("repo_capability_usage_filter", not errors, "Repo capability usage passed" if not errors else "Repo capability usage failed", errors=errors, warnings=warnings, data={"imports": imports, "integration_plan": str(integration_path)})
    out_dir = run_dir / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "repo-capability-usage-filter.json", result)
    ledger("validation-ledger.jsonl", {"time": utc_id(), "event": "repo_usage.checked", "ok": result["ok"], "errors": errors})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()
    run_dir = Path(args.run_dir) if args.run_dir else harness_root() / "runs" / "repo-usage-run"
    if not run_dir.is_absolute():
        run_dir = harness_root() / run_dir
    print(json.dumps(check_candidate(run_dir), indent=2))


if __name__ == "__main__":
    main()
