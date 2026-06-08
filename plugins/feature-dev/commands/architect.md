---
description: Design architecture for a feature or component — produces a complete implementation blueprint with files, data flow, and build sequence
argument-hint: <feature or component> [--minimal | --clean | --pragmatic]
---

Perform a complete architecture analysis and design for:

"$ARGUMENTS"

**Approach flags** (optional):
- `--minimal` — smallest footprint, maximum reuse of existing abstractions
- `--clean` — prioritises maintainability and elegant new abstractions; accepts more new code
- `--pragmatic` — balances speed and quality; good default

If no flag is given, pick the approach that best fits the codebase and state your reasoning.

---

## Process

### 1. Analyse existing patterns

Use `mcp__semble__search` and `mcp__semble__find_related` as the primary exploration tools; fall back to Glob, Grep, LS, and Read only when semble is unavailable:
- Find similar features and trace their implementation end to end
- Map module boundaries, abstraction layers, and extension points relevant to this area
- Identify testing patterns, naming conventions, and any architectural constraints
- Read CLAUDE.md guidelines if present
- Surface 5–10 key files that are essential to understanding this area

### 2. Design the architecture

Make decisive choices within the selected approach. Ensure integration with existing code. Design for testability and maintainability within the approach's trade-offs.

### 3. Deliver the blueprint

- **Approach summary** — one paragraph: philosophy, key trade-offs
- **Patterns & conventions found** — existing patterns with `file:line` references, similar features, key abstractions
- **Component design** — each component: file path, responsibilities, dependencies, interfaces
- **Implementation map** — specific files to create or modify, with detailed change descriptions
- **Data flow** — complete flow from entry points through transformations to outputs
- **Build sequence** — phased implementation checklist
- **Critical details** — error handling, state management, testing approach, performance, security

Be specific and actionable: file paths, function names, concrete steps.

---

After completing the blueprint, ask: **proceed to implementation, refine further, or compare against an alternative approach?**
