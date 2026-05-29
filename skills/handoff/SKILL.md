---
name: handoff
description: Write or update a HANDOFF.md so the next agent (or a future you with fresh context) can resume this work without re-deriving the state. Invoke at end of session, before context compaction, or before handing off to another agent.
---

Write or update a handoff document so the next agent with fresh context can continue this work.

## When to invoke

- The user asks to "wrap up", "write a handoff", or "summarise for next time"
- Context is approaching the limit and work will continue in a new conversation
- Work is pausing mid-task and resumes later (today, tomorrow, next sprint)
- You are about to switch agents (Copilot ↔ Claude Code ↔ subagent)

## Target file

1. **Use the folder the user names** (e.g. "in software folder" → `software/HANDOFF.md`).
2. If no folder is named **and** the workspace has multiple roots, ask which folder
   before writing. Do not guess.
3. If a single-root workspace, use `<root>/HANDOFF.md`.
4. **Never merge a HANDOFF across sibling folders** without explicit confirmation —
   nearby `HANDOFF.md` / `HANDOFF2.md` files in other roots are usually local
   working notes, not duplicates to consolidate.

## Process

1. **Read the existing HANDOFF.md if it exists.** Preserve its structure and the
   reader's mental model. Do not rewrite a doc that already works — amend it.
2. If amending: add a dated **"Session Update — YYYY-MM-DD"** block at the top
   summarising what changed this session, then update only the sections rendered
   stale (typically *Next Steps*, *Repo State*, *Reference Files*).
3. If creating: use the section list below.
4. After writing, post a short summary in chat **and** end the reply with exactly:
   ```
   Resume with: <absolute path to HANDOFF.md>
   ```

## Required sections (in order)

| Section | Purpose |
|---|---|
| **Goal** | One paragraph. What the project is trying to accomplish. Stable across sessions. |
| **Repo State** | Branch, last commit SHA (and any merge SHA from this session), files touched, anything pushed. One block, scannable. |
| **Current Progress** | Checklist. Preserve prior items verbatim; mark new ones. |
| **Next Steps** | Ordered, actionable. Each item names the file or symbol to touch. No vague "continue work on X". |
| **Open Questions** | Things the next agent **must not assume** an answer to. Single most valuable section — fill it honestly even if short. |
| **Out of Scope** | Work the user explicitly deferred. Prevents the next agent from drifting back into it. |
| **How to Verify State** | One command (or short list) that proves where things stand: `git log --oneline -6`, `pytest -q`, `npm test`, etc. |

## Optional sections (include only when non-obvious)

- **What Worked** — only when a non-obvious approach succeeded and would be missed
- **What Didn't Work** — only when a real dead-end was hit; skip filler
- **Key Decisions** — when the session produced architectural choices that need to survive
- **Reference Files** — paths to code, specs, prior handoffs that informed the work

## Anti-patterns

- Filling *What Worked* with truisms ("reading the code first helped")
- Restating the *Goal* every session — it should be stable; touch it only when scope changes
- Writing *Next Steps* as a wish list — every item must be the next concrete action
- Quoting tool output dumps; summarise instead
- Pasting whole code blocks; link the file with `[path](path)` + line numbers
- Naming planning vocabulary (phase X, sprint Y) instead of the actual work
