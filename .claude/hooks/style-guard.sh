#!/usr/bin/env bash
# PostToolUse hook for Edit|Write. Checks ONLY the lines the edit added (git diff against
# HEAD; every line when the file is new or untracked): em dashes in any text file, ruff
# findings in Python. Legacy lines never trigger it, so the surgical rule holds and an agent
# is never pushed into rewriting a whole file. Exit 2 returns the message to Claude as
# feedback; exit 0 is silent. Version 2026-08-30 (diff-aware).
set -u
PAYLOAD="$(cat)"
export PAYLOAD
python3 - <<'PY'
import json, os, pathlib, re, shutil, subprocess, sys
try:
    file = json.loads(os.environ.get("PAYLOAD", "")).get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)
if not file or not os.path.isfile(file): sys.exit(0)
f = pathlib.Path(file).resolve()
if f.suffix not in {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".json", ".ipynb"}: sys.exit(0)

def git(*a):
    return subprocess.run(["git", "-C", str(f.parent), *a], capture_output=True, text=True)
root = git("rev-parse", "--show-toplevel").stdout.strip()
tracked = bool(root) and git("ls-files", "--error-unmatch", str(f)).returncode == 0
lines = open(f, errors="ignore").read().split("\n")
if tracked:
    added = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", git("diff", "-U0", "HEAD", "--", str(f)).stdout, re.M):
        start, count = int(m.group(1)), int(m.group(2)) if m.group(2) is not None else 1
        added.update(range(start, start + count))
else:
    added = set(range(1, len(lines) + 1))
if not added: sys.exit(0)

problems = []
for n in sorted(added):
    if n <= len(lines) and "—" in lines[n - 1]:
        problems.append(f"{f.name}:{n}: em dash. House rule: a colon, a comma, or two sentences.")
if f.suffix == ".py":
    ruff = shutil.which("ruff") or next((str(p) for p in [pathlib.Path(root or ".") / ".venv/bin/ruff"] if p.exists()), None)
    if ruff:
        out = subprocess.run([ruff, "check", "--output-format=concise", str(f)], capture_output=True, text=True).stdout
        for line in out.splitlines():
            m = re.match(r"^(.*?):(\d+):\d+: (.*)$", line)
            if m and int(m.group(2)) in added:
                problems.append(f"{f.name}:{m.group(2)}: ruff {m.group(3)}")
if problems:
    print("style-guard (added lines only):", file=sys.stderr)
    for p in problems[:8]: print("  " + p, file=sys.stderr)
    sys.exit(2)
PY
