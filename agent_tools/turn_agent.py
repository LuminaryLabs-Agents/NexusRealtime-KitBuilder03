from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
from typing import Any

from openai import OpenAI

from .common import append_text, extract_json_object, list_known_files, load_json, safe_repo_path, save_json, write_text
from .run_tools import run_tool_ids

ALLOWED_ACTIONS = ["THINK", "WRITE_FILE", "APPEND_FILE", "UPDATE_GOAL", "MARK_GOAL_COMPLETE", "MARK_GOAL_BLOCKED", "STOP_RUN"]
DEFAULT_ALLOWED_PATHS = [".agent/", "docs/", "src/", "generated/", "agent_tools/"]


def _policy(queue: dict[str, Any]) -> dict[str, int]:
    raw = queue.get("run_policy") if isinstance(queue.get("run_policy"), dict) else {}
    return {
        "max_goals_per_run": int(os.environ.get("MAX_GOALS_PER_RUN") or raw.get("max_goals_per_run") or 7),
        "max_turns_per_goal": int(os.environ.get("MAX_TURNS_PER_GOAL") or raw.get("max_turns_per_goal") or 6),
        "max_total_turns": int(os.environ.get("MAX_TOTAL_TURNS") or raw.get("max_total_turns") or 30),
    }


def _ordered_goals(queue: dict[str, Any]) -> list[dict[str, Any]]:
    goals = [g for g in queue.get("goals", []) if isinstance(g, dict)]
    active = [g for g in goals if g.get("status") == "active"]
    queued = sorted([g for g in goals if g.get("status") == "queued"], key=lambda g: int(g.get("priority", 999)))
    return active + queued


def _criterion_passes(text: str) -> bool | None:
    low = text.lower().strip()
    if low.endswith(" exists"):
        path = text[: -len(" exists")].strip()
        return Path(path).exists()
    if "javascript syntax" in low or "js syntax" in low:
        return None
    if "check passes" in low or "checks pass" in low:
        return None
    return None


def _criteria_complete(goal: dict[str, Any], tools_ok: bool) -> bool:
    criteria = goal.get("success_criteria") or []
    if not criteria:
        return False
    for item in criteria:
        if not isinstance(item, str):
            continue
        passed = _criterion_passes(item)
        if passed is False:
            return False
    required = goal.get("required_tools") or []
    if required and not tools_ok:
        return False
    return True


def _apply_actions(response: dict[str, Any], goal: dict[str, Any], allowed_paths: list[str]) -> list[str]:
    applied: list[str] = []
    actions = response.get("actions") or []
    if not isinstance(actions, list):
        raise ValueError("response.actions must be a list")
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("each action must be an object")
        kind = str(action.get("type") or "").upper()
        if kind in {"WRITE_FILE", "APPEND_FILE"}:
            path = action.get("path")
            content = action.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                raise ValueError(f"{kind} requires path and content")
            target = safe_repo_path(path, allowed_paths)
            if kind == "WRITE_FILE":
                write_text(target, content if content.endswith("\n") else content + "\n")
            else:
                append_text(target, content if content.endswith("\n") else content + "\n")
            applied.append(f"{kind} {target}")
        elif kind == "UPDATE_GOAL":
            patch = action.get("patch") if isinstance(action.get("patch"), dict) else {}
            goal.update(patch)
            applied.append("UPDATE_GOAL")
        elif kind == "MARK_GOAL_COMPLETE":
            goal["status"] = "complete"
            applied.append("MARK_GOAL_COMPLETE")
        elif kind == "MARK_GOAL_BLOCKED":
            goal["status"] = "blocked"
            applied.append("MARK_GOAL_BLOCKED")
        elif kind == "STOP_RUN":
            applied.append("STOP_RUN")
        elif kind == "THINK":
            applied.append("THINK")
        else:
            raise ValueError(f"unsupported action type: {kind}")
    goal_update = response.get("goal_update")
    if isinstance(goal_update, dict):
        if goal_update.get("completed_step"):
            progress = goal.setdefault("progress", {})
            steps = progress.setdefault("completed_steps", [])
            if goal_update["completed_step"] not in steps:
                steps.append(goal_update["completed_step"])
        if goal_update.get("next_step"):
            goal.setdefault("progress", {})["next_step"] = goal_update["next_step"]
        if goal_update.get("status") in {"queued", "active", "blocked", "complete", "failed"}:
            goal["status"] = goal_update["status"]
    return applied


