---
mode: kit-builder
public_title: Composition Host Block World V4
public_goal: Build a browser playable block-world domain lab with repo-aware intake, bounded HTML shell, import map, boot module, NexusRealtime and ProtoKit composition surfaces, local fallbacks, top-of-world spawn, world loading, HUD, inventory, input surface, and GameHost integration diagnostics.
---

# Product Requirements

Create a full first-pass block-world game that works immediately in the browser and is not just a small terrain demo.

Required shell and composition:

- index.html must be a thin bounded host shell
- include an import map for NexusRealtime core, ProtoKits action input, and Three.js
- load only src/boot.js as the boot module
- no gameplay logic in HTML
- GameHost exposes integration mode, selected providers, and fallback notes

Required play surface:

- Player spawns on top of the generated world at a safe surface point
- Infinite procedural terrain loads around the player through a world loading system
- Chunk or patch lifecycle state exposes loaded chunks, unloaded chunks, visible blocks, and revision
- Three.js renderer with camera, fog, lighting, instanced block meshes, and visible chunk radius
- HUD with biome, objective, selected block, domain event count, loaded chunk count, and fly mode
- Inventory bar with selectable blocks
- Input testing surface that shows keys, mouse lock state, and last command
- WASD movement, mouse look, numbered inventory selection, left click clear block, right click place block, F toggle fly
- Place and clear actions routed through domain commands with command IDs
- GameHost state exposing player, world, worldLoader, inventory, domainTrace, events, input, sequence, renderer diagnostics, integration diagnostics, and debug state

Architecture requirements:

- Run source intake loops for NexusRealtime core, NexusRealtime ProtoKits, and KitBuilder03 local structure before the build swarm
- Runtime modules own command queue, event bus, and clock
- Movement domain owns input intent and player state
- Inventory domain owns selected block and block counts
- Build domain owns command trace, applied IDs, and world updates
- World loader owns active chunk windows and load/unload lifecycle
- Sequence domain owns objective state
- Renderer presents state only
- Host maps input into domain requests
