---
name: add-tests
description: This skill should be used when the user asks to add, write, or improve tests for an existing module or newly implemented feature — e.g. "add tests", "write integration tests", "test this module", "improve test coverage", "add contract tests", "add property tests", or "write a test suite for X". Covers Python, C, and C++ including PlatformIO embedded projects. Accepts one or more module paths, feature names, or directories. Also suggested after /feature-dev completes.
argument-hint: "<module-path> [module-path...]"
---

## Dependencies

Sub-agents (same plugin): `test-forge:scaffold-tests`, `test-forge:integration-tests`, `test-forge:property-tests`, `test-forge:contract-tests`

Optional skills:
- `/commit` — invoked after each test tier; falls back to manual `git add` + `git commit`

---

## Role

Act as a senior QA/test engineer throughout. Before spawning any agent, produce a test plan. Think adversarially: happy paths, edge cases, error conditions, boundary values, concurrency hazards. A test that only verifies success is half a test.

## Input

Accept one or more of:
- Module path (e.g. `src/worker.py`, `lib/sensor/sensor.c`)
- Feature name (e.g. `DeviceManager.health`)
- Directory (e.g. `microcore/core/devio/`)

**Multiple modules:** spawn one set of agents per module in parallel (§Multi-module). After all module agents finish, handle cross-module integration tests sequentially.

---

## Workflow

### 1. Detect language stack

Examine the project root:
- `platformio.ini` present → **PlatformIO** (C/C++ embedded)
- `setup.py` / `pyproject.toml` / `requirements.txt` present → **Python**
- `CMakeLists.txt` + `.cpp`/`.c` files present → **bare C/C++**

If mixed (e.g. Python + C extension), note both and apply rules per file type.

### 2. Check test infrastructure

**Python:** `tests/` dir, `conftest.py`, pytest config
**PlatformIO:** `test/<lib_name>/platformio.ini` with `native_test` env, `extra_configs` in root `platformio.ini`
**Bare C/C++:** `tests/CMakeLists.txt`, framework setup (gtest / Catch2 / Unity)

If infrastructure is missing or incomplete → run `test-forge:scaffold-tests` before proceeding. Pass it the detected stack, lib_name (for PlatformIO), and module paths.

### 3. Produce test plan

Read the implementation file(s) and any existing tests. Present the consolidated plan before writing anything:

```
## Test Plan: <module name>

### Integration [tests/integration/]
1. <test name>
   What: <behaviour being verified>
   Why: <gap or risk this covers>

### Property [tests/property/]
1. <test name>
   What: <invariant or property>
   Strategy: <Hypothesis @given / RapidCheck / libFuzzer approach>

### Contract [tests/contract/]
(only if multiple concrete implementations of the same interface exist)
1. <test name>
   What: <conformance requirement>
   Implementations: <which ones>
```

Get user confirmation before proceeding. If invoked with `--plan-only`: stop here.

### 4. Create worktree

```sh
git worktree add ../<repo>-add-tests-<module-name> -b tests/<module-name>
```

All work happens in this worktree.

### 5. Dispatch agents (per module)

Launch in parallel:
- `test-forge:integration-tests` — integration tests for this module
- `test-forge:property-tests` — property/fuzz tests for this module
- `test-forge:contract-tests` — contract tests (omit unless the module exposes an interface or abstract base class that has two or more concrete implementations in the codebase)

Pass each agent: `module_path`, `stack`, `lib_name` (PlatformIO), the relevant test plan section, and `worktree_path`.

### 6. Finish

After all module agents complete, check for **cross-module integration tests** — scenarios that exercise two or more modules together. If gaps exist, handle sequentially in a shared worktree:

```sh
git worktree add ../<repo>-add-tests-cross -b tests/cross-module
```

List all tests added per tier and file. Ask: **PR or merge?**

Repeat the following block for **each module worktree/branch** created in §4 (one per module):

**If PR:**
```sh
git push -u origin tests/<module-name>
gh pr create
git worktree remove ../<repo>-add-tests-<module-name>
```

**If merge:**
```sh
git checkout main
git merge --no-ff tests/<module-name>
git worktree remove ../<repo>-add-tests-<module-name>
git branch -d tests/<module-name>
```

If a cross-module worktree was created (`tests/cross-module`), clean it up last.

---

## Rules

- Never write tests expected to fail — implementation already exists; red means something is wrong
- Never skip the worktree
- Check for existing tests before writing — no duplicates
- Contract tests only when multiple implementations of the same interface exist
- `tests/hardware/` is out of scope
- PlatformIO property tests target `native_test` env only — never embedded hardware
