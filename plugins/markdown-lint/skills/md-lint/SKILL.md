---
name: md-lint
description: >-
  This skill should be used when the user asks to "fix markdown lint errors", "fix markdownlint issues",
  "clean up this markdown", "lint this markdown file", "check markdown formatting", or "what's wrong with
  this markdown". Also activates automatically when the markdown-lint PostToolUse hook feeds lint violations
  back after writing or editing a .md file. Provides specific, actionable fix suggestions for each
  markdownlint rule violation without auto-applying changes.
version: 0.1.0
---

# Markdown Lint Skill

Handles markdownlint violations for `.md` files. Always present fixes as suggestions — do not silently rewrite
content without showing what changes and why.

## markdownlint Output Format

```
file.md:10:1 MD022/headings-should-be-surrounded-by-blank-lines Headings should be surrounded by blank lines [Context: "## Section"]
file.md:23 MD009/no-trailing-spaces Trailing spaces [Expected: 0; Actual: 2]
```

Format: `file:line[:col] RULE_ID/rule-name Description [details]`

Parse each line to identify: which line is affected, which rule triggered, and what the violation is.

## Suggesting Fixes

For each violation, surface:
1. **Line number** and the offending content — read the file to retrieve the offending line before presenting a fix
2. **What the rule requires** (one sentence)
3. **The exact fix** — show the before/after diff or the corrected text

Group violations by type when there are many of the same rule. Offer to apply all fixes of the same type at once.

Never auto-apply without stating what will change. Use phrasing like:
- "Line 10 is missing a blank line before the heading — want me to add it?"
- "5 lines have trailing spaces (lines 4, 7, 12, 18, 23) — fix all?"
- "MD013: Lines 34 and 67 exceed the configured line length — here's how to wrap them."

## Configuration Awareness

Check whether a `.markdownlint.json` (or `.jsonc`/`.yaml`/`.yml`) exists at the project root.

- **Config present**: Rules and their settings come from the config. A rule disabled in config is not a violation even if the output shows it (the hook already passes the config to markdownlint, so the hook output is authoritative).
- **No config**: markdownlint defaults apply. Common defaults to be aware of: MD013 line-length defaults to 80 chars, MD041 requires H1 as first line.

If a user wants to suppress a rule permanently, suggest adding it to `.markdownlint.json`:
```json
{
  "MD013": false
}
```

Or to disable for a block inline:
```markdown
<!-- markdownlint-disable MD013 -->
long line here
<!-- markdownlint-enable MD013 -->
```

## Most Common Violations and Fixes

| Rule | Issue |
|------|-------|
| MD009 | Trailing spaces |
| MD010 | Hard tabs |
| MD012 | Multiple consecutive blank lines |
| MD013 | Line exceeds configured length |
| MD022 | No blank line around heading |
| MD031 | No blank line around fenced code block |
| MD032 | No blank line around list |
| MD034 | Bare URL not wrapped in angle brackets or link syntax |
| MD040 | Fenced code block missing language identifier |
| MD041 | First line is not an H1 heading |
| MD047 | File does not end with a single newline |

For fix patterns, see `references/rules.md`.

## Inline Disable Comments

When a violation is intentional (e.g. a long URL in MD013), suggest the narrowest disable scope:

```markdown
<!-- markdownlint-disable-next-line MD013 -->
https://very-long-url-that-exceeds-line-length.example.com/path/to/resource
```

