---
name: commit
description: Analyze staged and unstaged changes and commit them as logical units using Conventional Commits style. Use this skill whenever the user asks to commit, stage, or check in changes — even for a simple "commit my changes" or "commit everything".
disable-model-invocation: true
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), mcp_gitkraken_git_add_or_commit, mcp_gitkraken_git_status, mcp_gitkraken_git_log_or_diff
---

## Current State

Run these commands via Bash to gather state before proceeding:

- `git branch --show-current`
- `git status --short`
- `git log --oneline -5`
- `git diff`
- `git diff --cached`

## Before staging

Inspect every untracked file (`??` in status) before staging anything:
- Is this a session artefact (handoff doc, plan, scratch note, test-plan)? **Do not commit it.**
- Is this a build output, IDE file, or ignored file that slipped through? **Do not commit it.**
- Only stage files that are intentional, reviewable changes to the codebase.

If any untracked files are ambiguous, **list them and ask the user** before proceeding.

Also check for logical dependencies between files before deciding what to stage:
- If file A deletes or removes something that file B now provides, they must be committed together or in the right order — staging the deletion without the addition would break the working tree.
- If a config or loader file references a new file that isn't being committed yet, flag it to the user rather than staging the reference without the target.

## Task

Analyze every change (staged and unstaged) and commit them as **multiple logical units** — one commit per coherent concern. If all changes belong to a single concern, make one commit.

Use **Conventional Commits** style without a scope in parentheses.

### Format

```
type: short imperative summary

Body explaining what changed and why. Wrap lines at 72 characters.
```

### Allowed types

| type        | use for |
|-------------|---------|
| `feat:`     | new feature or capability |
| `fix:`      | bug fix |
| `test:`     | adding or updating tests |
| `chore:`    | maintenance — configs, tooling, removing files |
| `refactor:` | restructuring with no behaviour change |
| `docs:`     | documentation only |
| `style:`    | formatting, whitespace — no logic change |
| `perf:`     | performance improvement |

### Rules

- Subject line: imperative mood ("add X", not "added X"), ≤72 chars, no trailing period, no scope in parentheses
- Body: include a body whenever the subject alone doesn't explain *why* the change was made — which is most of the time. Wrap at 72 chars.

### Grouping strategy

- Files that serve the same purpose belong in the same commit
- Never mix types in one commit (a `feat:` and a `chore:` are separate)
- For **corrective** changes (bug fix, coverage gap, refactor): source and tests go in
  the same commit — the fix is meaningless without the test proving it
- For **additive** changes (new module, new feature, new method on an existing class):
  source in a `feat:` commit first, tests in a follow-up `test:` commit — the
  implementation should be reviewable independently of the test strategy
- Exception: if the additive test suite is trivial (<~20 lines, one test function),
  combining is acceptable
- Config/tooling changes unrelated to the feature are their own `chore:` commit
- Each commit must be independently reviewable and revertable — a reviewer should be able to understand and approve it without reading adjacent commits
- If multiple files each target a different module or concern, split them one commit per module/concern regardless of file type (source, test, config)

### Commit message quality

Subject line (≤72 chars, imperative mood, no trailing period):
- Describe **what** changed and **why** — not the task name, sprint, or phase number
- Bad:  `test: close 18 missing coverage lines — phase 1`
- Good: `test: cover AsyncSerialBackend import guard, close error, and flush timeout`
- Append the Azure DevOps work item ID at the end of the subject when one exists:
  `test: cover AsyncSerialBackend import guard AB#4521`
- Never use planning-vocabulary in the subject: phase numbers, sprint names,
  test-plan section labels (e.g. "phase 0", "p1", "phase 1 coverage")

Body (blank line after subject):
- Explain the *reason* for the change if the subject alone is insufficient
- List specific behaviours covered, decisions made, or alternatives rejected

### Execution

For each commit group in sequence:
1. Stage only the files for this commit: `git add <file1> <file2> ...`
   - If a single file contains changes that belong to different commits (e.g., two independent edits in the same file), use `git add -p <file>` to stage only the relevant hunks.
2. Commit with the full message using a multiline format appropriate for the shell

Confirm the proposed grouping with the user **before executing** if:
- Any untracked files (`??`) are being staged, OR
- The grouping involves more than 5 commits

Otherwise execute all groups in a single response without asking.

Never add `Co-authored-by:` trailers or any AI attribution lines to commit messages.

### Merge commits

| Merge type | Message |
|---|---|
| Sync merge (pulling `main` into your branch mid-work) | Keep the default `Merge branch '...'` — these are noise |
| Integration merge (landing a completed feature/fix into `main`) | Use the dominant type with a body summarising what landed |

Integration merge example:
```
feat: add user authentication

Merged from feature/auth. Adds OAuth2 login, session management,
and protected route middleware.
```
