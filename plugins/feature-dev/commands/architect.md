---
description: Design architecture for a feature or component — produces a complete implementation blueprint with files, data flow, and build sequence
argument-hint: <feature or component> [--minimal | --clean | --pragmatic]
---

Spawn a `feature-dev:code-architect` agent with this task:

"$ARGUMENTS"

After the agent completes, present the blueprint and ask: proceed to implementation, refine further, or compare against an alternative approach?

***

**Approach flags** (optional — append to your description):

- `--minimal` — smallest footprint, maximum reuse of existing abstractions; prefer this for low-risk additions to stable code
- `--clean` — prioritises maintainability and elegant new abstractions; accept more new code; prefer this for long-lived, heavily-modified areas
- `--pragmatic` — balances speed and quality; good default for most features

If no flag is provided, the agent picks the approach that best fits the codebase.
