# feature-dev

A TDD-first feature development workflow for Claude Code, with parallel codebase exploration, architecture design, and quality review agents.

## What it does

Runs a structured 8-phase workflow when you start implementing a feature:

1. **Gather context** — 2–3 parallel `code-explorer` agents map similar features, architecture, and testing patterns
2. **Clarifying questions** — surfaces every underspecified aspect before any design is committed
3. **Architecture design** — 2–3 parallel `code-architect` agents produce focused blueprints (minimal / clean / pragmatic); you pick one
4. **Plan sub-features** — breaks the feature into ordered, independently-commitable slices with assigned test tiers
5. **Create worktree** — all work happens on an isolated branch; main is never touched
6. **TDD loop** — for each sub-feature: write failing tests → implement → green → commit → user approval; escalates after 3 failed attempts
7. **Quality review** — 3 parallel `code-reviewer` agents (simplicity/DRY, bugs, conventions) consolidate findings
8. **Finish** — summary, then PR or merge (with `--no-ff` / `--squash` choice)

Supports `--plan-only` to stop after the confirmed sub-feature plan without creating a worktree or writing code.

## Installation

Run `deploy.ps1` from the repo root. It:

1. Creates a junction `skills/feature-dev` → `plugins/feature-dev` so Claude Code auto-loads the plugin as `feature-dev@skills-dir`
2. Registers the plugin in `~/.claude/plugins/installed_plugins.json` for VS Code Copilot resolution
3. Adds the plugin path to `chat.pluginLocations` in VS Code `settings.json`

```powershell
.\deploy.ps1
```

After running, restart Claude Code and reload VS Code.

## Usage

### Claude Code

```
/feature-dev Add rate limiting to the API
/feature-dev --plan-only Refactor the auth module
```

Standalone agent commands:

```
/feature-dev:code-explore authentication middleware
/feature-dev:architect user notification system --clean
```

### VS Code Copilot

The agents are available via the **agents picker** in Copilot Chat:

1. Open Chat (`Ctrl+Alt+I`)
2. Switch to **Agent** mode (dropdown at top of chat)
3. Select `code-explorer`, `code-architect`, or `code-reviewer` from the agents list
4. Type your query

The agents appear because this plugin's skills are injected into the session context via workspace instructions. They are not `@` chat participants — they are subagents routed by the Copilot orchestrator.

## Dependencies

The TDD loop (Phase 6) invokes the [`/commit` skill](../../skills/commit/SKILL.md) to commit each sub-feature. Ensure it is available in your Claude Code setup before running the full workflow.

## Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| `code-explorer` | Traces execution paths, maps architecture, identifies patterns | sonnet |
| `code-architect` | Produces implementation blueprints for a specific approach | sonnet |
| `code-reviewer` | Reviews for bugs, quality, and conventions (confidence ≥ 80 only) | inherit |

The explorer prefers `mcp__semble__search` for semantic queries when available, falling back to Grep/Glob.

## Repository

This plugin is part of [ai-config](https://github.com/samyakpuri/ai-config) — a personal Claude Code / VS Code Copilot configuration repository.

## Author

Samyak Puri

## License

See [LICENSE](LICENSE).
