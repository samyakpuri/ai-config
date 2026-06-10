# markdownlint Rule Reference

Full list of rules surfaced by `markdownlint-cli`. Each entry includes: rule ID, name, what it flags, and the fix pattern.

## Heading Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD001 | heading-increment | Heading levels skip (e.g. H1 → H3) | Change to sequential levels only (H1 → H2 → H3) |
| MD002 | first-heading-h1 | (deprecated, see MD041) | — |
| MD003 | heading-style | Mixed `#` ATX and `===` setext styles | Standardise to ATX (`#`) throughout |
| MD018 | no-missing-space-atx | `#Heading` with no space | Add space: `# Heading` |
| MD019 | no-multiple-space-atx | `#  Heading` with extra spaces | Single space after `#` |
| MD020 | no-missing-space-closed-atx | `#Heading#` closed ATX with no space | Add space: `# Heading #` |
| MD021 | no-multiple-space-closed-atx | `#  Heading  #` | Single space inside `#` |
| MD022 | blanks-around-headings | Heading not preceded and followed by blank line | Add blank line above and below |
| MD023 | heading-start-left | Heading indented with spaces | Move heading to column 0 |
| MD024 | no-duplicate-heading | Two headings with identical text (same or different levels) | Make headings unique or configure `siblings_only: true` |
| MD025 | single-title | More than one H1 | Use a single `# Title` at the top |
| MD026 | no-trailing-punctuation | Heading ends with `.`, `!`, `,` etc. | Remove trailing punctuation |
| MD036 | no-emphasis-as-heading | `**Bold text**` used as a section header | Replace with proper heading `## Section` |
| MD041 | first-line-heading | First line is not an H1 | Add `# Title` as line 1, or disable for partial/fragment files |
| MD043 | required-headings | Required heading structure not present | Follow defined heading outline |

## Whitespace Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD009 | no-trailing-spaces | Line ends with one or more spaces | Strip trailing spaces (editor trim-trailing-whitespace setting) |
| MD010 | no-hard-tabs | Tab character used for indentation | Replace tabs with spaces |
| MD012 | no-multiple-blanks | Two or more consecutive blank lines | Reduce to a single blank line |
| MD028 | no-blanks-blockquote | Blank line inside a blockquote | Remove blank line or use `>` on the blank line |

## Line Length

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD013 | line-length | Line exceeds configured length (default 80) | Wrap prose at word boundary. Configure exceptions in `.markdownlint.json`: `{"MD013": {"line_length": 120, "code_blocks": false, "tables": false}}` |

## Code Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD031 | blanks-around-fences | Fenced code block not preceded/followed by blank line | Add blank line before opening ` ``` ` and after closing ` ``` ` |
| MD038 | no-space-in-code | Space inside inline code `` ` code ` `` | Remove spaces: `` `code` `` |
| MD040 | fenced-code-language | Fenced code block has no language identifier | Add language: ` ```python `, ` ```bash `, ` ```json ` |
| MD046 | code-block-style | Mixed indented and fenced code blocks | Use fenced blocks consistently |
| MD048 | code-fence-style | Mixed ` ``` ` and `~~~` fences | Standardise to backticks |

## List Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD004 | ul-style | Mixed `*`, `-`, `+` bullets | Use a single style throughout (default: `dash`) |
| MD005 | list-indent | Unordered list item at wrong indent level | Use consistent 2- or 4-space indentation |
| MD007 | ul-indent | Unordered list items indented wrong | Set indent to configured value (default 2 spaces) |
| MD029 | ol-prefix | Ordered list items don't start at 1 or aren't sequential | Start at `1.` and increment, or configure `ordered: true` |
| MD030 | list-marker-space | Wrong number of spaces after list marker | Single space after `-`/`*`/`1.` |
| MD032 | blanks-around-lists | List not preceded/followed by blank line | Add blank line above first item and below last item |

## Link and URL Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD011 | no-reversed-links | `(text)[url]` — brackets reversed | Correct to `[text](url)` |
| MD034 | no-bare-urls | Raw URL in text without angle brackets or link syntax | Wrap: `<https://example.com>` or `[label](https://example.com)` |
| MD042 | no-empty-links | `[text]()` — empty link destination | Add URL or remove the link |
| MD051 | link-fragments | Fragment link `#section` doesn't match any heading | Fix heading text or fragment |
| MD052 | reference-links-images | Reference link undefined | Define `[ref]: url` or fix the reference name |
| MD053 | link-image-reference-definitions | Unused link reference definition | Remove unused `[ref]: url` definitions |

## Image Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD045 | no-alt-text | Image has no alt text `![]( )` | Add descriptive alt text: `![description](image.png)` |

## HTML Rules

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD033 | no-inline-html | Raw HTML tag in markdown | Remove HTML or allowlist specific tags in config: `{"MD033": {"allowed_elements": ["br", "sub"]}}` |

## Document Structure

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD041 | first-line-heading | First content line is not H1 | Add `# Title` or disable for fragment files |
| MD047 | single-trailing-newline | File doesn't end with exactly one newline | Add newline at end of file |

## Horizontal Rule

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD035 | hr-style | Inconsistent `---` vs `***` vs `___` | Pick one style and use it throughout |

## Blockquote

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD027 | no-multiple-space-blockquote | `>  Text` — extra space after `>` | Single space: `> Text` |

## Table Rules (GFM)

| Rule | Name | Flags | Fix |
|------|------|-------|-----|
| MD055 | table-pipe-style | Inconsistent pipe style in table | Ensure all rows start and end with `|` |
| MD056 | table-column-count | Row has different column count than header | Fix row to match header column count |

## Inline Suppress Pattern

To suppress a single rule for one line:
```markdown
<!-- markdownlint-disable-next-line MD013 -->
This line is intentionally long: https://very.long.url.example.com/path
```

To suppress for a block:
```markdown
<!-- markdownlint-disable MD033 -->
<div class="custom">HTML block</div>
<!-- markdownlint-enable MD033 -->
```

To suppress for the entire file (add near top):
```markdown
<!-- markdownlint-disable MD041 -->
```
