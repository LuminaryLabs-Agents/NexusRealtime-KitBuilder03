# Repository Profile

## Purpose and status

This is an experimental kit-building workspace, not the stable runtime or final kit registry. Its checked-in implementation centers on `LiveHarnessV.01`, an active, ledger-driven harness that produces sandbox-validated static browser builds.

`HARNESS_ACTIVE.json` identifies `LiveHarnessV.01` as active. Its orchestration state is idle, and project memory records a successful massive build whose public output is the latest entry in `docs/games.json`.

## Implemented architecture

```txt
prompt / run input
  -> LiveHarnessV.01 tools and typed schemas
  -> per-run artifacts, planning, bounded worker slots, and reconciliation
  -> sandbox candidate and validation gates
  -> docs/ public launcher and versioned game output
```

The massive build loop prepares an isolated run, performs source intake and swarm planning, reconciles a multi-file write set, applies it to a sandbox, validates it, and promotes a passing candidate to `docs/games/<candidate-id>/`. It also records status and ledger artifacts.

The current public build is a module-based voxel experiment. Its game entrypoint assembles runtime services (command queue, event bus, clock), world state, gameplay domains, renderer, input, HUD, and `window.GameHost`. The build/break domain owns build commands and emits events; the renderer presents state.

## Key paths

```txt
.agent/                         Earlier bounded queue/turn-agent template state and contracts
agent_tools/                    Local deterministic checks and queue/turn-agent utilities
LiveHarnessV.01/
  goals/                        Harness goal documents
  prompts/, prompt-inbox/       Versioned prompt contracts and queued product prompts
  schemas/                      JSON contracts for harness inputs, outputs, and state
  state/                        Current harness state, policies, capability records, and memory
  tools/live_harness/           Harness implementation modules
  ledgers/                      Append-only JSONL decision and artifact records
  runs/                         Per-run inputs, sandbox outputs, validation, and reports
  docs/                         Harness workflow documentation
docs/                           Static public launcher, build manifest, and promoted games
HARNESS_ACTIVE.json             Active harness selector
README.md                       Repository role and promotion boundary
```

## Conventions

- Keep generated work isolated under `LiveHarnessV.01/runs/<run-id>/`; the documented swarm model forbids workers from writing directly to `docs/`.
- Treat JSON schemas as the contracts between harness stages. Keep run evidence and ledgers as JSON or JSONL artifacts.
- Promote public game files only after sandbox validation. The current massive-loop implementation rebuilds the launcher from `docs/games.json` during promotion.
- Public game builds are self-contained directories under `docs/games/` with an HTML shell, module entrypoints, source modules, and a smoke test.
- Preserve domain boundaries: runtime services coordinate commands and events, domains own state transitions, and renderers present state.

## Documented intent and historical context

- The root README describes this repository as a KitBuilder-lane workspace used to test kit structure, prompts, generated files, and promotion rules before promotion elsewhere.
- `.agent/goal.md` describes an earlier or parallel goal: a reusable YAML-driven LLM repository-building template with a static browser-game launcher. Its workflow document defines bounded queue-worker turns and local deterministic checks.
- `LiveHarnessV.01/goals/goal.md` defines the active harness goal as a versioned, ledger-driven multi-agent game and app factory.

## Verified Operational State

- GitHub Actions contains queue-agent and LiveHarness workflow entrypoints; LiveHarness workflows can commit artifacts and deploy `docs/`.
- Recent historical workflow outcomes are mixed. Several build steps and Pages deployments succeeded while their commit steps failed.
- The Pages URL was reachable on 2026-07-31 but served a later workflow artifact than tracked `main`.
- Required queue/state/policy checks and the newest tracked game's focused smoke test passed locally.
- Optional launcher-manifest and HTML checks fail against active module builds because they still require legacy root `game.js` files.

## Unresolved Decisions

- The relationship and migration status between the `.agent` queue/turn-agent template and `LiveHarnessV.01`.
- The long-term retention policy for historical runs and generated game folders.
- Whether legacy `NexusLiveLLM` identifiers remain intentional.
