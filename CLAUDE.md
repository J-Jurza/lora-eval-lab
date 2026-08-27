# lora-eval-lab: agent briefing

Read `README.md`, `PROCESS.md` and `DECISIONS.md` first. This repo belongs to a job search
whose rules live in an Obsidian vault; the ones that bind here:

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

Vault context for the human side of this project:
`Work/Career/Job Search 2026-08/Strategy/58 - Learning Path (Projects, Courses, Profile Updates).md`
(Project 1) and `Work/Career/Job Search 2026-08/Strategy/43 - Game Plan (2026-08-26).md` section 6.
