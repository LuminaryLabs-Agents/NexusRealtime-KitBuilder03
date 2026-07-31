# Agent Memory

This repository is an experimental, proof-first NexusRealtime builder workspace. It creates and reviews candidate kits and browser-game proofs; it is not the stable runtime, canonical ProtoKit registry, or a released game product.

## Durable Model

- `LiveHarnessV.01/` is the active ledger-driven harness selected by `HARNESS_ACTIVE.json`.
- `.agent/` and `agent_tools/` provide a separate bounded queue-agent path with deterministic checks.
- `docs/games.json` selects active launcher entries; other game folders can be retained historical artifacts.
- Keep candidate work sandboxed until recorded validation and review gates pass.
- Preserve append-only ledgers and per-run evidence.
- Treat tracked Git state, workflow results, and deployed Pages content as separate evidence surfaces.
- Treat legacy `NexusLiveLLM` names as historical implementation facts, not current repository URLs.
- Do not describe the repository as generally reusable open-source software while no license is detected.
- Visual identity assets live under `docs/assets/brand/`.

## Known Validation Boundary

Required queue, state, and repository-policy checks pass on the documented baseline, as does the newest tracked game's focused Node smoke test. Optional launcher-manifest and HTML checks still require legacy root `game.js` files and therefore fail against active module builds that use `src/boot.js`.
