# test-forge

Multi-language test generation — integration, property, and contract tests for Python, C, and C++ (including PlatformIO embedded).

## Skills

| Skill | Trigger |
|---|---|
| `add-tests` | "add tests", "write integration tests", "improve test coverage", "add contract tests", after `/feature-dev` |

## Agents

| Agent | Purpose |
|---|---|
| `scaffold-tests` | Create test infrastructure (dirs, config, stubs) |
| `integration-tests` | Write integration tests per module |
| `property-tests` | Write Hypothesis / RapidCheck property tests |
| `contract-tests` | Write conformance tests across multiple implementations |

## Language support

| Stack | Integration | Property | Contract |
|---|---|---|---|
| Python | pytest | Hypothesis | ABC parametrized fixture |
| PlatformIO (embedded) | Unity via `pio test -e native_test` | RapidCheck (if configured) | Function pointer / HAL pattern |
| Bare C++ | Google Test / Catch2 | RapidCheck / libFuzzer | Typed test suite |
| Bare C | Unity | libFuzzer / AFL | Function pointer table |

## PlatformIO convention

For library tests, the plugin creates `test/<lib_name>/platformio.ini` and patches the root `platformio.ini`:

```ini
[platformio]
extra_configs = test/<lib_name>/platformio.ini
```

## Installation

Run `deploy.ps1` from the repo root — it creates a junction from `skills/test-forge` → `plugins/test-forge`, registers the plugin in `installed_plugins.json`, and adds it to VS Code Copilot settings.

```powershell
.\deploy.ps1
```

Restart Claude Code and reload VS Code after running.
