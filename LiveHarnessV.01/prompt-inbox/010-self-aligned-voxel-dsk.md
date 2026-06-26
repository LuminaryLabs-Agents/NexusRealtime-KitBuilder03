---
mode: kit-builder
public_title: Self-Aligned Voxel DSK Lab
public_goal: Build a browser-playable voxel world experiment that visibly separates movement, inventory, and build-break domain responsibilities.
private_harness_notes:
  - preserve run artifacts
  - run self-alignment turns before tools
  - update capability memory
---

# Product Requirements

Create a voxel experiment with:

- block terrain and a selected block palette
- movement state exposed through GameHost
- build.place.request and block.break.request command traces
- recent domain events visible through GameHost.getState()
- concise public UI focused on gameplay and domain contracts
- no public control-plane metadata

The renderer presents blocks and state only. Domain concepts own build, break, movement, inventory, and replay-safe command meaning.
