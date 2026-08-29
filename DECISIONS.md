# Decisions

One entry per choice that shapes the result. Git log says what changed; this says why.

## 2026-08-28: The evaluation is the deliverable
**Context:** Anyone can run a LoRA script. Very few portfolio repos evaluate the result blind.
**Decision:** Design the blinded side-by-side, rubric, swap control and human pass before writing any training code. Training is step 3 of 7.
**Alternatives rejected:** Reporting validation loss or ROUGE as the headline (measures overlap, not quality).

## 2026-08-28: MTS-Dialog, dialogue to clinical note section
**Status:** Superseded by "2026-08-28: Pivot to vision" below. The text task continues separately at lower priority.
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

## 2026-08-28: The dataset's official split, with a duplicate check, not a home-made split
**Context:** In MTS-Dialog every row is an independent dialogue snippet with its own id, so "split by id" is the same as "split by row" and guarantees nothing on its own. The dataset ships an official split (1,201 train / 100 validation / 200 test) used by the MEDIQA-Chat 2023 shared task.
**Decision:** Use the official split. Freeze the official test ids in `eval/holdout_ids.json`. Check normalised dialogue text across splits and drop any held-out row whose dialogue also appears in train (the first inspection found 1 such row in test and 2 in validation); record the dropped ids.
**Alternatives rejected:** Our own random split by id (not comparable to the literature, and no stronger against leakage); ignoring duplicates (the one form of leakage this dataset actually has).
**Consequences:** 199 held-out pairs rather than 200; numbers are comparable to published MTS-Dialog results, which the README may cite for context only.

## 2026-08-28: Train on all 20 section types, judge all held-out pairs, break out History of Present Illness
**Context:** The data has 20 section headers, dominated by family/social history (351 train rows) and history of present illness (GENHX, 282). Many sections are one-line notes (allergies, medications). GENHX alone would leave 282 train and 53 test pairs.
**Decision:** Train on every row, with the section header in the prompt so the model is conditioned on which section to write. Judge every held-out pair. Report the GENHX subset separately in the README, since it is the ambient-scribe case.
**Alternatives rejected:** GENHX only (too few pairs; the interval would be uninformative); top five sections only (narrower story for no gain in rigour).
**Consequences:** The headline number mixes easy one-line sections with hard ones; the per-section breakdown is therefore mandatory, not optional.

## 2026-08-28: Zero-shot base as the control; one-shot prompted base as an optional second control
**Context:** A zero-shot base model loses many pairs on format alone, which can hide whether fine-tuning changed faithfulness. The fairer question is "fine-tune versus good prompting".
**Decision:** The zero-shot base is the primary control, as in `PROCESS.md`. If GPU time allows, a one-shot base (one fixed training example in the prompt) is generated and judged as a second column. It is never a replacement for the primary control.
**Alternatives rejected:** One-shot as the only control (deviates from the written process mid-project); few-shot with several examples (prompt length on a T4, and picking the examples is another unrecorded choice).

## 2026-08-28: Gemini Flash as judge, with a resumable cache and a stated fallback for the free-tier cap
**Context:** 199 pairs judged twice is about 400 calls. Free-tier daily request caps are in the low hundreds and change without notice. Gemini is a different model family from Qwen, so the judge has no self-preference, and rag-eval-lab used the same judge.
**Decision:** Every verdict is written to disk as it lands and reruns skip finished pairs, so the run can span days. If the cap blocks completion: first Flash-Lite, then a seeded random 120-pair subset, with whichever fallback was used stated in the README next to the numbers.
**Alternatives rejected:** Claude or GPT as judge (paid; otherwise equivalent); single-pass judging to halve the calls (position bias unmeasured); giving up on the swap under quota pressure.

## 2026-08-28: Swap-consistency rule
**Decision:** A pair is kept when both orderings prefer the same model, or both say tie. Any other combination (including tie in one ordering and a preference in the other) is dropped, counted, and reported. A sensitivity line treats dropped pairs as ties.
**Alternatives rejected:** Treating tie-plus-preference as a weak preference (imports the position bias the swap exists to remove).

## 2026-08-28: Greedy decoding, identical for base and tuned
**Decision:** Temperature 0 (greedy), same `max_new_tokens`, same prompt template and system instruction for both models. Recorded in each generations file.
**Alternatives rejected:** Sampling (a second source of variance on top of a 199-pair sample, and non-reproducible outputs).

