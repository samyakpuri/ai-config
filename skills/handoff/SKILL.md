---
name: handoff
description: Write or update a HANDOFF.md so the next agent or session can resume without re-deriving state. Use whenever the user says "wrap up", "I'm done for today", "save my progress", "write a summary", "before I go", or when context is approaching its limit.
allowed-tools: Read, Glob, Write, Bash(git log:*), Bash(git status:*), Bash(git diff:*)
---

Write or update a handoff document so the next agent with fresh context can continue this work.

## Target file

1. **Use the folder the user names** (e.g. "in software folder" → `software/HANDOFF.md`).
2. If no folder is named, run `git rev-parse --show-toplevel` to find the git root of
   the project actually being worked on. Use that as the target folder.
3. If git returns multiple candidates (e.g. you are operating across multiple repos),
   or if `git rev-parse` fails (no repo), ask the user which folder before writing.
   Do not guess.
4. **Never use the Claude Code primary working directory as a fallback** — it is often
   a config or tooling repo, not the project the user is handing off.
5. **Never merge a HANDOFF across sibling folders** without explicit confirmation —
   nearby `HANDOFF.md` / `HANDOFF2.md` files in other roots are usually local
   working notes, not duplicates to consolidate.

## Gather context first

Before writing anything, reconstruct what happened this session:

- Run `git log --oneline -10` to see what was committed
- Run `git status` and `git diff` for uncommitted work
- Scan the conversation for decisions made, blockers hit, and explicit user instructions

If git history is sparse or absent (no repo, nothing committed yet), fall back to scanning recently modified files with Glob and rely on the conversation history instead.

This gives you the raw material — write from that, not from memory.

## Amend or rewrite?

- **Amend** if the existing handoff is recent and most sections are still accurate. Add a dated **"Session Update — YYYY-MM-DD"** block at the top summarising what changed, then update only the stale sections (typically *Next Steps*, *Repo State*, *Reference Files*).
- **Rewrite** if the *Next Steps* are all completed and *Repo State* is more than a few commits behind — a full rewrite serves the reader better than a heavily patched document.
- If creating fresh: use the section list below.

If handing off to a different agent (not resuming yourself) — a subagent, Copilot → Claude Code, etc. — they have zero conversation history. Be more explicit in *Open Questions* and *Key Decisions* than you would for a personal session resume; they cannot infer intent from context you haven't written down.

After writing, post a short summary in chat **and** end the reply with exactly:
```
Resume with: <absolute path to the HANDOFF.md file you just wrote>
```

The path in `Resume with:` **must be the exact absolute path passed to the Write tool** —
copy it from the write operation, do not recompute it. This prevents the resume path from
pointing to a different HANDOFF.md than the one that was written.

## Required sections (in order)

| Section | Purpose |
|---|---|
| **Goal** | One paragraph. What the project is trying to accomplish. Stable across sessions *(update only when scope genuinely changes)*. |
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
