---
applyTo: "**"
---

# Coding

- Implement exactly what was asked — no extra features, no unsolicited refactors
- No comments unless the WHY is non-obvious (hidden constraint, workaround, subtle invariant)
- Use Doxygen/doctag-style comments (`@param`, `@return`, `@brief`, etc.) for public APIs and exported functions — no freeform prose comment blocks
- No defensive error handling for impossible cases — trust internal guarantees
- Prefer editing existing files over creating new ones
- No backwards-compatibility shims for removed code

# Code Exploration

- Prefer `mcp__semble__search` / `mcp__semble__find_related` over Grep, Glob, or Read when available