def main() -> None:
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing NVIDIA_API_KEY secret")
    model = os.environ.get("NVIDIA_MODEL", "").strip() or "nvidia/nemotron-3-ultra-550b-a55b"
    run_note = os.environ.get("RUN_PROMPT", "").strip() or "Work through the queue safely until a checkpoint is reached."
    allowed_paths = [p for p in os.environ.get("ALLOWED_PATHS", ",".join(DEFAULT_ALLOWED_PATHS)).split(",") if p]

    queue = load_json(".agent/queue.json", {"version": 1, "goals": []})
    state = load_json(".agent/state.json", {"version": 1, "turn_count": 0})
    policy = _policy(queue)
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_dir = Path(".agent/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

    total_turns = 0
    goals_done = 0
    transcript: list[str] = []
    latest_tools: dict[str, Any] | None = None
    stop_run = False

    for goal in _ordered_goals(queue):
        if goals_done >= policy["max_goals_per_run"] or total_turns >= policy["max_total_turns"] or stop_run:
            break
        goal["status"] = "active"
        queue["active_goal_id"] = goal.get("id")
        turns_for_goal = 0
        tools_ok = False

        while turns_for_goal < policy["max_turns_per_goal"] and total_turns < policy["max_total_turns"]:
            turns_for_goal += 1
            total_turns += 1
            turn_request = {
                "schema_version": 1,
                "mode": "queue_worker_turn",
                "run_id": run_id,
                "turn_index": total_turns,
                "goal": goal,
                "repo_context": {
                    "allowed_paths": allowed_paths,
                    "known_files": list_known_files(allowed_paths),
                },
                "latest_tool_results": latest_tools,
                "allowed_actions": ALLOWED_ACTIONS,
                "run_note": run_note,
            }
            save_json(run_dir / f"turn-{total_turns:03d}-request.json", turn_request)

            prompt = {
                "instruction": "Return only valid JSON matching the Nexus turn response contract. Do one bounded repo-building move. Use tools/tests feedback when present.",
                "turn_request": turn_request,
                "response_contract": {
                    "decision": "THINK | WRITE_FILE | APPEND_FILE | UPDATE_GOAL | MARK_GOAL_COMPLETE | MARK_GOAL_BLOCKED | STOP_RUN",
                    "summary": "brief operational summary",
                    "actions": [{"type": "WRITE_FILE", "path": "src/example.js", "content": "..."}],
                    "goal_update": {"goal_id": goal.get("id"), "status": "active", "completed_step": "optional", "next_step": "optional"},
                    "requested_tools": ["optional registered tool ids"],
                    "continue": True,
                },
            }
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a bounded repo worker. Return only JSON. Never include markdown fences."},
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
                temperature=0.55,
                top_p=0.95,
                max_tokens=8192,
                extra_body={"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 4096},
            )
            raw = completion.choices[0].message.content or ""
            response = extract_json_object(raw)
            save_json(run_dir / f"turn-{total_turns:03d}-response.json", response)

            applied = _apply_actions(response, goal, allowed_paths)
            requested = response.get("requested_tools") if isinstance(response.get("requested_tools"), list) else []
            tool_ids = list(dict.fromkeys(list(goal.get("required_tools") or []) + [str(x) for x in requested]))
            latest_tools = run_tool_ids(tool_ids, {"allowed_paths": allowed_paths, "run_id": run_id}, include_required=True)
            save_json(run_dir / f"turn-{total_turns:03d}-tools.json", latest_tools)
            tools_ok = bool(latest_tools.get("ok"))

            applied_md = [
                f"# Turn {total_turns}",
                "",
                f"Goal: `{goal.get('id')}`",
                f"Decision: `{response.get('decision')}`",
                "",
                "## Summary",
                "",
                str(response.get("summary", "")),
                "",
                "## Applied",
                "",
                *(f"- {item}" for item in applied),
                "",
                "## Tools OK",
                "",
                str(tools_ok),
                "",
            ]
            write_text(run_dir / f"turn-{total_turns:03d}-applied.md", "\n".join(applied_md))
            transcript.append(f"Goal {goal.get('id')} turn {turns_for_goal}: {response.get('decision')} - {response.get('summary')}")

            if "STOP_RUN" in applied or response.get("decision") == "STOP_RUN":
                stop_run = True
                break
            if goal.get("status") == "complete" or _criteria_complete(goal, tools_ok):
                goal["status"] = "complete"
                goals_done += 1
                break
            if response.get("continue") is False and tools_ok:
                break

        if goal.get("status") == "active" and not stop_run:
            goal.setdefault("progress", {})["next_step"] = goal.get("progress", {}).get("next_step", "continue active goal")

    if not any(g.get("status") == "active" for g in queue.get("goals", []) if isinstance(g, dict)):
        queue["active_goal_id"] = None
    state["latest_run_id"] = run_id
    state["latest_summary"] = transcript[-1] if transcript else "No turns executed"
    state["status"] = "completed"
    state["turn_count"] = int(state.get("turn_count", 0) or 0) + total_turns

    save_json(".agent/queue.json", queue)
    save_json(".agent/state.json", state)
    write_text(".agent/LATEST.md", "# Latest Nexus Turn Agent Run\n\n" + "\n".join(f"- {line}" for line in transcript) + "\n")
    save_json(run_dir / "run-summary.json", {"run_id": run_id, "model": model, "total_turns": total_turns, "goals_completed": goals_done, "stop_run": stop_run})

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        append_text(summary_path, "# Nexus Turn Agent\n\n" + "\n".join(f"- {line}" for line in transcript) + "\n")


if __name__ == "__main__":
    main()
