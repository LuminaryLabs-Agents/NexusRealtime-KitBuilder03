# LiveHarnessV.01

LiveHarnessV.01 is the versioned harness root for NexusLiveLLM.

It follows the LEDGER operating model:

- Log every step.
- Explain decisions with evidence.
- Deterministically validate outputs.
- Gate repo writes through harness code.
- Externalize memory as JSON artifacts.
- Replay, review, and reconcile every run.

## First proof target

The first rapid-game proof creates a Three.js open-world exploration demo and publishes it under `docs/games/<run-id>-three-open-world/`.

## Main folders

- `state/` stores queue, run state, orchestration state, and active injections.
- `models/` stores model tier and budget configuration.
- `schemas/` stores JSON contracts.
- `prompts/` stores versioned prompt contracts.
- `tools/live_harness/` stores executable harness modules.
- `ledgers/` stores append-only JSONL logs.
- `runs/` stores per-run request, response, tool, reconcile, and review artifacts.
