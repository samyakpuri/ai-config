---
name: feature-dev
description: This skill should be used when the user asks to implement, build, or develop a feature, starts work on a named capability ("start work on X"), or provides a spec or requirements document. It orchestrates a TDD workflow in an isolated git worktree — parallel codebase exploration, requirement clarification, architecture design with trade-off options, sequential sub-feature TDD loop (failing tests → implementation → passing tests → commit), and parallel quality review. Supports --plan-only to stop after the confirmed sub-feature plan without creating a worktree or writing any code.
argument-hint: Optional feature description or spec
---

## Dependencies

Sub-agents (same plugin): `feature-dev:code-explorer`, `feature-dev:code-architect`, `feature-dev:code-reviewer`

Optional skills (use if available):
- `/commit` (`skills/commit/SKILL.md`) — invoked per sub-feature in the TDD loop; falls back to a manual `git add` + `git commit`
- `/add-tests` (`skills/add-tests/SKILL.md`) — suggested after feature completion for integration/contract coverage; falls back to a manual reminder

---

## Role

Act as a senior software engineer throughout this workflow — make opinionated design decisions, push back on vague requirements, prefer simple and idiomatic solutions over clever ones, and flag anything that smells like tech debt before it lands.

## Workflow

### 0. Setup

Use TodoWrite to create a task list covering all phases:

- Gather context
- Clarifying questions
- Architecture design
- Plan sub-features
- Create worktree
- TDD loop (expand with one task per sub-feature after planning)
- Quality review
- Finish

Feature request: `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask the user to describe the feature before proceeding.

---

### 1. Gather context

Launch 2–3 `feature-dev:code-explorer` agents in parallel, each targeting a different angle:

- **Similar features** — find existing features that resemble what's being built; trace their implementation end to end
- **Architecture** — map abstractions, data flow, and extension points relevant to the feature area
- **Testing and conventions** — identify testing patterns, naming conventions, and any UX/API patterns in use

Each agent should return a list of 5–10 key files. After agents complete, read those files before proceeding — the goal is to build a real picture of the codebase, not just skim surface-level docs.

Also check for feature docs in `architecture/`, `docs/`, `specs/`, and any `*.md` matching the feature name.

Mark **Gather context** done.

---

### 2. Clarifying questions

Review the codebase findings and the feature request together. Identify every underspecified aspect before committing to a design:

- Edge cases and error handling
- Integration points with existing code
- Scope boundaries — what's in, what's explicitly out
- Backward compatibility requirements
- Performance or security considerations
- Design preferences where the codebase shows multiple patterns

Present all questions in a clear numbered list. Wait for answers before proceeding to architecture.

If the user says "whatever you think is best", state your recommendation explicitly and get confirmation.

Mark **Clarifying questions** done.

---

### 3. Architecture design

Launch 2–3 `feature-dev:code-architect` agents in parallel with different focuses:

- **Minimal changes** — smallest footprint, maximum reuse of existing abstractions
- **Clean architecture** — prioritises maintainability and elegant abstractions, accepts more new code
- **Pragmatic balance** — optimises for speed and quality together

After agents complete:

1. Summarise each approach in 2–3 sentences
2. Show a trade-offs comparison (complexity, reuse, maintainability, risk)
3. Give a recommendation with reasoning — consider scope, urgency, team context
4. Ask the user which approach to use

Wait for explicit approval before continuing.

Mark **Architecture design** done.

---

### 4. Plan sub-features

Break the feature into an ordered list where each sub-feature:
- Has a single, testable behaviour
- Builds on the previous one
- Can be committed independently
- Has an assigned test tier (`unit` or `property` only — integration/contract tests are added separately after the feature is complete via `/add-tests`):
  - `unit` — pure logic, no I/O, no event loop where avoidable
  - `property` — Hypothesis-based, generative input testing

Present the list to the user in this format and get confirmation before proceeding:

```
1. <sub-feature name> [unit]
   What: <one-line description of the behaviour>
   Test: <what the test asserts>

