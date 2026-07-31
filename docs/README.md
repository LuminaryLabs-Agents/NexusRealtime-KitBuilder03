# Documentation and Pages Archive

`docs/` is the repository's static launcher and playable-game archive. The `LiveHarness-Massive-Build` workflow uploads this directory as its Pages artifact.

Project guides live beside that application:

- [Architecture](architecture.md)
- [Operations](operations.md)
- [Validation](validation.md)
- [Artifact lifecycle](artifact-lifecycle.md)
- [Visual identity](visual-identity.md)

## Contents

- `index.html`, `launcher.js`, and `launcher.css` implement the launcher UI.
- `games.json` is the launcher manifest. It supplies each build's identifier, title, summary, URL, score, visibility, and promotion timestamp.
- `games/<run-id>/` contains build-specific static applications and their supporting files.
- `cleanup.html` explains the public-gallery cleanup policy.
- `fresh-start.json` records a historical reset of the active manifest.

## Launcher behavior

On load, `launcher.js` fetches `games.json` without using a cached response. It ignores entries whose `visibility` is `hidden`, sorts public entries by `promoted_at`, groups versions by title (falling back through prompt, summary, and ID), and renders a version selector for each group. The first current public entry becomes the launcher’s “latest” link.

The checked-in manifest currently lists three public versions of **Massive Voxel DSK Loop Lab**. Each points to a timestamped folder under `docs/games/`.

## Build folders

Treat a folder referenced by `games.json` as a self-contained browser build. The newest listed voxel build includes an HTML entry point, stylesheet, module entry point at `src/boot.js`, application modules under `src/`, a small Node smoke script under `tests/`, and a local README.

Older folders can remain in `docs/games/` without appearing in the launcher. `fresh-start.json` explicitly records that this is expected historical state after the public manifest was reset.

## Maintenance notes

When changing the launcher, preserve the manifest fields consumed by `launcher.js`, especially `id`, `title`, `summary`, `url`, `visibility`, and `promoted_at`. Keep URLs repository-relative so the static artifact can be hosted from its configured site root.

The deterministic validation registry is in `.agent/tools.json`; `agent_tools/run_tools.py` runs registered checks. `agent_tools/launcher_manifest.py` currently expects every manifest target to contain `index.html`, `style.css`, and `game.js` at its root. The currently listed voxel builds instead use `src/boot.js` as their browser module entry point, so this validator contract should be reconciled before treating its result as proof that the active builds are valid.

## Status boundaries

Implemented: the static launcher, manifest-driven version grouping, timestamped build folders, and Pages-artifact upload configuration are present in this repository.

Historical: older game folders and the generated “latest” metadata predate the current active manifest and are not evidence of the current public launcher contents.

Observed during the 2026-07-31 documentation review:

- The configured Pages URL returned HTTP 200.
- The live launcher served a later workflow artifact than the launcher files tracked at current `main`.
- Required queue, state, and repository-policy checks passed locally.
- The latest tracked game's focused Node smoke test passed.
- Optional launcher-manifest and HTML checks failed because they still require legacy root `game.js` files for module builds that use `src/boot.js`.

Do not use Pages availability alone as proof that the deployed artifact matches current `main`.
