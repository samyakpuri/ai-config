---
name: commit
description: Analyze all current changes (staged and unstaged) and split them into multiple logical git commits using Conventional Commits style. Use when committing work that spans multiple concerns.
disable-model-invocation: true
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
---

## Current State

- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Unstaged changes: !`git diff`
- Staged changes: !`git diff --cached`

## Task

Analyze every change (staged and unstaged) and commit them as **multiple logical units** — one commit per coherent concern. If all changes belong to a single concern, make one commit.

Follow the conventions in [conventions/commit.md](../../../conventions/commit.md).

### Grouping strategy

- Files that serve the same purpose belong in the same commit
- Never mix types in one commit (a `feat:` and a `chore:` are separate)
- Tests for a change can go in the same commit as the code, or a separate `test:` commit if the test suite is substantial
- Config/tooling changes unrelated to the feature are their own `chore:` commit

### Execution

For each commit group in sequence:
1. Stage only the files for this commit: `git add <file1> <file2> ...`
2. Commit with the full message using a multiline format appropriate for the shell

Do not ask for confirmation between commits. Execute all groups in a single response.

Never add `Co-authored-by:` trailers or any AI attribution lines to commit messages.