2. <sub-feature name> [property]
   ...
```

If invoked with `--plan-only`: stop here after the user confirms the plan. Do not create a worktree or write any code.

After confirmation, add one TodoWrite task per sub-feature to the task list, then mark **Plan sub-features** done.

---

### 5. Create worktree

```sh
git worktree add ../<repo>-feature-<name> -b feature/<name>
```

All work happens in this worktree. Do not touch the main working tree.

Mark **Create worktree** done.

---

### 6. TDD loop — one sub-feature at a time

Repeat for each sub-feature in order:

**Red**
- Write the minimum failing tests that define the sub-feature's behaviour, in the tier assigned in the plan
- Run the tests and confirm they fail for the right reason (not import errors, not wrong assertion message)

**Green**
- Implement only enough code to make the failing tests pass
- Only touch files directly required by this sub-feature — do not refactor, clean up, or modify anything outside its scope
- Run tests again — if still failing, fix and re-run
- Do not move on until all tests for this sub-feature are green

**Commit**
- If `/commit` skill is available, invoke it; otherwise run `git add -p` (stage only this sub-feature's files) and `git commit` with a concise message scoped to this sub-feature
- Scope the commit to this sub-feature only

**Review**
- Show the user the diff (`git diff HEAD~1`) and ask for approval
- If approved: mark this sub-feature's task done and proceed to the next
- If rejected: address feedback, re-run tests, re-commit

Only after approval, move to the next sub-feature.

**If stuck (tests won't go green)**

After 3 failed fix attempts, stop and surface to the user:

1. What was tried and why it didn't work
2. Options:
   - Re-examine the test — is it over-specified or testing the wrong thing?
   - Shrink the sub-feature — split into a smaller, provably passable step
   - Skip and note — move on with a TODO comment, revisit at end
   - Ask the user for direction

---

### 7. Quality review

After all sub-features are committed and approved, launch 3 `feature-dev:code-reviewer` agents in parallel:

- **Simplicity/DRY/elegance** — duplication, unnecessary complexity, abstraction mismatches
- **Bugs and correctness** — logic errors, edge cases, unsafe assumptions
- **Conventions and architecture** — adherence to project patterns, naming, structure

Consolidate the findings. Identify the highest-severity issues worth fixing now versus later. Present to the user and ask: fix now, note for later, or proceed as-is?

Address issues based on their decision, re-running tests after any fixes.

Mark **Quality review** done.

---

### 8. Finish

Summarise what was delivered:

- Sub-features implemented and their test files
- Any deviations from the original plan and why
- Key architecture decisions made
- Suggested next steps (e.g., invoke `/add-tests` if available, or manually add integration/contract tests)

Then ask: **PR or merge?**

**If PR:**
```sh
git push -u origin feature/<name>
```
Open the PR via `gh pr create` or ask the user to open it. Clean up the worktree:
```sh
git worktree remove ../<repo>-feature-<name>
```

**If merge:**

Ask the user: `--no-ff` (default) or `--squash`?

- `--no-ff` preserves the per-sub-feature commit history on main — each TDD step stays bisectable and revertable individually. Recommended default.
- `--squash` collapses all sub-feature commits into one — cleaner main branch story but loses the granular audit trail.

```sh
# --no-ff (default)
git checkout main
git merge --no-ff feature/<name>

# --squash (if preferred)
git checkout main
git merge --squash feature/<name>
git commit  # write a summary commit message
```

Then clean up:
```sh
git worktree remove ../<repo>-feature-<name>
git branch -d feature/<name>
```

Mark **Finish** done.

---

## Rules

- Never write tests for more than one sub-feature at a time
- Never implement before tests exist and are confirmed failing
- Never commit with failing tests
- Never skip the worktree — every feature gets its own branch and worktree
- Never expand scope beyond the confirmed plan — if something extra seems useful, note it and move on
- Never touch files outside the current sub-feature's scope, even to clean up or refactor
