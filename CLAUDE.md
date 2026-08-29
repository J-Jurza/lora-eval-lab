# lora-eval-lab: agent briefing

Read [CONTEXT.md](CONTEXT.md) first (what this is, stack, current focus), then `README.md`,
`PROCESS.md` and `DECISIONS.md`. Change history: [CHANGELOG.md](CHANGELOG.md). This repo
belongs to a job search whose rules live in an Obsidian vault; the ones that bind here:

- **Honesty.** Portfolio project, built in a weekend, agent-assisted. Never word anything as
  production experience. Report the interval, report parity as parity, report what got worse.
- **The owner must be able to explain every step.** After each step, update `PROCESS.md` if
  reality diverged from the plan, and write the step's "you should be able to say" lines as
  questions the owner answers before moving on.
- **No leakage.** Held-out ids are frozen in `eval/holdout_ids.json`; nothing in that set is
  ever read during development.
- **Every non-obvious choice goes in `DECISIONS.md`** with the alternative rejected.
- **No em dashes** in any prose (the owner's rule across all writing).
- Keep dependencies minimal: `transformers`, `peft`, `datasets`, `unsloth` (Colab only),
  `numpy`. Metrics hand-rolled with tests, as in rag-eval-lab.
- The Colab notebook is for the two GPU steps only (train, generate). Everything else runs
  locally on CPU.

The task pivoted to vision on 28 Aug (see DECISIONS.md): NEU-DET defects, Qwen2.5-VL-3B,
same evaluation design. A live BHP Computer Vision / VLM contract is the reason; urgency is
real but the honesty and explain-every-step rules do not relax.

Vault context for the human side of this project:
`Work/Career/Job Search 2026-08/Strategy/58 - Learning Path (Projects, Courses, Profile Updates).md`
(Project 1) and `Work/Career/Job Search 2026-08/Strategy/43 - Game Plan (2026-08-26).md` section 6.

## Commands

```bash
source .venv/bin/activate                          # Python 3.12 venv; pytest and ruff live here
pytest -q                                          # 40 pure-logic tests, no model, no API key
python -m lora_eval_lab.data --download --stats    # pinned MTS-Dialog CSVs into data/raw/, sha256 checked
python -m lora_eval_lab.judge --human              # 30-pair human pack; refuses to overwrite a filled one
python -m lora_eval_lab.judge --judge              # Gemini judge, twice per pair, resumable; GEMINI_API_KEY in .env
python -m lora_eval_lab.evaluate                   # results/metrics.json and metrics.md from committed verdicts
python tools/make_figures.py                       # docs/figures/ from results/; matplotlib is in the dev extra
# generate.py and train.py: Colab only, through notebooks/lora_eval_lab_colab.ipynb, never this machine
```

## Working rules

<!-- four-rules: the Karpathy preamble, identical in every repo. Change it in agent-skills, never here. -->
- **Think before coding.** State assumptions; when a request has two readings, ask and propose the one you would pick. Name a simpler approach when you see one. Never code through confusion.
- **Simplicity first.** The minimum code that solves the problem: no speculative abstraction, configurability, or error handling for cases that cannot happen. If 200 lines could be 50, rewrite.
- **Surgical changes.** Every changed line traces to the request. Match the existing style, leave adjacent code alone, mention dead code rather than deleting it, and remove only the orphans your own change created.
- **Goal-driven execution.** Turn the task into a check before starting: "fix the bug" is "write the failing test, then make it pass". Multi-step work gets a short plan with a verification per step.
- **Self-check**: fewer unnecessary diff lines, fewer rewrites, questions before mistakes.

- **Style**: comments explain why, not what. No hype. Write for a sceptical senior engineer. House rules load from `.claude/rules/` when a `.py`, `.md` or `.ipynb` is touched; a hook rejects em dashes and lints `.py`.
- **Commits**: one component per commit, conventional prefixes (`feat(scope):`, `fix:`, `docs:`, `results(step N):`, `chore:`), why in the body when not obvious. Stage explicit paths.
- **Docs upkeep**: a significant choice gets a DECISIONS.md entry with the alternative rejected; a user-visible change gets a CHANGELOG.md line; CONTEXT.md "Current focus" reflects reality at session end.
- **Results discipline**: never hand-edit `results/` beyond the two hand-scored packs; regenerate the rest. Numbers in the README or figures must match `results/metrics.json`.

## Token discipline

- Read `CONTEXT.md`, then this file, then only what the task needs. `grep -n` and `git diff --stat` before reading whole files. Never dump `results/`, `data/`, notebook outputs or logs into the conversation.
- Do not re-read an unchanged file. Delegate broad searches to a subagent and keep the conclusion, not the listing.
- Replies: no preamble, no restating the plan. What was done, what was not, numbers verbatim. Prose longer than a paragraph goes in a file, not the chat.

## Mechanics you will otherwise get wrong

- Unsloth needs CUDA and will not import on this Mac. `train.py` imports it lazily inside `train()`;
  the tests cover only the pure parts (config, dataset shaping, log export).
- Inside `train()`, `unsloth` is imported before `trl` and `transformers` so its patches apply, and
  `SFTConfig` gets the tokenizer's real `eos_token`, not Unsloth's placeholder (commit 47152fe).
- `results/blinding_key.json` is seeded (`BLIND_SEED` in `judge.py`) and written on first use. Never
  regenerate it: 388 verdicts and the human pack hang off it, and pair ids desync silently.
- `eval/holdout_ids.json` is frozen: 194 kept of 199 official test ids after two duplicate checks (dialogue
  text, then note text); excluded and kept-boilerplate ids are listed. Any amendment gets a DECISIONS.md entry first.
- `results/human_pack.md` and `results/losses.md` hold hand-entered scores and labels. `judge --human`
  and `evaluate --taxonomy` refuse to overwrite them without `--force`; `--force` destroys the owner's work.
- `data/raw/` is gitignored MTS-Dialog fetched at commit `3ff0801` with sha256 checksums; read-denied.
- The judge is pinned (`gemini-3.6-flash`, recorded on every verdict row) on prepaid credit; a
  `-latest` alias would silently change the judge on a rerun.
- The Colab notebook is hand-written and thin: install, clone, one cell per stage calling the package.
  Logic goes in `src/`, never in a cell; `nb-pass` before committing it.

## Machine and repo quirks

- Never push; the owner reviews and pushes. The repo is public: nothing from `notes/` or `.env` in a commit.
- `.env` holds `GEMINI_API_KEY`; gitignored and read-denied. Never print or commit it.
- The adapter (about 70 MB) is on the owner's Drive, not in the repo; a clone cannot regenerate `generations_tuned.jsonl`.
- `ruff check` reports 28 pre-existing findings (17 semicolons in `tools/make_figures.py`, `zip()` without
  `strict=` elsewhere). The hook lints the whole file you edit, so fix that file's findings in the same commit.

## Skills that apply here

Binding, not advisory. Skills are model-invoked; this table says when.

| When | Skill |
|---|---|
| A notebook was edited, before its commit | `nb-pass` (style, annotate, structure; `--checks` adds `nb-check`) |
| README, docs or article prose written or changed, before showing it | `wr-unslop` audit; `wr-skimproof` first for anything published |
| A `.docx` deliverable | `word-style` |
| Before a milestone commit | `qa-audit`, then `qa-respond` |
| Docs drifted from code | `docs-audit` |
| Repo feels heavy or stale, or monthly | `repo-lint` |
| Explaining a concept for the write-up | `explain` |
| Working through the project as a course | `learn-course` |

## Owner rulings

- 2026-08-28: the five encounter-level duplicates found after training are excluded from evaluation only; no retrain.
- 2026-08-29: judge on prepaid Gemini credit, `gemini-3.6-flash` pinned; the free-tier fallback chain is superseded.
- 2026-08-30: the taxonomy is agent-labelled with stated provenance; the owner audits a seeded 15 (15 of 15 agreed).

## Definition of done for a change

1. Tests pass (`pytest -q`), including any new pure logic pinned by hand-computed values.
2. Results regenerated if anything upstream of them changed.
3. DECISIONS / CHANGELOG / CONTEXT updated per the rules above.
4. No em dashes; `ruff check` clean on every file touched.

## Knowledge base

The Obsidian dev vault at `/Users/honzik/code/obsidian-dev-vault/coding_projects/` is the hub this repo hangs off. When a task needs background (a book, a paper, a technique, a decision made in another project), read `Wiki/_Meta/index.md` there first, then the doc it points to, and cite vault docs by path. This repo's vault-side notes are `Projects/lora-eval-lab/`: `CONTEXT.md` and `DECISIONS.md` are agent-maintained, `ideas.md` and `research.md` are the owner's. The vault is readable from here through `additionalDirectories` in `.claude/settings.local.json`; never edit it from this repo. Hand learnings worth keeping to the vault agent for `Wiki/3. Project Knowledge/`.
