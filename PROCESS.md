# The process, in plain language

This file exists so that the person whose name is on the repo can explain every step
without the agent in the room. Read it before each step, and after.

## 0. What we are actually testing

A base model (say Qwen2.5-1.5B-Instruct) can already turn a doctor-patient dialogue into
something note-like if you ask it. Fine-tuning shows it a thousand examples of *how this
dataset's notes are written*. The claim under test is narrow: **after fine-tuning, are the
notes better, as judged blind by a rubric a clinician would accept?** Everything below is in
service of answering that honestly. Loss curves are not the answer; preference is.

## 1. Data (`data.py`)

- Download MTS-Dialog. Each row is a dialogue, a section header (e.g. "History of Present
  Illness"), and the reference note text for that section.
- Use the dataset's **official split** (1,201 train / 100 validation / 200 test). Each row is
  its own dialogue snippet with its own id, so the split is already by dialogue. Then check
  for the leakage this dataset actually has, which comes in two kinds: the same dialogue text
  in more than one split, and the same source note behind different dialogues. Any held-out
  row whose dialogue is also in train, or whose reference note (8 or more words) matches a
  training note, is dropped and its id recorded. Short boilerplate notes that recur across
  encounters ("No known drug allergies") are kept and listed; they are the task, not leakage.
  The second kind was found after training, from the first tuned output examined; the
  exclusion applies to evaluation and is recorded in `DECISIONS.md`.
  If the same dialogue appears in train and test the result is contaminated. This is the
  first thing a reviewer checks.
- Freeze the held-out set: write its ids to `eval/holdout_ids.json` and never look at those
  dialogues during development.
- Every row keeps its section header (there are 20), and the header goes in the prompt so the
  model knows which section to write. History of Present Illness is reported separately in
  the write-up because it is the ambient-scribe case.
- Format each training example as a chat: system instruction, the dialogue as the user turn,
  the reference note as the assistant turn.

**You should be able to say:** how many examples in each split, how the split was made, what
the duplicate check found, and why leakage between splits matters.

## 2. Base model generations first (`generate.py`)

Before training anything, run the **untuned** base model over the held-out set with the same
prompt and save every output. This is the control. Without it there is nothing to compare
against, and "the fine-tuned model produces notes" is not a finding.

## 3. Train (`train.py`, on Colab)

- QLoRA: the base model is loaded in 4-bit to fit a free T4 GPU, and only small low-rank
  adapter matrices are trained. The base weights never change.
- Hyperparameters are few and recorded: rank, alpha, learning rate, epochs, max sequence
  length. Defaults from the Unsloth docs, changed only with a reason written in
  `DECISIONS.md`.
- Validation loss is watched for overfitting, and that is *all* it is used for.
- Save the adapter (tens of MB), not the merged model. The adapter kept is the one from the
  step where validation loss was lowest.

**You should be able to say:** what LoRA changes and what it leaves alone, why 4-bit, what the
adapter file is, and roughly how long training took.

## 4. Tuned model generations (`generate.py` again)

Same held-out dialogues, same prompt, same decoding settings (temperature, max tokens), base
model plus adapter. Save every output beside the base outputs. Now each held-out dialogue has
three texts: reference, base output, tuned output.

## 5. Blinded side-by-side judging (`judge.py`)

- For each dialogue, present the judge with the dialogue, the reference, and the two outputs
  labelled **A** and **B**, with **which one is the tuned model randomised** and the mapping
  stored separately. The judge never knows.
- The judge is an LLM (Gemini Flash, as in rag-eval-lab; prepaid credit, since new keys carry no
  free quota) given the rubric in
  `eval/rubric.md`: score A and B on faithfulness, completeness, format and concision, then
  state a preference or a tie, with one sentence of reason.
- Run each pair **twice with A/B swapped** and keep only consistent verdicts; position bias
  is real and this is the cheap control for it.
- **Human pass:** you judge 30 pairs blind yourself, same rubric, before the judge runs.
  `judge.py --human` writes the pack; you fill a scores line per pair. Raw agreement and
  Cohen's kappa between you and the judge are reported. This is the step that mirrors
  Heidi's clinician side-by-side, at portfolio scale.

**You should be able to say:** why blinding, why the swap, why a human subset, and what
agreement rate you saw.

## 6. Metrics and the failure write-up (`evaluate.py`)

- Win rate (tuned preferred), tie rate, with a bootstrap 95% confidence interval, over the
  pairs kept by the swap check. The dropped count is reported, with a sensitivity line that
  counts dropped pairs as ties.
- Per-section rates, so History of Present Illness is visible on its own.
- Per-dimension mean scores, base vs tuned.
- ROUGE-L as a sanity check only, with the sentence "ROUGE rewards overlap, not
  correctness" next to it.
- **Failure taxonomy:** every pair the tuned model *lost*, labelled: hallucinated fact,
  omitted fact, wrong section, format break, other. This table is the most useful thing in
  the repo, because it says what fine-tuning broke. What happened: the agent labelled all 88
  with stated provenance and the owner audits a seeded random 15 (see `DECISIONS.md`).

## 7. Write it up

What happened (29 to 30 August 2026): the base model won, 51.5% to 33.9% with 14.6% ties, and faithfulness was the dimension that fell. The README leads with that.

README gets the numbers, the interval, the failure table and the honest sentence about
what the result does and does not show. If the tuned model is at parity or worse, that is
the write-up. A negative result with a clean method is a better portfolio piece than an
inflated positive one.

## What "done" means

- Held-out ids frozen and never trained on.
- Base and tuned generations committed.
- Judge verdicts with swap-consistency filtering committed.
- Human blind pass on 30 pairs committed.
- Metrics with confidence intervals in the README.
- Failure taxonomy table in the README.
- Every non-obvious choice in `DECISIONS.md`.
- You can explain steps 1 to 6 without notes.
