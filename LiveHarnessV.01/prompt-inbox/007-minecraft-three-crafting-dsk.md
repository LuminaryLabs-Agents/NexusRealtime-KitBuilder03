---
mode: kit-builder
public_title: Voxel Crafting Domain Test
public_goal: Build a Three.js Minecraft-like voxel experiment focused on crafting, inventory, and repeat-safe domain commands.
private_harness_notes:
  - preserve run artifacts
  - run deterministic checks
  - update project memory
---

# Product Requirements

Create a voxel game/tool with:

- a block palette and small inventory state
- a crafting recipe panel for turning wood and stone into a tool descriptor
- repeat-safe command IDs for build, break, collect, and craft actions
- event trace showing command, validation, state change, and event
- world-space block feedback with minimal overlay UI
- window.GameHost.getState() exposing the inventory, commands, and recent events

The public app should focus on NexusRealtime Runtime, Kits, Sequences, DSKs, commands, events, and state.
