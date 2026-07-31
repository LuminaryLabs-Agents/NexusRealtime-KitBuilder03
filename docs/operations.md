# Operations Guide

## Scope

This repository contains two implemented automation lanes:

- The **Nexus Turn Agent** lane builds repository changes from a queued, bounded set of goals.
- The **LiveHarness** lane builds and promotes sandbox-validated browser-game candidates.

The GitHub Pages artifact is published from `docs/`. The launcher reads `docs/games.json` and links to entries below `docs/games/`.

## Choose an operation

| Need | Workflow | Result |
| --- | --- | --- |
| Turn an idea into a structured queue | `.github/workflows/Nexus-Queue-Builder.yml` | Updates `.agent/queue.json` and records queue-builder artifacts under `.agent/runs/`. |
| Execute bounded queue goals | `.github/workflows/Nexus-Turn-Agent.yml` | Applies permitted repository changes, records each turn under `.agent/runs/`, runs deterministic tools, and commits changes when present. |
| Route a queue build, turn-agent run, game-builder request, or combined sequence | `.github/workflows/Main.yml` | Dispatches the selected child workflow or workflows. |
| Produce a sandbox-first game candidate and deploy Pages | `.github/workflows/LiveHarness-Massive-Build.yml` | Records a build run under `LiveHarnessV.01/runs/`, promotes a passing candidate to `docs/games/`, updates the launcher manifest, commits once, and deploys `docs/`. |
| Run the alternate expanded build entry point | `.github/workflows/LiveHarness-Expanded-Build.yml` | Invokes the same `massive_build_loop_v3` entry point with fixed worker and loop limits, then stages Pages. |
| Generate idea-inbox artifacts | `.github/workflows/LiveHarness-Idea-Inbox.yml` | Records a batch run and commits generated run artifacts. |

The legacy NVIDIA game-builder workflow is manual-only and reports that public `docs/` generation should use LiveHarness Massive Build.

## Nexus Turn Agent lane

1. Keep the durable intent in `.agent/goal.md` and the execution contract in `.agent/workflow.md`.
2. Use the queue builder when `.agent/queue.json` needs to be created or refreshed from a high-level idea.
3. Use the turn agent to process queued or active goals. Its default limits are 7 goals, 6 turns per goal, and 30 total turns; workflow-dispatch inputs can override them.
4. Inspect `.agent/LATEST.md`, `.agent/state.json`, and the matching `.agent/runs/<run-id>/` directory after a run.

The turn agent may write only in `.agent/`, `docs/`, `src/`, `generated/`, and `agent_tools/`. It does not permit its model actions to change `.github/workflows/`.

The deterministic tool registry is `.agent/tools.json`. Required baseline checks are `queue_check`, `state_check`, and `repo_policy_check`; JavaScript, launcher-manifest, and HTML-smoke checks are also registered. The workflow runs the final deterministic tool command after the queue worker.

## LiveHarness massive-build lane

Run `.github/workflows/LiveHarness-Massive-Build.yml` with an optional repository-relative prompt file and optional worker and loop limits. When no prompt file is supplied, the workflow selects the latest Markdown file from `LiveHarnessV.01/expanded-prompts/` or `LiveHarnessV.01/prompt-inbox/`.

Each run is stored at `LiveHarnessV.01/runs/<run-id>/`. Key inspection points are:

- `input/` - selected prompt, interpretation, goal, and intake artifacts.
- `swarm/` and `write-sets/` - worker outputs and the reconciled candidate write-set.
- `sandbox/` - the candidate before public promotion.
- `validation/validation-summary.json` - sandbox validation result and failed filters.
- `self-alignment/final-self-review.json` - advance or revise decision.
- `status/final-status.json` - authoritative completion status.
- `status/failure.json` - present when the build did not reach a successful public result.
- `final-report.md` - concise run summary.

The implementation applies reconciled files to the sandbox first. It promotes a candidate only after sandbox validation passes and self-alignment returns `ADVANCE`. Promotion copies the candidate to `docs/games/<candidate-id>/`, inserts it into `docs/games.json`, and regenerates the launcher files. The manifest is capped at ten entries by the promotion code.

Sandbox validation includes path, public-output, size, required-file, module-graph, domain-boundary, renderer-boundary, GameHost, JavaScript-syntax, and run-artifact-completeness checks. The v3 entry point also adds composition checks.

After promotion, final public validation checks active public output for prohibited control-plane terms and applies domain, GameHost, and legacy-output checks.

## Verification and triage

Treat `LiveHarnessV.01/runs/<run-id>/status/final-status.json` with `status: "success"` and `validation_ok: true` as the success signal for a massive build. A workflow run can continue to later commit and Pages steps after the build command exits nonzero, so workflow completion alone is not sufficient evidence of a successful candidate.

For a failed massive build:

1. Read `status/failure.json` and `validation/validation-summary.json`.
2. Use the first failed filter and recorded `loopback` target to identify the failed stage.
3. Review the corresponding loop record in `loops/` and worker artifacts in `swarm/`.
4. Preserve the run artifacts; they are the repository’s recorded evidence for the attempt.

For launcher issues, compare `docs/games.json` with the referenced `docs/games/<id>/` folder. The local launcher-manifest check expects each listed game folder to contain `index.html`, `style.css`, and `game.js`.

## Current planned work

`.agent/queue.json` currently lists queued work for the agent-harness foundation, deterministic tools, launcher quality, reusable browser-game runtime files, a layered demo, broader validation, and archive polish. These are plans, not proof that the corresponding goals are complete.

## Historical note

`docs/fresh-start.json` records a previous reset of the active game manifest and notes that older game folders can remain in `docs/games/` without being linked from the public launcher.
