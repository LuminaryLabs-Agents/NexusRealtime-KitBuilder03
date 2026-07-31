# Changelog

This file records repository-verified changes. Dates below are artifact timestamps, not declared releases.

## Unreleased

### Documentation

- Established a public repository overview, maintainer and agent entrypoints, architecture, operations, validation, artifact-lifecycle, security, and contribution guidance.
- Added a reusable visual identity pack under `docs/assets/brand/`.
- Recorded the boundary between tracked `main`, workflow run evidence, and the independently deployed GitHub Pages artifact.
- Preserved the known legacy `game.js` validator mismatch instead of treating optional checks as passing.

## Current documented state - 2026-06-27

### Implemented

- `LiveHarnessV.01` is the active versioned harness and uses a ledger-driven operating model with state, schemas, prompts, tools, ledgers, and per-run artifacts.
- The massive-build workflow performs source intake, plans and dispatches typed slots, reconciles a write set, applies it to a sandbox, validates it, and promotes a successful candidate to `docs/games/`.
- The public launcher reads `docs/games.json`, groups visible builds by family, presents version selection, and links to the selected build.
- The catalog contains three active public entries for **Massive Voxel DSK Loop Lab**. The latest entry is `docs/games/2026-06-27t23-46-02z-massive-build-011-massive-voxel-dsk-loop-voxel-dsk/`.

### Validation recorded

- The latest massive-build entry records successful slot, repository-usage, sandbox, composition, and public-output validation.
- The published voxel-lab artifact documents a bounded HTML shell, import map, boot module, kit resolver, adapter contracts, and local fallbacks.

### Planned architecture

- The current goal describes a versioned, ledger-driven multi-agent game and app factory: large models choose structure, bounded agents fill typed slots, deterministic tools validate outputs, and a reconciler merges final files.

### Historical notes

- The build ledger records three successful massive-build completions on 2026-06-27 for the current voxel-lab family.
- The launcher files tracked at `main` identify the latest visible build as the 2026-06-27T23-46-02Z candidate; a workflow-deployed Pages artifact may differ and must be verified separately.

### Unknowns

- No declared repository release versions, release dates, or semantic-versioning policy were verified.
- The complete change history before the recorded 2026-06-27 artifacts is not established by the inspected files.
