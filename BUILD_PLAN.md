# Build plan

One commit per step. Each step fits one sitting. Ordered as `PROCESS.md`. After each step
the agent asks the "you should be able to say" questions and does not move on until the
owner has answered in their own words. If reality diverges from `PROCESS.md`, `PROCESS.md`
is updated in the same commit.

Weekend shape: steps 1 to 4 on Saturday (steps 2 to 4 are one Colab session), steps 5 to 7
on Sunday. Step 8 is optional.

## Status, 30 August 2026

Steps 0 to 6 done and committed: GPU session run 28 August (base generations, 15-minute
train, tuned generations), human pass 29 August, judge run 30 August (388 verdicts),
metrics computed. Result: base model preferred, 51.5% to 33.9%. Step 6's failure taxonomy
awaits the owner's labels in `results/losses.md`; step 7's README results section is
written with the taxonomy table marked pending. Step 8 (one-shot base) not run.

## Rulings needed before step 1 (resolved, kept for the record)

Three items from the plan review; each becomes a `DECISIONS.md` entry once ruled.

| # | Question | Recommendation |
|---|---|---|
| R1 | Own split by id, or the dataset's official split? | Official split (1,201 / 100 / 200), test ids frozen in `eval/holdout_ids.json`, plus a near-duplicate check across splits |
| R2 | Zero-shot base only, or also a one-shot prompted base? | Zero-shot is the control; one-shot is optional step 8, a second column, never a replacement |
| R3 | What if the Gemini free tier caps out? | Resumable verdict cache; fall back to Flash-Lite, then to a random 120-pair subset, stated in the README |

Decisions to write regardless (proposed text goes in at step 0): swap-consistency rule
(same winner in both orderings, or tie in both; everything else dropped, counted, and
reported with a sensitivity line treating dropped pairs as ties); greedy decoding for both
models; section header in the prompt; adapter saved to Drive and not committed; thin
hand-written notebook whose cells only call the package.

## GPU budget (Colab free tier, T4, 15 GB)

| Item | Estimate |
|---|---|
| Unsloth install, repo clone, model download | 5 to 8 min |
| Base generations, 200 dialogues, greedy, batched, max 320 new tokens | 8 to 15 min |
| QLoRA train, 1,201 examples, 2 epochs, max seq 1,536, batch 2 x grad-acc 4 | 15 to 30 min |
| Tuned generations, same settings | 10 to 20 min |
| **Total** | **40 to 75 min, one session** |

Free-tier sessions run a few hours and can be pre-empted; the notebook saves every
artefact to Drive as it lands so a pre-emption costs one stage, not the day. Budget two
sessions in case the first is lost. Step 8 adds 10 to 15 min.

---

## Step 0: plan and decisions

**Written:** this file; `DECISIONS.md` entries for R1 to R3 and the five smaller items;
`PROCESS.md` step 1 updated if R1 is ruled as recommended.
**You run:** nothing.
**Explain afterwards:** why each decision was made and what was rejected.
**Done:** rulings recorded, plan committed.

## Step 1: data (`data.py`, `eval/holdout_ids.json`)

**Written:** `data.py` downloads the MTS-Dialog CSVs from the source GitHub repo at a
pinned commit into `data/` (git-ignored, CC BY 4.0 so committing would be legal, but the
pinned-source pattern matches rag-eval-lab and keeps the diff clean); applies the split;
writes `eval/holdout_ids.json`; a near-duplicate check across splits (normalised dialogue
text, fail loudly on any hit); a `format_example()` that builds the chat: system
instruction naming the task, user turn with the section header and the dialogue, assistant
turn with the reference section text; `--stats` prints counts per split, section-header
distribution, and token-length quantiles (this is where max seq length comes from).
`tests/test_data.py`: split disjointness, formatting on a hand-written row, duplicate
detector on a planted duplicate.
**You run:** `pip install -e ".[dev]"`, `python -m lora_eval_lab.data --stats`, `pytest -q`.
**Explain afterwards:** how many rows per split, how the split was made, why leakage is
the first thing a reviewer checks, why the section header is in the prompt, and why the
held-out ids are committed but the held-out text is never opened.
**Done:** `holdout_ids.json` committed, stats in the commit message, tests green.

## Step 2: base generations (`generate.py`, notebook part 1)

**Written:** `generate.py` loads a model (plus optional adapter path), builds the same
prompt as `data.format_example()` without the assistant turn, generates greedily with a
fixed `max_new_tokens`, and writes `results/generations_<tag>.jsonl` with id, prompt hash,
output, decoding settings and model identifier. Batched, resumable (skips ids already
written). The notebook: install cell, clone cell, one cell per stage, each stage copies its
output to Drive. `tests/test_generate.py`: prompt construction and output parsing only, no
model.
**You run:** open the notebook in Colab, run install, clone and the base-generation cell.
Download `generations_base.jsonl` and commit it.
**Explain afterwards:** why the control comes before training, why greedy decoding, and
what is in each row of the generations file.
**Done:** 200 base outputs committed with the settings that produced them.

