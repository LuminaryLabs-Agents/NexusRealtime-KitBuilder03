# NexusRealtime-KitBuilder03

![NexusRealtime-KitBuilder03 workflow](docs/assets/brand/social-card.png)

`NexusRealtime-KitBuilder03` is an experimental, proof-first builder workspace for NexusRealtime-compatible kit candidates and browser-game prototypes. It uses bounded agent harnesses, deterministic checks, sandboxed candidates, and retained ledgers before selected output reaches the public launcher.

This repository is not the stable NexusRealtime runtime, the canonical ProtoKit registry, or a released game product.

## What It Does

- `LiveHarnessV.01/` records prompts, typed contracts, bounded worker output, reconciliation, validation, reviews, and run evidence.
- `.agent/` and `agent_tools/` provide a separate queue-driven path with restricted actions and deterministic repository checks.
- `docs/games.json` selects the browser builds visible through the [GitHub Pages launcher](https://luminarylabs-agents.github.io/NexusRealtime-KitBuilder03/).
- `docs/games/<build-id>/` retains self-contained browser proofs; unlisted folders are historical artifacts, not active releases.

```text
prompt or queued goal
  -> bounded harness work
    -> reconciled sandbox candidate
      -> deterministic validation and review
        -> retained evidence
          -> selected browser proof
```

## Repository Map

| Path | Responsibility |
| --- | --- |
| `.agent/` | Queue, state, schemas, tool registry, and agent operating guidance |
| `agent_tools/` | Deterministic queue, state, policy, syntax, launcher, and HTML checks |
| `LiveHarnessV.01/` | Active ledger-driven builder harness and preserved run evidence |
| `docs/` | GitHub Pages launcher, active manifest, historical builds, and project documentation |
| `generated/` | Earlier generated-game artifacts and pointers |
| `HARNESS_ACTIVE.json` | Active harness selector and manual-review promotion policy |

## Start Here

1. Read [the documentation map](docs/README.md) and [architecture](docs/architecture.md).
2. Use [operations](docs/operations.md) to choose the queue-agent or LiveHarness lane.
3. Run the applicable checks in [validation](docs/validation.md).
4. Review [artifact lifecycle](docs/artifact-lifecycle.md) before promoting or pruning generated output.
5. Agents should begin with [.agent/start-here.md](.agent/start-here.md).

The required local checks pass on the documented baseline:

```sh
python3 -m agent_tools.run_tools
node docs/games/2026-06-27t23-46-02z-massive-build-011-massive-voxel-dsk-loop-voxel-dsk/tests/smoke.mjs
```

The optional launcher and HTML checks currently expose a known contract mismatch: they require legacy root `game.js` files while active module builds start through `src/boot.js`. See [validation](docs/validation.md) for the exact boundary.

## Current Status

- `LiveHarnessV.01` is the active harness and requires manual review before promotion.
- Tracked `main` lists three active versions of **Massive Voxel DSK Loop Lab**.
- The live Pages deployment was reachable during the 2026-07-31 documentation review, but it served a newer workflow artifact than the launcher files tracked at `main`. Treat Git history, workflow runs, and the deployed Pages artifact as separate evidence surfaces.
- Some checked-in files retain the earlier `NexusLiveLLM` identity. Those names are historical implementation facts, not alternate repository URLs.
- No license is currently detected. Public visibility alone does not grant reuse rights.

See [contributing](CONTRIBUTING.md), [security](SECURITY.md), and the [changelog](CHANGELOG.md) for maintenance guidance.
