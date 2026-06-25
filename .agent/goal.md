# Nexus Turn Agent Goal

Build this repository into a reusable template for LLM-driven repo building through GitHub Actions YAML harnesses.

The agent should incrementally build a playable, layered, static browser-game system without requiring the workflow itself to become large or domain-specific.

The repository should evolve toward:

- a GitHub Pages launcher at `docs/index.html`
- generated playable games under `docs/games/<run-id>/`
- reusable game systems under `src/` when useful
- generated artifacts under `generated/`
- durable agent memory under `.agent/`

The turn agent must work in bounded loops. Each loop may think, write one file, append to one file, or stop.

The agent should prefer small, auditable changes over large rewrites.

The agent should make the repo more useful as a template for YAML-driven LLM building each time it runs.
