# Nexus Turn Agent Workflow

This repository is a YAML-driven LLM build harness template.

The system is split into two harnesses:

1. `Nexus-Queue-Builder.yml` turns a high-level idea into `.agent/queue.json`.
2. `Nexus-Turn-Agent.yml` reads `.agent/queue.json` and executes bounded queue turns.

The repo is the memory layer. The workflow is the executor. The model is the planner/writer for one bounded action at a time.

## Queue worker loop

Each turn-agent run reads:

- `.agent/goal.md`
- `.agent/workflow.md`
- `.agent/queue.json`
- `.agent/state.json`
- `.agent/tools.json`
- recent `.agent/runs/` artifacts when present

Then it processes queued or active goals using bounded turns.

The loop is:

1. pick the next active or queued goal
2. build a turn-request JSON object
3. call the model for a turn-response JSON object
4. validate the response
5. apply safe file actions
6. run deterministic tools and tests
7. save request, response, tool, and applied artifacts
8. update queue and state
9. move to the next goal when complete
10. commit a checkpoint

## Turn request contract

Each model call receives JSON with schema version, mode, run id, turn index, active goal, repo context, latest tool results, and allowed actions.

## Turn response contract

The model must return only JSON with these fields:

- `decision`
- `summary`
- `actions`
- `goal_update`
- `requested_tools`
- `continue`

Allowed action types:

- `THINK`
- `WRITE_FILE`
- `APPEND_FILE`
- `UPDATE_GOAL`
- `MARK_GOAL_COMPLETE`
- `MARK_GOAL_BLOCKED`
- `STOP_RUN`

## Write boundaries

The turn loop may write only inside these prefixes:

- `.agent/`
- `docs/`
- `src/`
- `generated/`
- `agent_tools/`

It must not edit `.github/workflows/` from inside the turn loop.

## Tool layer

Tools are deterministic repo-local checks listed in `.agent/tools.json`.

The model may request a registered tool by id, but it cannot run arbitrary shell commands.

Required baseline tools:

- `queue_check`
- `state_check`
- `repo_policy_check`
- `js_syntax_check`
- `launcher_manifest_check`
- `html_smoke_check`

Tool results are written into `.agent/runs/<run-id>/turn-*-tools.json` and fed back into the next turn.

## Goal completion

A goal can be marked complete when the model marks it complete, or when file-existence success criteria pass and required tools pass.

The agent should prefer small, auditable repo changes over large rewrites.
