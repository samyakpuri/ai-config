---
name: md-lint
description: >-
  This skill should be used when the user asks to "fix markdown lint errors", "fix markdownlint issues",
  "clean up this markdown", "lint this markdown file", "check markdown formatting", or "what's wrong with
  this markdown". Also activates automatically when the markdown-lint PostToolUse hook feeds lint violations
  back after writing or editing a .md file. Applies all fixes and loops until the file is clean.
version: 0.2.0
---

# Markdown Lint Skill

Handles markdownlint violations for `.md` files. Fix all violations in one pass, then re-run markdownlint
to verify. Loop until clean or stuck.

## markdownlint Output Format

```
file.md:10:1 MD022/headings-should-be-surrounded-by-blank-lines Headings should be surrounded by blank lines [Context: "## Section"]
file.md:23 MD009/no-trailing-spaces Trailing spaces [Expected: 0; Actual: 2]
```

Format: `file:line[:col] RULE_ID/rule-name Description [details]`

Parse each line to identify: which line is affected, which rule triggered, and what the violation is.

## Fix Loop

1. Read the full violation list from the hook output.
2. Apply **all** fixes in a single edit — do not fix one violation and wait.
3. Re-run markdownlint on the file:
   ```
   npx --yes markdownlint-cli "<file_path>"
   ```
4. If violations remain, apply another round of fixes and re-run.
5. Repeat until the file is clean (exit 0) or until the **same violations appear twice in a row** (stuck).

### When stuck

A violation is stuck if it persists unchanged after a fix attempt. For each stuck rule:

1. **Explain why the auto-fix cannot resolve it** (e.g. ambiguous content, conflicting rules, intentional style).
2. **Offer two options**:
   - Apply a manual correction with user guidance
   - Suppress the rule in `.markdownlint.json`:
     ```json
     { "MD060": false }
     ```
3. Do not loop further on stuck rules — suppress or skip them, then continue fixing the rest.

## Applying Fixes

Fix all violations of all rules in one `Edit` call per file where possible. When multiple rules affect the
same lines, resolve them together. Do not make one edit per violation.

Read the file once before editing to get current line content — line numbers in markdownlint output shift
after edits, so resolve all changes against the original content.

## Configuration Awareness

Check whether a `.markdownlint.json` (or `.jsonc`/`.yaml`/`.yml`) exists at the project root.

- **Config present**: Rules and their settings come from the config. The hook already passes the config to
  markdownlint, so its output is authoritative.
- **No config**: markdownlint defaults apply. Common defaults: MD013 line-length = 80, MD041 requires H1
  as first line.

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
| MD060 | Table column style inconsistency |

For fix patterns, see `references/rules.md`.

## Inline Disable Comments

When a violation is intentional (e.g. a long URL in MD013), use the narrowest disable scope:

```markdown
<!-- markdownlint-disable-next-line MD013 -->
https://very-long-url-that-exceeds-line-length.example.com/path/to/resource
```
