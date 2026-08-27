# lora-eval-lab

A small open-weight language model, LoRA fine-tuned on one narrow clinical task, and
**evaluated blind** against its own base model. Companion to
[rag-eval-lab](https://github.com/J-Jurza/rag-eval-lab): same organising idea, that the
evaluation is the deliverable and the model is the excuse to build it.

**Task:** doctor-patient dialogue → clinical note section (the ambient-scribe problem), on
the public MTS-Dialog dataset (CC BY 4.0, ~1.7k dialogue-note pairs).
**Model:** a 1B to 4B open-weight instruct model, QLoRA on a free Colab GPU.
**The point:** did the fine-tune actually make the notes *better*, judged the way a
clinician would judge them, blind, side by side, with a rubric and a failure taxonomy?
Not "did the loss go down".

## What gets measured

| Question | Method | Blind spot, stated |
|---|---|---|
| Is the tuned note preferred over the base note? | Blinded side-by-side, randomised left/right, LLM judge with a written rubric, plus a human pass on a subset | Judge and human can share biases (fluency over faithfulness) |
| Preferred on *what*? | Per-dimension rubric scores: faithfulness, completeness, format, concision | Rubric is ours; a real clinic's rubric would differ |
| What got worse? | Failure taxonomy over every loss: hallucinated fact, omitted fact, wrong section, format break | Taxonomy is hand-labelled on a sample, not exhaustive |
| Sanity | ROUGE-L against the reference note | Rewards overlap, not correctness; reported, never headlined |

Win rate is reported with a bootstrap confidence interval. A 49.9% win rate is parity, not
a win, and the README will say so if that is what happens.

## Honesty

Portfolio project, built in a weekend with Claude Code as the implementing agent. The
task, the evaluation design, the rubric and the decisions in `DECISIONS.md` are mine; the
code was written with the agent and reviewed line by line. Nothing here is claimed as
production work. See `PROCESS.md` for the steps in plain language.

## Layout

```
src/lora_eval_lab/   data.py · train.py · generate.py · judge.py · evaluate.py
eval/                rubric.md · held-out ids · judge prompts
notebooks/           the Colab notebook that runs train + generate on the free GPU
results/             generations, judgements, metrics (committed as JSON/CSV)
tests/               metric and parsing tests with hand-computed values
PROCESS.md           what happens, step by step, and why
DECISIONS.md         every choice that shapes the result, with alternatives rejected
```
