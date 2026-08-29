# lora-eval-lab: Context

> [!NOTE]
> For agents: read at session start, with [CLAUDE.md](CLAUDE.md). Keep this file small.
> Historical reasoning lives in [DECISIONS.md](DECISIONS.md), change history in
> [CHANGELOG.md](CHANGELOG.md), step order in [PROCESS.md](PROCESS.md) and
> [BUILD_PLAN.md](BUILD_PLAN.md).

status:: active

## What this is

Qwen2.5-1.5B-Instruct, QLoRA fine-tuned on MTS-Dialog (doctor-patient dialogue to clinical
note section) and evaluated blind against its own base model: seeded A/B blinding, a Gemini
judge with a written rubric, every pair judged twice with the order swapped, a 30-pair human
pass scored first, win rate with a bootstrap interval, per-dimension and per-section scores,
and a failure taxonomy over every loss. The evaluation is the deliverable. Result: the base
model won (51.5% to 33.9%, tie 14.6%, 171 kept pairs), faithfulness fell, ROUGE-L rose.
Companion to rag-eval-lab; sibling of vlm-defect-lab, which carries the vision task.

## Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.12 (`.venv/` in repo root) |
| Core deps | numpy, datasets, transformers, peft; `judge` extra adds google-genai, `dev` adds pytest, ruff, matplotlib |
| Training | Unsloth, TRL, 4-bit bitsandbytes on a Colab T4 (`notebooks/`, never local) |
| Data | MTS-Dialog at a pinned commit, official split, duplicate checks on dialogue and note text, 194 held-out |
| Judge | gemini-3.6-flash via google-genai, prepaid credit, A/B swapped, resumable verdicts |
| Metrics | hand-rolled in `evaluate.py`, pinned by hand-computed tests |
| Tests / CI | pytest, 40 tests; GitHub Actions runs them on push, the notebook is not run in CI |

## Things an agent should always know

- Portfolio project, built in a weekend with Claude Code as the implementing agent; never
  worded as production work. A negative result is the result.
- The owner must be able to explain every step: after a step, ask the PROCESS.md "you should
  be able to say" questions and wait for answers. They live in the gitignored `notes/owner_answers.md`.
- Data is gitignored on purpose; rebuild with `python -m lora_eval_lab.data --download`.
  Never commit it.
- Every number in the README traces to a command and a committed file in `results/`.
- Vault-side notes: `~/code/obsidian-dev-vault/coding_projects/Projects/lora-eval-lab/`.

## Do NOT touch without asking

- `eval/holdout_ids.json`: the frozen split is the credibility of every number downstream.
- `results/blinding_key.json`: the verdicts and the human pack are keyed to it.
- `results/human_pack.md` scores and `results/losses.md` labels: hand-entered and complete;
  only the corrections log may change.
- The fixed decisions in DECISIONS.md (dataset, model, judge, swap rule).
- Published git history (no rebase or force-push).

## Current focus

- Steps 0 to 7 done: results in the README, taxonomy audited (15 of 15 agree), write-up
  published on Medium on 2026-08-30.
- Open: step 8, the one-shot prompted base as a second control. Worth running because the
  zero-shot base already won. Needs one Colab session and about 200 more judge calls.