## Step 3: train (`train.py`, notebook part 2)

**Written:** `train.py` builds the chat-formatted train and validation sets, loads
Qwen2.5-1.5B-Instruct in 4-bit through Unsloth, attaches LoRA (rank 16, alpha 16, dropout
0, all linear projections, Unsloth defaults), trains with TRL's SFT trainer on assistant
tokens only, logs train and validation loss per epoch, saves the adapter only. All
hyperparameters in one dict at the top of the file and echoed into
`results/train_config.json`. `DECISIONS.md` gets the hyperparameter entry.
**You run:** the train cell. Watch the validation loss. Copy the adapter and
`train_config.json` plus the loss log to Drive; commit the config and loss log, not the
adapter.
**Explain afterwards:** what LoRA changes and what it leaves alone, why 4-bit, what rank
and alpha are, what the adapter file is, what validation loss was used for and what it was
not used for, and how long training took.
**Done:** adapter on Drive, config and loss curve committed, training time in the commit.

## Step 4: tuned generations (notebook part 3)

**Written:** nothing new; `generate.py` with `--adapter`.
**You run:** the tuned-generation cell. Download `generations_tuned.jsonl` and commit it.
Spot-read five pairs (base, tuned, reference) and write two sentences of first
impressions in the commit message; this is the last unblinded look before judging.
**Explain afterwards:** what is identical between the two runs and why that matters.
**Done:** every held-out dialogue has reference, base output, tuned output.

## Step 5: blinded judging (`judge.py`, `eval/judge_prompt.md`)

**Written:** `judge.py` builds the pairs: for each id, a random A/B assignment from a
seeded RNG, stored in `results/blinding_key.json` (never read by the scoring code until
step 6). `--human` writes `results/human_pack.md`: 30 seeded-random pairs, dialogue,
reference, A, B, with a scoring stub, no key. `--judge` calls Gemini Flash with the rubric
and the pair, twice per id with A/B swapped, parses a fixed JSON reply (four scores per
side, preference, one sentence), writes each verdict to `results/judge_verdicts.jsonl` as it
lands, resumes on rerun. `tests/test_judge.py`: verdict parsing, swap logic, and the
blinding key never leaking into the human pack.
**You run:** `python -m lora_eval_lab.judge --human`, then score all 30 pairs yourself
with the rubric, before running the judge. Then `--judge` with `GEMINI_API_KEY` set.
Commit the human scores, the verdicts, and the key.
**Explain afterwards:** why blinding, why the swap, what position bias looks like in the
verdicts, why the human pass comes first, and what the agreement rate was.
**Done:** 30 human verdicts and up to 400 judge verdicts committed, key committed.

## Step 6: metrics and the failure taxonomy (`evaluate.py`)

**Written:** hand-rolled, each with a test on hand-computed values: swap-consistency
filter; win rate, tie rate, loss rate over kept pairs; percentile bootstrap 95% interval on
win rate (seeded, 10,000 resamples); sensitivity line with dropped pairs as ties;
per-dimension means base vs tuned with a paired difference and its bootstrap interval;
ROUGE-L via longest common subsequence on whitespace tokens; human-judge agreement as raw
agreement and Cohen's kappa. `--taxonomy` writes `results/losses.md`: every kept pair the
tuned model lost, with both outputs, for you to label by hand into hallucinated fact,
omitted fact, wrong section, format break, other. `evaluate.py` then reads your labels
back and writes `results/metrics.json` and `results/metrics.md`.
**You run:** `pytest -q`, `python -m lora_eval_lab.evaluate`, label the losses, run again.
**Explain afterwards:** what a bootstrap interval is and why the interval is wide, why
ROUGE is a sanity check, what kappa adds over raw agreement, and what the taxonomy says
fine-tuning broke.
**Done:** `metrics.md` committed with intervals; every loss labelled.

## Step 7: write-up (`README.md`)

**Written:** README results section: the win-rate line with its interval, the tie and
dropped counts, the per-dimension table, the failure table with the same prominence as
the win rate, the ROUGE line with its caveat, the human-judge agreement, a "what this does
and does not show" list, and a "what this is NOT" table in the rag-eval-lab pattern.
`PROCESS.md` reconciled against what happened. GitHub Actions running `pytest` only (the
notebook needs a GPU and is not run in CI; stated).
**You run:** read the README top to bottom; if a sentence would not survive an
interviewer's follow-up, it goes.
**Explain afterwards:** steps 1 to 6 without notes.
**Done:** the "done" list in `PROCESS.md` is fully ticked.

## Step 8 (optional): one-shot prompted base

**Written:** `generate.py --one-shot` prepends one fixed training example to the prompt.
**You run:** the extra cell; judge and evaluate as a second comparison.
**Explain afterwards:** why a prompted baseline is the fairer control and what changed.
**Done:** a second results column, or a sentence saying it was skipped and why.

## After the repo

Not in this repo: CV bullet key in `_build/content.py`, skills row, letter gap
sentences, LinkedIn Projects entry, Post 2 (title updated to 1.5B).
