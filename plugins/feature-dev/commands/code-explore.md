---
description: Deeply explore a codebase area — traces execution paths, maps architecture layers, identifies patterns and dependencies
argument-hint: <feature, area, or component to explore>
---

Deeply explore and analyse this codebase area:

"$ARGUMENTS"

---

## Process

Use `mcp__semble__search` and `mcp__semble__find_related` as the primary exploration tools; fall back to Glob, Grep, LS, and Read only when semble is unavailable:

1. **Find relevant files** — search for the named feature, class, function, or module; include related tests, docs, and config
2. **Trace execution paths** — follow the code end to end: entry point → processing → output; note every branch and side effect
3. **Map architecture layers** — identify abstraction boundaries, module ownership, and where this area fits in the larger system
4. **Identify patterns and conventions** — naming, error handling, testing style, data flow patterns in use
5. **Map dependencies** — what this area depends on, what depends on it, any circular or surprising couplings

---

## Output

- **Essential files** (5–10): each with a one-line note explaining why it's key
- **Architecture summary**: layers, boundaries, key abstractions
- **Execution path trace**: entry point → processing steps → output, with file:line references
- **Patterns and conventions**: what to follow when modifying this area
- **Dependency map**: inbound and outbound dependencies worth knowing
- **Key insights or concerns**: anything surprising, fragile, or worth flagging before making changes
