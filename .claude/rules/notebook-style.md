---
paths:
  - "**/*.ipynb"
---
<!-- source: agent-skills/rules/notebook-style.md, version 2026-08-29. Distilled from the
nb-structure skill (rules 1 to 9). Edit the source and re-run bin/rules-export; repo-lint
flags a stale copy. For the full reformatting pass run nb-pass before committing. -->

# Notebook structure (house rules, apply when writing or editing any .ipynb)

Code cells also follow `python-style.md`; markdown cells follow `prose-style.md`.

1. **Title cell first**: markdown, an H1, a `---` rule, then what the notebook does and why.
   No per-notebook change log when the repo has a root `CHANGELOG.md`.
2. **Setup cell, then a separate settings cell.** The first code cell holds plumbing only:
   `sys.path` bootstrap, third-party imports, a blank line, local imports, warnings filter,
   fixed paths and an `OUT_DIR`. Tunable parameters live in their own cell as aligned named
   constants under a `| Setting | What it controls |` markdown table, ending with a
   `display(Markdown(...))` readout of the active settings. No magic literals later.
3. **Suffix naming**: DataFrames `_df`, GeoDataFrames `_gdf`, join inputs `_in`, export-ready
   frames `_out`, paths `_file`; joined frames named for their join chain left to right.
4. **Report banners**: a diagnostic block opens and closes with `#` plus 83 `=` characters.
5. **Reused functions** get type hints and the house docstring (one-line purpose, short
   description, `Args:` one line per parameter with the type in brackets, `Returns:`), and
   validate inputs up front. Tiny local helpers get a one-line docstring.
6. **Defensive data handling**: `.copy()` before mutating a slice, `.reset_index(drop=True)`
   after any filter, a provenance column to verify a join, dropped before export.
7. **Export sequence**: copy, lowercase columns, select and reorder, `drop_duplicates()` and
   reset, rename, `astype(dtype_map)`, `to_csv(index=False)`. Keep the write line commented
   out while the output is still being iterated.
8. **Diagnostics through `display(Markdown(...))`**, not bare prints: backtick names, bold
   the key number, plain **Yes** / **No**, no emoji.
9. **One job per cell**: helpers, build a frame, draw a figure, or report. A cell chaining
   three or more jobs is split; a variable stays with its only consumer.
