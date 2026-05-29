# Commit Message Conventions

All commits use **Conventional Commits** style without a scope in parentheses.

## Format

```
type: short imperative summary

Body explaining what changed and why. Wrap lines at 72 characters.
Multiple paragraphs are fine when needed.
```

## Allowed Types

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

## Rules

- **Summary line**: imperative mood ("add X", not "added X"), ≤72 chars, no trailing period, no scope in parentheses
- **Body**: always required — explain the *what* and *why*, not the *how*; wrap at 72 chars

## Merge Commits

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
