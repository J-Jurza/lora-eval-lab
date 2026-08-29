#!/usr/bin/env bash
# PreToolUse hook on the Bash tool. Enforces what CLAUDE.md can only request: no force
# pushes or history rewrites, ever; a plain push asks the owner. Prints a permission
# decision as JSON and exits 0, per the hooks contract. Version 2026-08-30.
set -u
PAYLOAD="$(cat)"; export PAYLOAD
python3 - <<'PY'
import json, os, re, sys
try:
    cmd = json.loads(os.environ.get("PAYLOAD", "")).get("tool_input", {}).get("command", "") or ""
except Exception:
    sys.exit(0)
def out(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))
    sys.exit(0)
DENY = [
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|--force-with-lease|\s--delete\b|\s:\S)", "force push, branch delete or history rewrite on the remote"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards work"),
    (r"\bgit\s+checkout\s+(--\s+)?\.\s*$|\bgit\s+checkout\s+--\s+\.", "git checkout . discards every uncommitted change"),
    (r"\bgit\s+restore\s+(\.|--worktree\s+\.)\s*$", "git restore . discards every uncommitted change"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean -f deletes untracked files"),
    (r"\bgit\s+(filter-repo|filter-branch)\b", "history rewrite"),
    (r"\bgit\s+branch\s+-D\b", "force branch delete"),
]
for pat, why in DENY:
    if re.search(pat, cmd):
        out("deny", f"Blocked by the house git guard: {why}. Ask the owner if this is really wanted.")
if re.search(r"\bgit\s+push\b", cmd):
    out("ask", "Pushes are the owner's call. Confirm this push.")
sys.exit(0)
PY
