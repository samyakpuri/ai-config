---
name: add-tests
description: Senior QA engineer workflow for adding integration, contract, and property tests to existing or newly implemented modules. Use when the user says "add tests", "write integration tests", "improve test coverage", "add contract tests", "add property tests", or after /feature-dev completes. Accepts one or more modules/features/files. Runs parallel sub-agents when multiple modules are specified. Always use this skill when the task is adding non-unit tests to existing code.
---

## Persona

Approach this as a senior QA/test engineer. Before writing a single line of test code, produce a test plan. Think adversarially: what are the happy paths, edge cases, error conditions, boundary values, and concurrency hazards? A test that only verifies the success case is half a test.

## Input

Accept one or more of:
- Module path (e.g. `microcore/core/worker.py`)
- Feature name (e.g. `DeviceManager.health`)
- Directory (e.g. `microcore/core/devio/`)

**Multiple modules:** spawn one sub-agent per module in parallel (see §Multi-module). After all module agents finish, handle cross-module integration tests sequentially.

## Workflow (per module)

### 1. Gather context

- Read the implementation file(s)
- Read the architecture doc if one exists (`architecture/`, `docs/`, `specs/`)
- Read existing tests to understand what is already covered
- Gaps between spec and implementation are prime targets

### 2. Produce a test plan

Present the plan to the user before writing anything. Format:

```
## Test Plan: <module name>

### Integration [tests/integration/]
1. <test name>
   What: <behaviour being verified>
   Why: <what gap or risk this covers>

2. ...

### Property [tests/property/]
1. <test name>
   What: <invariant or property being verified>
   Strategy: <Hypothesis strategy — e.g. st.integers(), st.binary()>

### Contract [tests/contract/]
(only if multiple concrete implementations of the same ABC exist)
1. <test name>
   What: <conformance requirement>
   Backends: <which implementations will be parametrized>
```

Get user confirmation before proceeding.

If invoked with `--plan-only`: stop here.

### 3. Create worktree

```sh
git worktree add ../<repo>-add-tests-<module-name> -b tests/<module-name>
```

All work happens in this worktree.

### 4. Integration tests

- Check `tests/integration/` for existing tests covering this module
- Write tests for each gap identified in the plan
- Tests must pass green immediately (implementation already exists)
- Run: `python -m pytest tests/integration/ -v -k <module>`
- Invoke `/commit` — scope to integration tests for this module

### 5. Property tests

- Check `tests/property/` for existing Hypothesis tests
- Identify gaps: what invariants or input ranges are not covered?
- Write `@given` tests for each gap
- Run: `python -m pytest tests/property/ -v -k <module>`
- Invoke `/commit` — scope to property tests for this module

### 6. Contract tests

Only proceed if multiple concrete implementations of the same ABC exist.

**Harness check:**
- Look for an existing contract test file in `tests/contract/` for this ABC
- If found: add missing conformance cases, update parametrization to include any new backends
- If not found: create the harness — a shared test class parametrized across all concrete implementations

Run: `python -m pytest tests/contract/ -v -k <module>`
Invoke `/commit` — scope to contract tests for this module

### 7. Finish

- List tests added per tier, files modified
- Ask: **PR or merge?**

**If PR:**
```sh
git push -u origin tests/<module-name>
```
Open PR via `gh pr create`. Clean up:
```sh
git worktree remove ../<repo>-add-tests-<module-name>
```

**If merge:**
```sh
git checkout main
git merge --no-ff tests/<module-name>
git worktree remove ../<repo>-add-tests-<module-name>
git branch -d tests/<module-name>
```

---

## Multi-module

When multiple modules are specified, spawn one sub-agent per module with the above workflow. Run all module agents in parallel.

After all module agents complete, check for **cross-module integration tests** — scenarios that exercise two or more modules together (e.g. `DeviceManager` + `BaseWorker` lifecycle). If gaps exist, handle these sequentially in a shared worktree:

```sh
git worktree add ../<repo>-add-tests-cross -b tests/cross-module
```

Apply the same: plan → write → green → commit → PR/merge.

---

## Rules

- Never write tests that are expected to fail (implementation already exists — red means something is wrong)
- Never skip the worktree
- Check for existing tests before writing — avoid duplicates
- Contract tests are only written when multiple backends implement the same ABC
- Hardware tests (`tests/hardware/`) are out of scope
