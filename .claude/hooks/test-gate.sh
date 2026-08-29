#!/usr/bin/env bash
# Stop hook. When the turn changed Python and the repo has tests, run them and refuse to
# end the turn on failure (exit 2 feeds the failure back to Claude). No-op otherwise.
# Claude Code overrides a Stop hook after 8 consecutive blocks. Version 2026-08-30.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
ls tests/*.py >/dev/null 2>&1 || exit 0
changed="$( { git diff --name-only HEAD -- '*.py' 2>/dev/null; git ls-files --others --exclude-standard -- '*.py' 2>/dev/null; } | grep -c . )"
[ "$changed" -gt 0 ] || exit 0
if [ -x .venv/bin/pytest ]; then PYTEST=.venv/bin/pytest; elif command -v pytest >/dev/null 2>&1; then PYTEST=pytest; else exit 0; fi
out="$("$PYTEST" -q -x -p no:cacheprovider 2>&1)"; code=$?
if [ "$code" -ne 0 ]; then
  echo "test-gate: the turn changed Python and the tests fail. Fix before finishing. Last lines:" >&2
  echo "$out" | tail -25 >&2
  exit 2
fi
exit 0
