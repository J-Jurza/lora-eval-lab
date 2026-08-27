# Decisions

One entry per choice that shapes the result. Git log says what changed; this says why.

## 2026-08-28: The evaluation is the deliverable
**Context:** Anyone can run a LoRA script. Very few portfolio repos evaluate the result blind.
**Decision:** Design the blinded side-by-side, rubric, swap control and human pass before writing any training code. Training is step 3 of 7.
**Alternatives rejected:** Reporting validation loss or ROUGE as the headline (measures overlap, not quality).

## 2026-08-28: MTS-Dialog, dialogue to clinical note section
**Context:** Need a narrow, public, licence-clean task in the candidate's domain.
**Decision:** MTS-Dialog (CC BY 4.0), section-level note generation. It is the ambient-scribe problem in miniature.
**Alternatives rejected:** Generic instruction data (no domain story); synthetic data (evaluation would measure the generator).
**Consequences:** Small dataset; results will have wide confidence intervals, which must be reported.

## 2026-08-28: 1B to 4B open-weight instruct model, QLoRA, free Colab GPU
**Context:** No paid compute. The point is method, not scale.
**Decision:** Qwen2.5-1.5B-Instruct as the default (Apache-2.0, no gated licence), 4-bit QLoRA with Unsloth.
**Alternatives rejected:** Llama 3.2 (gated licence, extra friction); 7B models (do not fit the free tier comfortably).

## 2026-08-28: Split by dialogue id, held-out ids frozen in the repo
**Context:** Leakage between train and test is the commonest silent error in fine-tuning writeups.
**Decision:** Split on dialogue id; commit `eval/holdout_ids.json`; the test set is never opened during development.

## 2026-08-28: Judge with position swap, plus a human blind subset
**Context:** LLM judges show position bias and fluency bias.
**Decision:** Every pair judged twice with A/B swapped, verdicts kept only when consistent; 30 pairs judged blind by the author first; agreement reported.
**Alternatives rejected:** Single-pass judging (position bias unmeasured); no human pass (no anchor for the judge).
