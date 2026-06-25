from __future__ import annotations

from pathlib import Path
import subprocess

from .common import result

DEFAULT_ALLOWED = [".agent/", "docs/", "src/", "generated/", "agent_tools/"]


def _changed_files() -> list[str]:
    try:
        proc = subprocess.run(["git", "status", "--porcelain"], text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return []
    files: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def run(context: dict | None = None) -> dict:
    allowed = list((context or {}).get("allowed_paths") or DEFAULT_ALLOWED)
    changed = _changed_files()
    errors: list[str] = []
    warnings: list[str] = []
    for path in changed:
        normalized = path.replace("\\", "/")
        if normalized.startswith(".github/workflows/"):
            errors.append(f"agent run changed workflow file: {normalized}")
            continue
        if not any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in allowed):
            errors.append(f"changed path outside allowed prefixes: {normalized}")
    if not changed:
        warnings.append("No changed files detected")
    ok = not errors
    return result("repo_policy_check", ok, "Repo policy passed" if ok else "Repo policy failed", errors, warnings, {"changed_files": changed, "allowed_paths": allowed})
