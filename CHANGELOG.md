# Changelog

Notable changes, newest first. One line per change; the *why* behind design choices
lives in [DECISIONS.md](DECISIONS.md), so entries here stay short.

## [Unreleased]

### Added
- Agent surface: CONTEXT.md, this changelog, committed `.claude/settings.json` with deny and allow rules, style-guard hook, path-scoped house rules, `[tool.ruff]`

## 2026-08-29

### Added
- Failure taxonomy over the 88 losses, agent-labelled with stated provenance; owner audit 15 of 15 agree
- README results section: base preferred 51.5% to 33.9%, dimension table, judge checks, taxonomy, Medium write-up link
- Figures from committed results (`tools/make_figures.py`); results README listing every artefact by step
- Judge verdicts: 388, gemini-3.6-flash, both orderings per pair; metrics over 171 swap-consistent pairs
- Human blind pass, 30 pairs, with a corrections log

### Changed
- `judge --human` and `evaluate --taxonomy` refuse to overwrite a filled pack without `--force`
- Judge pinned to gemini-3.6-flash on prepaid credit; one genai client per run
- CI token limited to `contents: read`; grouped, commented `.gitignore`

## 2026-08-28

### Added
- Data module: pinned MTS-Dialog fetch, official split, duplicate checks on dialogue and note text, frozen held-out ids
- Generation (greedy, batched, resumable), QLoRA training via Unsloth, blinded judging with a seeded key, hand-rolled metrics with pinned tests
- Base and tuned generations, training config and loss log, blinding key, unfilled human pack
- Thin Colab notebook for the GPU steps; CI running the pure-logic tests
- Scaffold: README, PROCESS, BUILD_PLAN, DECISIONS, rubric, judge prompt

### Changed
- Five held-out rows sharing an encounter with training excluded from evaluation (194 kept), recorded in DECISIONS.md
