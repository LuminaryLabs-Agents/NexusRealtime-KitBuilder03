from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import html_smoke, js_syntax, launcher_manifest, queue_check, repo_policy, state_check
from .common import load_json, save_json, result

STATIC_TOOLS = {
    "queue_check": queue_check.run,
    "state_check": state_check.run,
    "repo_policy_check": repo_policy.run,
    "js_syntax_check": js_syntax.run,
    "launcher_manifest_check": launcher_manifest.run,
    "html_smoke_check": html_smoke.run,
}


def load_registry(path: str = ".agent/tools.json") -> dict[str, dict[str, Any]]:
    registry = load_json(path, {"tools": []})
    tools = registry.get("tools", []) if isinstance(registry, dict) else []
    return {tool.get("id"): tool for tool in tools if isinstance(tool, dict) and tool.get("id")}


def run_tool_id(tool_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    func = STATIC_TOOLS.get(tool_id)
    if not func:
        return result(tool_id, False, "Unknown or disabled tool", [f"No static tool registered with id {tool_id}"])
    try:
        value = func(context or {})
    except Exception as exc:  # noqa: BLE001
        return result(tool_id, False, "Tool raised an exception", [f"{type(exc).__name__}: {exc}"])
    if not isinstance(value, dict):
        return result(tool_id, False, "Tool returned invalid value", ["Tool must return a JSON-compatible object"])
    value.setdefault("id", tool_id)
    value.setdefault("ok", False)
    value.setdefault("summary", "No summary")
    value.setdefault("errors", [])
    value.setdefault("warnings", [])
    value.setdefault("data", {})
    return value


def run_tool_ids(tool_ids: list[str] | None = None, context: dict[str, Any] | None = None, include_required: bool = True) -> dict[str, Any]:
    registry = load_registry()
    selected: list[str] = []
    if include_required:
        selected.extend([tool_id for tool_id, tool in registry.items() if tool.get("required")])
    if tool_ids:
        selected.extend(tool_ids)
    ordered: list[str] = []
    for tool_id in selected:
        if tool_id and tool_id not in ordered:
            ordered.append(tool_id)
    results = [run_tool_id(tool_id, context) for tool_id in ordered]
    return {"ok": all(item.get("ok") for item in results), "tools": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Nexus deterministic tools")
    parser.add_argument("--tools", default="", help="Comma-separated tool ids")
    parser.add_argument("--output", default="", help="Optional JSON output path")
    parser.add_argument("--no-required", action="store_true", help="Do not automatically include required tools")
    args = parser.parse_args()
    tool_ids = [item.strip() for item in args.tools.split(",") if item.strip()]
    value = run_tool_ids(tool_ids, include_required=not args.no_required)
    print(json.dumps(value, indent=2, ensure_ascii=False))
    if args.output:
        save_json(Path(args.output), value)
    if not value.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
