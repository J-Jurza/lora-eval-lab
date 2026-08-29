#!/usr/bin/env bash
# PostToolUse hook for Edit|Write. Reads the tool call JSON on stdin, finds the edited
# file, and rejects two things the house rules forbid but an LLM keeps producing:
# em dashes in any text file, and lint errors in Python. Exit 2 sends the message back
# to Claude as feedback so it fixes the file; exit 0 is silent.
set -u

file="$(python3 -c 'import sys, json
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))
except Exception:
    print("")')"
[ -n "$file" ] && [ -f "$file" ] || exit 0

case "$file" in
  *.py|*.md|*.toml|*.yml|*.yaml|*.txt|*.json|*.ipynb) ;;
  *) exit 0 ;;
esac

# U+2014 em dash. Notebooks are generated, but the builder's strings end up in them too.
if grep -n $'\xe2\x80\x94' "$file" >/dev/null 2>&1; then
  echo "style-guard: em dash found in $file. House rule: use a colon, a comma, or two sentences." >&2
  grep -n $'\xe2\x80\x94' "$file" | head -5 >&2
  exit 2
fi

if [[ "$file" == *.py ]]; then
  ruff=""
  if [ -x "${CLAUDE_PROJECT_DIR:-.}/.venv/bin/ruff" ]; then ruff="${CLAUDE_PROJECT_DIR:-.}/.venv/bin/ruff"
  elif command -v ruff >/dev/null 2>&1; then ruff="ruff"; fi
  if [ -n "$ruff" ]; then
    out="$("$ruff" check --quiet "$file" 2>&1)" || { echo "style-guard: ruff check failed for $file" >&2; echo "$out" >&2; exit 2; }
  fi
fi
exit 0
