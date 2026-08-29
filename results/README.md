# results

Committed outputs, in the order they were produced.

| File | Step | What it is |
|---|---|---|
| `generations_base.jsonl` | 2 | Base model outputs, all 199 official test dialogues (194 used after the note-level duplicate check), greedy, one JSON line each with settings and prompt fingerprint |
| `train_config.json`, `train_log.jsonl` | 3 | Hyperparameters, row counts, timing; train and validation loss every 25 steps |
| `generations_tuned.jsonl` | 4 | Tuned model outputs, same prompts (fingerprints match) |
| `blinding_key.json` | 5 | Which side is the tuned model per pair; read only by the scoring code |
| `human_pack.md` | 5 | The author's blind pass on 30 pairs, with a corrections log at the top |
| `judge_verdicts.jsonl` | 5 | 388 Gemini verdicts, both orderings per pair, raw reply kept on every row |
| `losses.md` | 6 | Every kept pair the tuned model lost, for hand labelling |
| `metrics.json`, `metrics.md` | 6 | Everything in the README's results section |

The adapter (about 70 MB) is on the author's Drive, not committed.
