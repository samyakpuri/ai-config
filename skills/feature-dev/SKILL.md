---
name: feature-dev
description: TDD feature development workflow in an isolated git worktree. Use when the user says "implement feature", "build feature", "develop feature", "start work on X", or hands you a spec/requirements doc. Reads architecture docs, plans sub-features, then implements each one sequentially: failing tests → implementation → passing tests → commit. Always use this skill when starting any non-trivial feature implementation. Supports --plan-only to stop after the confirmed sub-feature plan without creating a worktree or writing any code.
---

## Workflow

### 1. Gather context

- Check for feature docs in: `architecture/`, `docs/`, `specs/`, any `*.md` matching the feature name
- Read any relevant architecture spec before planning
- Ask the user to clarify anything ambiguous before proceeding

### 2. Plan sub-features

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

### 3. Create worktree

```sh
git worktree add ../<repo>-feature-<name> -b feature/<name>
```

All work happens in this worktree. Do not touch the main working tree.

### 4. TDD loop — one sub-feature at a time

Repeat for each sub-feature in order:

**Red**
- Write the minimum failing tests that define the sub-feature's behaviour, in the tier assigned in the plan
- Run the tests and confirm they fail for the right reason (not import errors, not wrong assertion message)

**Green**
- Implement only enough code to make the failing tests pass
- Run tests again — if still failing, fix and re-run
- Do not move on until all tests for this sub-feature are green

**Commit**
- Invoke the `/commit` skill
- Scope the commit to this sub-feature only

**Review**
- Show the user the diff (`git diff HEAD~1`) and ask for approval
- If approved: proceed to the next sub-feature
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

### 5. Finish

After all sub-features are committed and approved:

- List sub-features implemented, test files added/modified, any deviations from plan
- Ask: **PR or merge?**

**If PR:**
```sh
git push -u origin feature/<name>
```
Then open the PR (via `gh pr create` or ask the user to open it). Clean up the worktree:
```sh
git worktree remove ../<repo>-feature-<name>
```

**If merge:**
```sh
git checkout main
git merge --no-ff feature/<name>
git worktree remove ../<repo>-feature-<name>
git branch -d feature/<name>
```

## Rules

- Never write tests for more than one sub-feature at a time
- Never implement before tests exist and are confirmed failing
- Never commit with failing tests
- Never skip the worktree — every feature gets its own branch and worktree
