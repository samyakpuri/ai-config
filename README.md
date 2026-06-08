# ai-config

Personal Claude Code configuration — global rules, skills, and plugins deployed across all projects via `deploy.ps1`.

## Structure

```
ai-config/
├── global/
│   ├── CLAUDE.md               # Global instructions (loaded by all projects)
│   └── rules/
│       ├── behavior.instructions.md
│       └── coding.instructions.md
├── skills/
│   ├── commit/                 # /commit — multi-commit workflow with Conventional Commits
│   └── handoff/                # /handoff — write a HANDOFF.md for session continuity
├── plugins/
│   ├── feature-dev/            # TDD-first feature development (explore → design → implement → review)
│   ├── test-forge/             # Multi-language test generation (integration, property, contract)
│   └── requirements-decompose/ # Requirements decomposition — SYS/FW/SW/UI/API/COMP layers with baseline diff
├── conventions/
│   └── commit.md               # Commit message conventions reference
└── deploy.ps1                  # Symlinks config and registers plugins into ~/.claude
```

## Deploy

```powershell
.\deploy.ps1
```

Symlinks `global/CLAUDE.md` into `~/.claude/CLAUDE.md`, links each skill into `~/.claude/skills/`, and registers each plugin into `~/.claude/plugins/`. Requires Developer Mode (symlinks) or will fall back to junctions.

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `/commit` | `/commit` | Commits staged/unstaged changes as multiple logical units following Conventional Commits |
| `/handoff` | `/handoff`, "wrap up", "I'm done for today" | Writes a HANDOFF.md so the next session can resume without re-deriving state |

## Plugins

| Plugin | Skill | Description |
|--------|-------|-------------|
| `feature-dev` | `/feature-dev` | 8-phase TDD workflow: parallel exploration, architecture design, implementation, review |
| `test-forge` | `/add-tests` | Generates integration, property, and contract tests for Python, C, and C++ |
| `requirements-decompose` | `/req-decompose` | Decomposes product docs into structured SYS/FW/SW/UI/API/COMP requirements with traceability; supports `--baseline` for delta analysis |
