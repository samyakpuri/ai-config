#!/bin/bash
set -euo pipefail

input=$(cat)

# Require jq for JSON parsing
if ! command -v jq &>/dev/null; then
  echo "markdown-lint hook: jq is required but not found. Install jq to enable automatic markdown linting." >&2
  exit 0
fi

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Only process .md files
if [[ -z "$file_path" ]] || [[ "$file_path" != *.md ]]; then
  exit 0
fi

# Warn and ask for installation if markdownlint is missing
if ! command -v markdownlint &>/dev/null; then
  printf 'markdown-lint: markdownlint CLI not found for "%s".\nInstall it with: npm install -g markdownlint-cli\n' "$file_path" >&2
  exit 2
fi

# Detect config file at project root (first match wins)
config_args=()
for config in \
  "$CLAUDE_PROJECT_DIR/.markdownlint.json" \
  "$CLAUDE_PROJECT_DIR/.markdownlint.jsonc" \
  "$CLAUDE_PROJECT_DIR/.markdownlint.yaml" \
  "$CLAUDE_PROJECT_DIR/.markdownlint.yml"
do
  if [[ -f "$config" ]]; then
    config_args=(--config "$config")
    break
  fi
done

# Run markdownlint — exit 0 if clean
if lint_output=$(markdownlint "${config_args[@]}" "$file_path" 2>&1); then
  exit 0
fi

# Errors found — feed back to Claude to trigger suggestions
printf 'markdownlint issues in %s:\n\n%s\n\nSuggest specific fixes for each violation above.' \
  "$file_path" "$lint_output" >&2
exit 2
