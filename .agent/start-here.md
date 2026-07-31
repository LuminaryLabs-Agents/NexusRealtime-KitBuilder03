# Start Here

## Purpose

This is an experimental KitBuilder workspace for shaping and validating NexusRealtime-compatible kit candidates before promotion. It is not the stable runtime, final ProtoKits registry, or public experiments gallery.

Active harness metadata selects `LiveHarnessV.01` and requires manual review for promotion.

## Two implemented automation paths

- `.agent/` contains a bounded queue-driven repo-building harness. Its GitHub workflows build a queue, execute small allowed file actions, and run registered deterministic checks.
- `LiveHarnessV.01/` contains the active ledger-driven build harness. It turns an input prompt into a sandboxed game candidate, validates it, then promotes passing output to `docs/`.

The repository does not document a replacement relationship between these paths. Treat them as coexisting until that decision is made.

## LiveHarness build flow

`LiveHarnessV.01/prompt-inbox/` or `LiveHarnessV.01/expanded-prompts/`
→ intake and interpretation artifacts in `LiveHarnessV.01/runs/<run-id>/`
→ bounded swarm and reconciled write-set
→ sandbox candidate and validation
→ promotion to `docs/games/<candidate-id>/` only after passing checks
→ `docs/games.json` and the launcher are regenerated.

The massive-build workflow owns public `docs/` output. Run artifacts, ledgers, and state are retained under `LiveHarnessV.01/` for review.

## Where to look first

- `README.md` - repository role and promotion requirements.
- `.agent/goal.md` and `.agent/workflow.md` - queue-worker goals, write boundaries, and deterministic tool model.
- `LiveHarnessV.01/README.md` and `LiveHarnessV.01/goals/goal.md` - active harness purpose and operating model.
- `LiveHarnessV.01/docs/massive-build-loop.md` - massive-build stages and validation gates.
- `.github/workflows/LiveHarness-Massive-Build.yml` - automation entry point for the active sandbox-first build path.
- `docs/index.html`, `docs/launcher.js`, and `docs/games.json` - current public launcher and active-build manifest.

## Conventions to preserve

- Keep build decisions and validation evidence in the versioned run artifacts and append-only ledgers.
- Do not write public launcher output directly from swarm workers; reconcile and validate in the sandbox first.
- Keep public game output under `docs/games/<candidate-id>/`; the launcher reads `docs/games.json`.
- Favor small, auditable changes. The queue worker is limited to `.agent/`, `docs/`, `src/`, `generated/`, and `agent_tools/`; it does not edit workflow files.
- Generated games may include local fallbacks when external integration is unavailable; inspect each candidate's README and source before treating an integration as required at runtime.

## Recorded state

The latest recorded massive build is `2026-06-27T23-46-02Z-massive-build-011-massive-voxel-dsk-loop`. Its final report records a successful sandbox validation and promotion of a voxel-world experiment to `docs/games/2026-06-27t23-46-02z-massive-build-011-massive-voxel-dsk-loop-voxel-dsk/`.

During the 2026-07-31 documentation review, the required queue/state/policy checks and this build's focused Node smoke test passed. The configured Pages URL returned HTTP 200 but served a later workflow artifact than tracked `main`. Optional manifest and HTML checks retained a known legacy `game.js` mismatch.

## Unresolved Decisions

- Is the `.agent/` queue-worker path still intended for new work, or retained as a parallel earlier harness?
- Which workflow should be the default entry point for a new build request?
- What review process satisfies the active metadata's `manual_review_required` promotion policy?
- Should legacy `NexusLiveLLM` identifiers be retained as historical harness names or migrated in a separate source-level change?
