# lora-eval-lab

A small open-weight language model, LoRA fine-tuned on one narrow clinical task, and
**evaluated blind** against its own base model. Companion to
[rag-eval-lab](https://github.com/J-Jurza/rag-eval-lab): same organising idea, that the
evaluation is the deliverable and the model is the excuse to build it.

**Task:** doctor-patient dialogue to clinical note section (the ambient-scribe problem), on
the public [MTS-Dialog](https://github.com/abachaa/MTS-Dialog) dataset (CC BY 4.0, 1,701
dialogue-note pairs across 20 section types).
**Model:** [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct),
4-bit QLoRA on a free Colab T4.
**The point:** did the fine-tune make the notes *better*, judged blind, side by side, with a
rubric and a failure taxonomy? Not "did the loss go down".

## Pipeline

```mermaid
flowchart LR
    D[MTS-Dialog, pinned commit] -->|data.py: official split, duplicate check| S[train 1,201 / valid 98 / held-out 194]
    S -->|generate.py, greedy| B[base outputs]
    S -->|train.py: QLoRA r=16, 2 epochs| A[adapter, ~70 MB]
    A -->|generate.py, same prompt| T[tuned outputs]
    B --> J[judge.py: blinded A/B, Gemini Flash, judged twice with swap]
    T --> J
    H[human blind pass, 30 pairs] -. agreement, kappa .-> J
    J -->|evaluate.py| M[win rate + bootstrap CI, per-dimension, per-section, ROUGE-L, failure taxonomy]
```

## Results

**Not yet run.** The GPU steps run on the weekend of 30 to 31 August 2026; this section is
filled in from `results/metrics.md` afterwards, with the interval, the tie and dropped
counts, the per-dimension and per-section tables, the human-judge agreement, and the
failure taxonomy over every loss. If the tuned model is at parity or worse, that is what
this section will say.

## What gets measured

| Question | Method | Blind spot, stated |
|---|---|---|
| Is the tuned note preferred over the base note? | Blinded side-by-side, randomised A/B, LLM judge with a written rubric, each pair judged twice with A/B swapped, plus a human pass on 30 pairs | Judge and human can share biases (fluency over faithfulness) |
| Preferred on *what*? | Per-dimension rubric scores: faithfulness, completeness, format, concision | Rubric is ours; a real clinic's rubric would differ |
| Preferred *where*? | Per-section breakdown, History of Present Illness reported on its own | 53 HPI pairs give a wide interval |
| What got worse? | Failure taxonomy over every loss, hand-labelled: hallucinated fact, omitted fact, wrong section, format break, other | Labelled by the author, not a clinician |
| How much to trust the judge? | Dropped-pair count from the swap; raw agreement and Cohen's kappa against the human pass | 30 pairs is a calibration, not a validation |
| Sanity | ROUGE-L against the reference note | Rewards overlap, not correctness; reported, never headlined |

Win rate is reported with a bootstrap 95% confidence interval. A 49.9% win rate is parity,
not a win, and the README will say so if that is what happens.

## Quickstart

Everything except training and generation runs on CPU.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m lora_eval_lab.data --download --stats   # pinned CSVs, checksums verified
pytest -q                                          # 38 pure-logic tests, no model, no API
```

The two GPU steps run in one Colab notebook, `notebooks/lora_eval_lab_colab.ipynb`
(T4, about an hour). Then, with a free Gemini key in `.env`:

```bash
pip install -e ".[judge]"
python -m lora_eval_lab.judge --human      # write the 30-pair human pack, score it first
python -m lora_eval_lab.judge --judge      # LLM judge, twice per pair, resumable
python -m lora_eval_lab.evaluate --taxonomy   # write losses.md, label every loss by hand
python -m lora_eval_lab.evaluate           # metrics.md
```

## Design decisions

The full record, with alternatives rejected, is `DECISIONS.md`.

| Decision | Why | Trade-off accepted |
|---|---|---|
| Official MTS-Dialog split, duplicate checks on dialogue text and on note text, held-out ids frozen in the repo | Leakage is the commonest silent error; one test dialogue was a copy of a training dialogue, and five test notes came from encounters also in training (found after training, recorded) | 194 held-out pairs, not 200 |
| Train on all 20 section types, report HPI separately | 1,201 rows beat 282; the section header conditions the model | Headline mixes one-line and paragraph sections |
| Zero-shot base as the control | The written process says so; a prompted base is an optional second column | A bare prompt is a weak opponent |
| Greedy decoding, identical for both models | Repeatable generations; committed outputs can be checked | Greedy can be blunt; both models pay equally |
| Every pair judged twice with A/B swapped, kept only when consistent | Position bias is real and measurable | Two calls per pair; fewer kept pairs |
| Human blind pass before the judge runs | Independence of the human scores | 30 pairs is a time budget |
| Metrics hand-rolled with hand-computed tests | The arithmetic is the deliverable and must be checkable | Slower than a library; no community review |
| Adapter on Drive, not committed | Tens of MB of binary in a docs repo | A clone cannot regenerate tuned outputs without it |

## What the metrics do not catch

- **Blinding and swapping do not remove fluency bias.** A judge can prefer the smoother note over the more faithful one; the rubric's "faithfulness outranks everything" line and the failure taxonomy are the only defences.
- **The human pass is one person, not a clinician.** Agreement with the judge bounds how much to trust the judge; it does not make either of them right.
- **ROUGE-L** rewards overlap with the reference. A note that invents a plausible sentence in the reference's style scores well.
- **The dialogues are constructed, not recorded.** MTS-Dialog's notes came first and the conversations were written to match them, so the task is cleaner than a real consultation.
- **No hyperparameter search.** One configuration, recorded; a better one may exist.

## What this is NOT

A measurement harness around a deliberately small fine-tune, built in a weekend with
Claude Code as the implementing agent. Not production work. What would have to change:

| Area | This repo | Production |
|---|---|---|
| Data | 1,201 constructed dialogues, one public dataset | Consented real consultations, many specialties, continuous collection |
| Evaluation | One LLM judge, one human, 199 pairs | Clinician panel, hundreds of pairs per release, inter-rater reliability tracked |
| Training | One QLoRA run on a free T4 | Search over data mix and hyperparameters, preference tuning after SFT, regression suites |
| Safety | Failure taxonomy read once | Every hallucination class monitored in production, with escalation |
| Serving | None | Quantised adapter behind an inference server, latency and cost measured |

## Honesty

Portfolio project, built in a weekend with Claude Code as the implementing agent. The
task, the evaluation design, the rubric and the decisions in `DECISIONS.md` are mine; the
code was written with the agent and reviewed line by line. Nothing here is claimed as
production work. See `PROCESS.md` for the steps in plain language.

## Repository map

```
src/lora_eval_lab/
  data.py       pinned fetch, official split, duplicate check, frozen held-out ids, chat format
  generate.py   greedy batched generation, base or adapter, prompt fingerprint per row
  train.py      QLoRA via Unsloth, assistant-only loss, best-validation checkpoint
  judge.py      blinding key, human pack, Gemini judge with swap, resumable verdicts
  evaluate.py   swap filter, bootstrap CI, dimensions, sections, ROUGE-L, kappa, taxonomy
eval/           rubric.md · judge_prompt.md · holdout_ids.json
notebooks/      the Colab notebook for the two GPU steps
results/        generations, key, verdicts, human pack, losses, metrics (committed)
tests/          38 tests with hand-computed expected values
PROCESS.md      what happens, step by step, and why
DECISIONS.md    every choice that shapes the result, with alternatives rejected
BUILD_PLAN.md   the build, one commit per step
```

MIT licence. MTS-Dialog is CC BY 4.0 (Ben Abacha et al., EACL 2023) and is fetched from
its source repository at a pinned commit, not stored here.
