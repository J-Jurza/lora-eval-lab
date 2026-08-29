---
paths:
  - "**/*.py"
---
<!-- source: agent-skills/rules/python-style.md, version 2026-08-29. Distilled from the
nb-style skill (rules 1 to 9, 12, 13, 16, 17). Edit the source and re-run
bin/rules-export; repo-lint flags a stale copy. -->

# Python style (house rules, apply when writing or editing any .py file)

Formatting rules only. Logic, names and quote style are not the concern here. `ruff check`
runs after every edit through a hook; it lints, it does not format, because rule 1 below
is not what a formatter would do.

1. **Calls with 3 or more arguments expand**: one argument per line, trailing comma, the
   closing `)` on its own line aligned with the start of the statement. A call that fits
   within about 100 characters may stay on one line. Never half-wrap: fully inline or fully
   expanded. Nested calls with 3+ arguments expand recursively.
2. **Method chains of 3 or more calls** wrap in outer parentheses, one `.method(...)` per
   line with a leading dot. Two-step chains stay inline unless over 100 characters.
3. **Dict, list and tuple literals with 4 or more items** go one item per line, trailing
   comma, closing bracket on its own line.
4. **Comprehensions**: one `for` and at most one short `if` stays inline. Two `for` clauses,
   a long condition, or a multi-argument call in the expression breaks one clause per line.
5. **Comments explain why, not what.** At most two consecutive inline comment lines. Delete
   narration (`# loop over rows`) and reviewer-talk (`# per QA finding 4`). Keep short
   group labels (`# Frame the zoom`). No em dashes and no `--` substitutes.
6. **No backslash continuation**: parenthesise, one operand per line.
7. `is None` / `is not None`, never `== None`. No semicolons between top-level statements.
8. **DataFrames carry a `_df` suffix, GeoDataFrames `_gdf`.** Series, arrays and scalars do
   not. Role suffixes compose: `left_gdf_in`, `routes_df_out`.
9. **Blank lines separate logical groups** (load, transform, output). One blank line, never
   two, inside a body. A group-label comment starts its group: blank line before it, not
   after. No blank line right after `def`/`for`/`if` or before a closing bracket.
10. **Docstrings**: one-line summary, then one to three plain sentences (dot points only for
    genuinely complicated functions). `Args:` one line per parameter as
    `name (type): description.`; related parameters may share a line. `Returns:` in the
    same style. Tiny helpers get a single line.
11. **Section banners** in files with three or more logical groups: a line of dashes, the
    title, a line of dashes, each prefixed `# `, dashes to column 78, one blank line each
    side. Sentence-case noun phrases. None in files under about 60 lines, none inside a
    function, never around a single function.

```python
# ----------------------------------------------------------------------------
# Paths and source pin
# ----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

chunks = build_chunks(
    docs,
    max_tokens=256,
    length_fn=tokenizer_length,
)
```

Tests: pin hand-computed values, not mocks of the thing under test. A test name says what
behaviour is pinned (`test_overlap_never_exceeds_cap`), not which function is called.
