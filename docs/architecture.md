# Architecture

## Scope

This repository is an experimental KitBuilder workspace, not the stable NexusRealtime runtime or final kit registry. It contains two implemented automation paths that share repository output areas but maintain separate state and artifacts.

## Implemented components

- `.agent/` and `agent_tools/` implement a bounded turn-agent system. `.agent/queue.json` holds prioritized goals; `.agent/state.json` records turn state; schemas define queue and turn payloads. `agent_tools/turn_agent.py` applies one allowed action at a time and records per-turn artifacts under `.agent/runs/`.
- `LiveHarnessV.01/` implements the versioned LiveHarness system. Its `state/`, `schemas/`, `prompts/`, `tools/live_harness/`, `ledgers/`, and `runs/` directories separate configuration, contracts, executable orchestration, append-only records, and run evidence.
- `docs/` is the static public-output area. `docs/index.html`, `docs/launcher.js`, and `docs/games.json` form the launcher; promoted game candidates live in `docs/games/<candidate-id>/`.
- `.github/workflows/` contains workflow entry points for the turn-agent and LiveHarness build paths, including Pages deployment for LiveHarness workflows.

## Turn-agent flow

1. The queue builder turns a high-level idea into `.agent/queue.json`.
2. The turn agent selects an active or queued goal and constructs a JSON turn request from `.agent/` state and allowed repository context.
3. The response may perform one bounded action: think, write or append an allowed file, update goal state, block or complete a goal, or stop.
4. Registered deterministic checks validate queue/state/policy and, when requested, JavaScript, HTML, and launcher output.
5. Requests, responses, applied actions, and tool results are saved under `.agent/runs/<run-id>/`.

The turn agent is restricted to `.agent/`, `docs/`, `src/`, `generated/`, and `agent_tools/`; it rejects workflow-file changes.

## LiveHarness build flow

The massive-build entry point prepares a run under `LiveHarnessV.01/runs/<run-id>/`, then performs:

```text
prompt
-> master interpretation and goal AST
-> source-intake reports and fused integration plan
-> swarm plan and bounded slot dispatch
-> slot validation and reconciled write-set
-> sandbox application
-> composition and sandbox validation
-> self-alignment and repair loop, if needed
-> promotion to docs/ only after success
-> final public validation
```

Run artifacts preserve inputs, intake results, swarm outputs, write sets, sandbox contents, validation records, loop state, status, and final report. The build loop updates LiveHarness project memory and capability evidence after completion.

Promotion copies a validated candidate from the run sandbox to `docs/games/<candidate-id>/`, prepends its metadata to `docs/games.json`, rerenders the launcher, and then runs final public validation. The launcher keeps only the first ten manifest entries during this promotion path.

## Generated game boundary

The currently promoted voxel-game candidates use a modular browser structure:

- `src/runtime/` provides clock, event bus, command queue, and local runtime utilities.
- `src/domains/` owns movement, inventory, build/break behavior, and objective sequence state.
- `src/world/` owns chunk storage, procedural data, spawning, and world loading.
- `src/renderer/` renders state and camera/material concerns; validation rejects gameplay ownership in renderer modules.
- `src/host/` connects input and HUD, and exposes `window.GameHost` for state inspection and commands.
- `src/integration/` resolves optional kit imports and supplies local fallbacks.

LiveHarness validation requires generated candidates to remain inside `docs/games/`, keep required modules present, resolve local imports within the candidate, expose expected domain traces and `GameHost` state, and pass syntax, public-output, and composition checks.

## Planned direction

The repository goal describes an intended reusable template for YAML-driven LLM repository building. It calls for a Pages launcher, generated games, reusable `src/` systems when useful, generated artifacts, durable agent memory, and incremental auditable changes. These are goals, not evidence that a shared root `src/` runtime is currently implemented.

## Governance note

`LiveHarnessV.01/docs/massive-build-loop.md` assigns public `docs/` ownership to the LiveHarness Massive Build workflow. The separate turn-agent policy also permits writes under `docs/`. Until ownership precedence is defined, public-output changes should be coordinated to avoid competing writers.
