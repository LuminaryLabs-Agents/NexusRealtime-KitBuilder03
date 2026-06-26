---
mode: kit-builder
public_title: Voxel Domain Builder
public_goal: Build a Three.js Minecraft-like voxel world experiment that demonstrates NexusRealtime domain service boundaries.
private_harness_notes:
  - preserve run artifacts
  - run deterministic checks
  - update capability ledger
---

# Product Requirements

Create a browser-playable voxel world with:

- Three.js block terrain made from grass, dirt, stone, wood, and glass descriptors
- first-person or over-shoulder movement with state-scoped input
- build and break actions routed conceptually through a Build Break Domain Service Kit
- inventory block palette with selected block state
- debug host exposing player position, selected block, block count, and domain trace
- public UI that avoids control-plane metadata

Keep gameplay meaning in domain/service concepts. The renderer should present blocks and input feedback only.
