# Artifact lifecycle

This repository keeps build evidence in `LiveHarnessV.01/` and publishes validated browser-game candidates under `docs/games/`. The public launcher reads `docs/games.json`.

## Implemented build lifecycle

```text
prompt -> run evidence -> reconciled write set -> sandbox candidate
      -> validation and self-alignment -> public candidate -> final status
```

1. A run is created at `LiveHarnessV.01/runs/<run-id>/`. It records the prompt, interpretation, intake, swarm-worker outputs, write sets, validation results, alignment reviews, logs, and status.
2. The reconciler writes both `write-sets/proposed/reconciled-write-set.json` and `write-sets/final-write-set.json`. A write set contains candidate-relative file paths and content.
3. The sandbox applier accepts only `docs/games/` paths and writes them below `runs/<run-id>/sandbox/`. Rejected paths are recorded with the sandbox-apply result.
4. Validation records individual filter results and `validation/validation-summary.json`. A failed filter routes the next loop to a repair target; the build can make up to its configured loop limit.
5. When sandbox validation passes and self-alignment returns `ADVANCE`, promotion copies the candidate to `docs/games/<candidate-id>/`, updates `docs/games.json`, regenerates the launcher, and writes `status/promotion-result.json`.
6. Final public validation runs after promotion. `status/final-status.json` reports `success` only when both promotion and final public validation succeed. A failed final-public check leaves a `failure_with_artifacts` status; the implemented code does not roll back the already promoted candidate.

Promotion replaces an existing public folder only when the candidate ID is the same. The public manifest is limited to ten entries, but this truncation alone does not remove older directories from `docs/games/` or create capsules for them.

## Validation and audit trail

The sandbox checks path safety, public-output content, repository-capability usage, file limits, required files, module imports, domain and renderer boundaries, `GameHost`, syntax, and run-artifact completeness. Composition builds add HTML-shell, import-map, kit-resolution, fallback, and kit-proof checks.

The harness appends lifecycle events to `LiveHarnessV.01/ledgers/`, including reconciliation and sandbox application in `artifact-ledger.jsonl`, validation results in `validation-ledger.jsonl`, alignment results in `alignment-ledger.jsonl`, and completed builds in `build-ledger.jsonl`.

## Learning, catalog, and purge path

`post_run_pipeline.py` implements a separate catalog-and-retention flow:

- `game_catalog.py` scans `docs/games/` and `docs/games.json`, then writes `state/gallery-index.json`.
- `game_scorer.py` assigns a score and fate: `keep_active` at 70 or above, `repair_candidate` from 55 through 69, and `purge_after_capsule` below 55.
- `learning_compressor.py` writes per-run game capsules to `learning/game-capsules.json`, updates `state/project-memory.json`, and records capsule events. `capability_tracker.py` updates `state/capability-ledger.json`.
- `purge_agent.py` writes `purge/purge-plan.json`. It protects the first configured number of supplied entries, then keeps the highest-scoring entries up to `max_active_games`.
- `apply_purge.py` creates a capsule at `LiveHarnessV.01/archive/game-capsules/<game-id>.json`, removes the selected ID from `docs/games.json`, and records planned game-folder pruning. It explicitly retains the folder for a later hardened janitor stage; it does not delete files.

`state/gallery-policy.json` declares a `hard_delete_after_capsule` mode, but the current purge implementation performs manifest hiding and capsule creation only. Its planner currently uses the active-count and protected-count fields; it does not apply the policy's minimum-score or feature-contributor fields.

## Historical note

The recorded massive-build runs show reconciled write sets, sandbox application, validation, promotion, and successful final statuses. The latest recorded run also contains the complete expected run-artifact structure, including intake, sandbox files, validation results, and promotion status.

## Open questions

- No invocation of `post_run_pipeline.py` was found in the inspected massive-build workflow; whether it is run manually or by another external process is not established here.
- No hardened janitor implementation or retention schedule was found. The trigger and conditions for physical removal of archived game folders remain unspecified.
- The intended relationship between manifest truncation during promotion and the separate capsule-and-purge path is not specified.
