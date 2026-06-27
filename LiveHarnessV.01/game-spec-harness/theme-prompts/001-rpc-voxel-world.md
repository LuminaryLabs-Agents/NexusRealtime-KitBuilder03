# Theme Prompt — RPC Procedural Voxel Worlds

Build a family of browser-playable voxel worlds that test whether KitBuilder03 can produce different game variants from one theme.

All variants should share these foundations:

- RPC-style command bus for player actions.
- Procedural voxel terrain with chunk or patch loading.
- Player spawns on top of the generated world.
- Inventory/tool selection.
- Build, clear, or terrain-edit commands with command IDs.
- GameHost state exposing player, worldLoader, RPC/domain trace, input, inventory, and renderer diagnostics.
- Kit-aware integration diagnostics where possible.

Each variant must have a distinct mechanic and world shape.
