# Prompt File Format v001

Prompt files should separate public product requirements from private harness notes.

Use frontmatter:

```md
---
mode: kit-builder
public_title: DSK Bubble Kit Builder
public_goal: Build a browser tool for designing NexusRealtime Domain Service Kits.
private_harness_notes:
  - preserve run artifacts
  - run deterministic checks
  - update capability ledger
---

# Product Requirements

Create:
- domain bubble editor
- owned state panel
- commands and events panel
- idempotency keys panel
- sequence and gate view
- debug host panel
```

Only `public_title`, `public_goal`, and product requirements should appear in generated public apps or launcher metadata. Private notes stay in run artifacts and ledgers.