## 2026-08-28: Adapter saved to Drive, not committed; thin hand-written notebook
**Decision:** The adapter (tens of MB) goes to Google Drive, optionally attached to a GitHub release; the repo commits the training config, loss log and every generation. The Colab notebook is a handful of cells that install, clone and call the package; no logic lives in the notebook.
**Alternatives rejected:** Committing the adapter (binary churn in a docs-and-code repo); a script-built, CI-executed notebook as in rag-eval-lab (this notebook needs a GPU, so CI cannot execute it; CI runs the tests only).

## 2026-08-28: Colab free tier, Kaggle as the fallback GPU
**Decision:** Colab T4. If Colab pre-empts twice, the same notebook runs on Kaggle (30 GPU hours a week). Unsloth needs CUDA, so a Mac is not an option for training.

## 2026-08-28: Pivot to vision, NEU surface defects with Qwen2.5-VL-3B-Instruct
**Status:** Active
**Context:** A live BHP contract (Data Scientist, Computer Vision / VLM: in-house VLM program for crusher and conveyor image analysis) makes a vision fine-tune the highest-value version of this project this week. Recent industrial-defect literature fine-tunes the Qwen-VL family with LoRA for exactly this task shape.
**Decision:** Task becomes defect description and classification on the NEU-DET surface-defect dataset (public, small, six defect classes on steel: the industrial-imagery miniature). Model becomes Qwen2.5-VL-3B-Instruct, QLoRA 4-bit on the free Colab T4. Everything else in PROCESS.md holds: base-model generations first, frozen held-out split, blinded side-by-side with A/B swap, judge with the rubric, human blind pass, failure taxonomy, bootstrap CI.
**Alternatives rejected:** MVTec-AD (licence is CC BY-NC, non-commercial; NEU is cleaner to publish against); PaliGemma-2 (fine, but Qwen-VL is what the defect-detection literature and likely the employer's ecosystem use); staying with the text task this week (serves Heidi, not the live BHP lead).
**Consequences:** The rubric needs a vision rewrite (faithfulness = does the description match the visible defect; localisation stated coarsely, no bounding-box claim). The judge needs images, so the judge model must be multimodal (Gemini Flash accepts images on the free tier).

## 2026-08-28: Training hyperparameters
**Context:** Few knobs, each recorded, defaults from the Unsloth Qwen2.5 notebook unless there is a reason.
**Decision:** LoRA rank 16, alpha 16, dropout 0, on all seven attention and MLP projections; learning rate 2e-4 with linear warmup over the first 5% of steps (15 of about 300) then linear decay; 2 epochs; batch 2 with gradient accumulation 4 (effective 8, about 150 steps per epoch); max sequence length 2,048 tokens; fp16 (the T4 has no bf16); seed 3407; loss on assistant tokens only; validation loss every 25 steps. All values live in one dict in `train.py` and are echoed to `results/train_config.json`.
**Alternatives rejected:** More epochs (1,201 examples, a third pass is where small models start memorising, and validation loss would only confirm it after the GPU time was spent); rank 64 (no evidence it helps at this data size, and the point is method not search); loss on the whole sequence (the model would spend capacity learning to predict the dialogue it is given); max length 1,024 (truncates about 5% of dialogues; 2,048 covers all but a handful).
**Consequences:** No hyperparameter search, stated in the README. If validation loss rises during epoch 2 the adapter from the best checkpoint is used and that is recorded.

## 2026-08-28: Training run outcome, recorded against the hyperparameter entry
**What happened:** 300 steps in 15 min 20 s on the T4. Unsloth dropped 1 of 1,201 training rows whose 1,509-word dialogue exceeded 2,048 tokens (the answer turn was truncated away), so 1,200 were trained on; `train_config.json` reports 1,201 because it counts before that filter. Warmup came out at 16 steps, not the 15 written above (151 steps per epoch, not 150). Validation loss fell 1.62 to 1.38 and flattened over the last 75 steps without rising; the final checkpoint was the best. One gradient-norm spike (2.3) at the epoch boundary, recovered in one step.
**Consequence:** No overfitting at 2 epochs, so the epoch decision stands. The dropped row and the warmup count are recorded here rather than silently corrected.

## 2026-08-28: Encounter-level leakage found after training; five held-out rows excluded from evaluation
**Context:** The first tuned output examined (`test1:0`) stated an age and a date that were in the reference note but not in the dialogue. Investigating, the dialogue-only duplicate check had missed a second kind of overlap: the same source note behind different dialogues across the official split. 28 held-out reference notes match a training note exactly; 24 of those are short boilerplate ("No known drug allergies") that recurs across unrelated encounters and is the task itself, not leakage. Four long notes match exactly and one at Jaccard 0.83: five held-out rows share an encounter with training.
**Decision:** `data.cross_split_note_duplicates` now drops held-out rows whose reference note (8 or more words) exactly or nearly matches a training note; short identical notes are kept and listed in `holdout_ids.json`. Held-out set is 194. The ids and their training matches are in the file. The model was trained before this was found, so the exclusion applies to evaluation only; the five rows stay in the committed generations files (both models generated them) and are simply not paired for judging.
**Alternatives rejected:** Retraining with the five training rows removed (the adapter would change for five examples out of 1,200, and the honest record of what happened is worth more than a cleaner story); keeping the rows and footnoting them (a reader would have to trust the footnote); dropping the boilerplate matches too (that would remove the allergy and medication sections almost entirely, and identical short notes are the correct output, not leakage).
**Consequences:** The frozen-ids rule in this file was amended after training, which is exactly what it exists to prevent; the amendment is a removal, applied before any verdict was produced, and is recorded here with the ids. Two checks are needed for this dataset, not one, and the README says so.

## 2026-08-28: Memorised specifics in tuned outputs, recorded as a finding to be judged, not fixed
**Context:** After excluding the five contaminated rows, the tuned model still states an exact age that appears in the reference note and nowhere in the dialogue (in digits or in words) in 7 held-out rows; the base model does so far less. MTSamples notes have been public since the 2000s and are plausibly in Qwen2.5's pretraining; fine-tuning into MTSamples style may surface memorised text. Not proven; the alternative is inference from context, which the taxonomy pass will check case by case.
**Decision:** No change to the pipeline. These are the cases the faithfulness dimension (judged against the dialogue, not the reference) and the "hallucinated fact" label exist to catch, and ROUGE-L will reward them, which is one more reason ROUGE is a sanity check only. The write-up reports the count and reads the 7 cases.
**Alternatives rejected:** Filtering such outputs (would hide the behaviour the evaluation is for); switching base model (untestable claim that another model's pretraining is cleaner).

## 2026-08-29: Judge model pinned to gemini-3.6-flash
**Context:** The free-tier Flash model assumed when the judge was written (gemini-2.5-flash) is closed to new API keys; the API itself recommended gemini-3.6-flash. The key can also reach gemini-3.5-flash-lite.
**Decision:** Pin `gemini-3.6-flash` as the judge and record it on every verdict row; `gemini-3.5-flash-lite` is the quota fallback named in the earlier entry. A dated version name rather than `gemini-flash-latest`, so a rerun next year judges with the same model or fails loudly.
**Alternatives rejected:** `gemini-flash-latest` (silently changes the judge over time).

## 2026-08-29: Judge runs on prepaid Gemini credit, not a free tier
**Context:** Every Flash model on a fresh API key returned "prepayment credits are depleted"; Google no longer attaches free quota to new keys. The earlier entry's fallback chain (Flash-Lite, then a subset) does not help when the whole key has no quota.
**Decision:** AUD 25 of prepaid credit added by the owner. The full run is about 388 calls of roughly 1,500 input and 150 output tokens, well under one dollar at Flash pricing; the README states the cost. Supersedes the "free tier" wording in the two judge entries above.
**Alternatives rejected:** Claude as judge (equally paid, and it would break family-independence continuity with rag-eval-lab); a smaller judged subset to fit a free tier that does not exist.

## 2026-08-30: Correction to the memorised-specifics count
**What happened:** The 2026-08-28 entry reported 7 held-out rows where the tuned model states an age absent from the dialogue. That check only tested the first number-word found in the dialogue; a stricter check (any number-word whose tens digit matches) finds 2 such rows. The judge scored both faithfulness 5, so it did not catch them either. The earlier entry stands as written; this one supersedes its count.

## 2026-08-30: Failure taxonomy labelled by the agent, audited by the owner
**Context:** PROCESS.md planned hand labelling by the owner. Eighty-eight losses is about an hour of careful reading, and the owner's time this weekend went to the blind pass and to another project.
**Decision:** The implementing agent (Claude) labelled all 88 from the dialogue, both outputs and the judge's two reasons, with one dominant label per pair; provenance is stated at the top of `results/losses.md` and in the README. The owner audits a seeded random sample of 15 (`notes/audit_sample.json`) and the agreement rate is published. Below 12 of 15 agreement the table is downgraded to "indicative" in the README and the owner relabels the disputed categories.
**Alternatives rejected:** Asking the judge to label its own losses (a second unvalidated opinion from the instrument under test); leaving the table empty (the most useful table in the repo would be missing); the owner labelling all 88 later (the write-up would wait on it for no gain in rigour over an audited sample).
**Consequences:** The labels are one reader's, and not a clinician's, stated as such.
