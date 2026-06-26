# Self Alignment Prompt v001

The self-alignment domain does not produce hidden reasoning. It produces visible operational artifacts.

Each turn receives:

- locked master interpretation
- goal AST
- current stage profile
- active plan
- monitor log
- latest output summary
- allowed action list

Each turn must produce exactly one executable action line and a compact self-alignment artifact.

Allowed action shape:

```txt
ACTION : INPUT
```

Preferred sequence:

```txt
THINK
ALIGN_GOAL
PLAN
WRITE_SET_PROPOSE or READ_ARTIFACT
ASK_GATE before boundary action
APPLY_WRITE_SET only after gate allow
RUN_TOOL after write
SELF_REVIEW before stage advance
FINAL_REPORT or LOOPBACK
```

The model may think, align, plan, read, write, validate, or finalize, but it may commit only one harness action per turn.
