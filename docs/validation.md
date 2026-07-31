# Validation

This guide describes the implemented validation paths and the manual checks needed for the public launcher and active game builds. The required checks and focused game smoke command below passed on revision `7caa074a2729f726b4979d543dd6caaf6dffef46` during the 2026-07-31 documentation review.

## Current validation surface

Implemented deterministic tools are registered in `.agent/tools.json`:

- Required: `queue_check`, `state_check`, `repo_policy_check`
- Optional: `js_syntax_check`, `launcher_manifest_check`, `html_smoke_check`

Run the complete registered set from the repository root:

```sh
python3 -m agent_tools.run_tools
```

This default command runs the required queue, state, and repository-policy checks. The runner prints JSON and exits unsuccessfully when any selected check is not OK. Add `--output <repository-relative-path>` only when a persisted JSON result is needed.

Run the optional checks explicitly:

```sh
python3 -m agent_tools.run_tools \
  --tools launcher_manifest_check,html_smoke_check,js_syntax_check
```

On the documented baseline, JavaScript syntax passed while the launcher-manifest and HTML checks reported the known module-layout mismatch below.

## Focused game smoke test

The newest entry in `docs/games.json` has a focused Node smoke test:

```sh
node docs/games/2026-06-27t23-46-02z-massive-build-011-massive-voxel-dsk-loop-voxel-dsk/tests/smoke.mjs
```

This test verifies command-id deduplication, creates a chunk store, and confirms that the generated spawn point is above the terrain surface. It does not validate rendering, browser input, or launcher navigation.

## Manual browser checks

Serve `docs/` through the repository's chosen static-hosting workflow, then check:

1. `docs/index.html` loads the active builds from `docs/games.json`; the version selector and its "Play selected version" link select the expected game folder.
2. Open each active manifest entry and confirm the loading state is replaced by the running game without showing `#errorPanel`.
3. In the newest active game, click the canvas, then verify movement with `W`, `A`, `S`, `D` or arrow keys; inventory selection with `1` through `7`; fly-mode toggle with `F`; block break with primary pointer input; and block placement with secondary pointer input.
4. In the browser console, inspect `window.GameHost.getState()`. Confirm that it reports movement, inventory, build/break, world, renderer, input, event, and integration state. After a build or break action, confirm the corresponding command identifier and event trace are present.

## Known current mismatch

`launcher_manifest_check` and `html_smoke_check` both require every game folder referenced by the manifest to contain `game.js`. The three active manifest folders instead contain `src/boot.js` and do not contain `game.js`. Static inspection therefore indicates those checks are expected to report errors for the current active builds until their expectations or the build layout are aligned.

`js_syntax_check` scans `.js` files under `docs/`, `src/`, and `generated/`; it does not syntax-check the `.mjs` smoke test. Keep the focused Node command above as a separate check.

## Evidence Boundaries

- A passing run-local `final-status.json` proves only that run's recorded gates.
- A successful workflow can still contain a failed commit step or deploy an artifact not committed to `main`.
- The live Pages site can remain reachable while serving a workflow artifact that differs from tracked launcher files.
- Verify Git revision, workflow status, deployed content, and browser behavior independently.

## Browser Proof

Playwright against a local static server on 2026-07-31 verified:

- The launcher rendered one game family and three active builds from `docs/games.json`.
- The version selector linked to the selected tracked build.
- The selected module build progressed from its loading state to a rendered voxel world with runtime HUD state.
- The only console error was a missing `/favicon.ico`.

Human View at 1280x720 also found that the top-left status HUD covers part of the first inventory controls. The favicon and layout issues are existing application limitations and are not repaired by this documentation-only change.

## Historical note

`docs/fresh-start.json` records that older game folders may remain as unlinked historical artifacts. Validate the current public surface through `docs/games.json`; do not treat the presence of an older folder alone as evidence that it is active or compliant with the current checks.
