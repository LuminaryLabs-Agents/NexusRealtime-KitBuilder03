# AGENTS.md

## Repository role

This is an experimental kit-builder workspace, not the stable NexusRealtime runtime or a final kit registry. It contains two implemented automation paths plus published static browser-game artifacts.

## Architecture

- `.agent/` and `agent_tools/` implement the bounded Nexus Turn Agent: queued goals, local deterministic checks, and restricted write paths.
- `LiveHarnessV.01/` is a versioned, ledger-driven harness. Its state, schemas, prompts, tools, ledgers, and per-run artifacts are kept together.
- `docs/` is the static launcher and public game output. `docs/games.json` is its manifest; `docs/index.html` and `docs/launcher.js` render the launcher.
- `generated/` contains generated summaries and game artifacts.

## Working conventions

- Read the goal and state for the system being changed before editing: `.agent/goal.md` and `.agent/workflow.md` for the Turn Agent; `LiveHarnessV.01/goals/goal.md`, `LiveHarnessV.01/state/project-memory.json`, and `LiveHarnessV.01/HARNESS_MANIFEST.json` for LiveHarness work.
- Keep changes small, auditable, and within the selected system's write boundaries. The Turn Agent permits `.agent/`, `docs/`, `src/`, `generated/`, and `agent_tools/`; the LiveHarness manifest permits `LiveHarnessV.01/`, `docs/`, `src/`, and `generated/`.
- Automated Turn Agent and LiveHarness flows block workflow-file writes. Change `.github/workflows/` only when the task expressly concerns workflow maintenance.
- Preserve the ledger model: record durable state in the established JSON artifacts and keep ledger data append-only where the harness requires it.
- Maintain `.agent/memory.md` when a lasting repository decision, architecture pattern, or user preference changes. Remove superseded entries rather than accumulating duplicates.

## Published games

- Treat `docs/games/<run-id>/` as self-contained published artifacts. Update `docs/games.json` when publishing, hiding, or removing a launcher entry; keep the latest-play link in `docs/index.html` aligned when appropriate.
- The current Voxel example uses a thin HTML shell, an import map, a boot module, separated runtime/world/domain/renderer/host/integration modules, and local fallbacks for unresolved kit imports. Preserve these boundaries when modifying that example.
- The Voxel example exposes `window.GameHost` for observable state and commands. Do not move domain ownership into the renderer or HUD.

## Validation

- Use the registered deterministic checks in `.agent/tools.json` for Turn Agent work. `agent_tools/run_tools.py` is their runner.
- Follow the applicable LiveHarness validation gates for LiveHarness outputs. A prior Massive Build records filters for module boundaries, kit resolution and fallbacks, public output, syntax, and ledger completeness.
- Do not assume an npm test script exists; the current Voxel package only declares ES-module mode and includes a standalone `tests/smoke.mjs`.

## Plans and historical notes

- The `.agent` goal plans reusable systems under `src/` when useful; no root `src/` implementation is currently present.
- `LiveHarnessV.01/runs/` contains historical run evidence. A successful Massive Voxel build is recorded there; it is evidence for that run, not automatic approval for later changes.
- `generated/latest-game-*.md` refers to an older generated game and should not be treated as the current launcher manifest.

## Unknown

The repository does not document whether the Nexus Turn Agent or LiveHarness is the preferred automation path for future work. Choose the path that matches the requested task and avoid changing both unless the task explicitly requires coordination.
