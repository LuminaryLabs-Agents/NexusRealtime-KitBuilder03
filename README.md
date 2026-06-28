# NexusRealtime-KitBuilder03

`NexusRealtime-KitBuilder03` is a focused builder workspace for generating, refining, and packaging NexusRealtime-compatible kits before they are promoted into the wider NexusRealtime kit ecosystem.

This repository is part of the KitBuilder lane, not the stable NexusRealtime runtime itself.

## Role in the NexusRealtime workflow

The intended flow is:

```txt
KitBuilder01 / KitBuilder02 / KitBuilder03
  -> NexusRealtime-ProtoKits
  -> NexusRealtime
  -> NexusRealtime-Experiments
```

KitBuilder03 should be treated as an experimental kit-building repo used to test structure, prompts, generated files, and promotion rules before anything becomes canonical.

## What belongs here

This repo is appropriate for:

- kit-builder prompts and planning documents
- draft kit manifests
- generated or hand-authored kit candidates
- validation scripts for kit shape and packaging
- examples that prove a kit can be consumed later by ProtoKits or Experiments

## What does not belong here

This repo should not be used as:

- the stable NexusRealtime runtime
- the final ProtoKits registry
- the public Experiments gallery
- a place to directly change production game behavior

## Promotion rule

A kit should only move forward from this repo when it has:

- a clear folder boundary
- a readable README or kit note
- a manifest or install contract
- a small validation path
- no hidden dependency on unrelated local files

## Current status

This README was added as a repository access and push test, and to make the repo purpose clearer for future work.
