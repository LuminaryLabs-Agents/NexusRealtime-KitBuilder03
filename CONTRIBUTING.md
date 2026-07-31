# Contributing

This repository is an experimental workspace for building, validating, and promoting NexusRealtime-compatible kit candidates. Keep contributions small, auditable, and scoped to one clear outcome.

## Choose the right area

- `.agent/` contains the bounded turn-agent goal, queue, state, tool registry, and JSON contracts.
- `agent_tools/` contains deterministic, repository-local validation tools.
- `docs/` contains the static launcher, its game manifest, and generated playable builds.
- `generated/` contains generated artifacts.
- `LiveHarnessV.01/` contains the ledger-driven LiveHarness system and its run artifacts.

Do not infer that this repository is the stable runtime, a final kit registry, or a production game surface. Those uses are explicitly outside the repository's stated scope.

## Working conventions

- Prefer a small, coherent change over a broad rewrite.
- Preserve JSON schema and queue conventions when changing `.agent/` artifacts.
- Keep generated game pages self-contained under `docs/games/<run-id>/` and add public builds to `docs/games.json` only when the entry and folder agree.
- Use repository-relative paths in documentation and generated metadata.
- Do not include credentials or other sensitive values in committed files.

For work executed by the queue-driven turn agent, stay within its declared write boundary: `.agent/`, `docs/`, `src/`, `generated/`, and `agent_tools/`. That agent must not edit `.github/workflows/`.

## Validate changes

Run the deterministic repository checks when they apply:

```sh
python3 -m agent_tools.run_tools
```

The tool runner includes queue, state, repository-policy, JavaScript-syntax, launcher-manifest, and HTML-smoke checks. For browser-facing changes, also verify the affected launcher or game page directly in a browser.

The current generated voxel build includes a focused Node smoke test at `docs/games/2026-06-27t23-46-02z-massive-build-011-massive-voxel-dsk-loop-voxel-dsk/tests/smoke.mjs`; it is evidence of an existing build-specific check, not a documented repository-wide test command.

## Current compatibility note

`agent_tools/launcher_manifest.py` currently requires `index.html`, `style.css`, and `game.js` for every manifest entry. The currently listed active voxel build instead boots from `src/boot.js` and does not contain `game.js`. Resolve that mismatch deliberately before relying on the manifest check for new module-based game builds.

## Plans versus implemented behavior

The queued goals in `.agent/queue.json` describe planned harness, launcher, runtime, demo, validation, and archive work. Their status is currently `queued`; do not describe them as completed functionality.

## Review and support

Use a focused review branch and state the scope, validation performed, and remaining limitations in the pull request. No license is currently detected, so do not assume public visibility grants permission to reuse repository content outside its existing terms.
