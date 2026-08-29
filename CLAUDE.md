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

The task pivoted to vision on 28 Aug (see DECISIONS.md): NEU-DET defects, Qwen2.5-VL-3B,
same evaluation design. A live BHP Computer Vision / VLM contract is the reason; urgency is
real but the honesty and explain-every-step rules do not relax.

Vault context for the human side of this project:
`Work/Career/Job Search 2026-08/Strategy/58 - Learning Path (Projects, Courses, Profile Updates).md`
(Project 1) and `Work/Career/Job Search 2026-08/Strategy/43 - Game Plan (2026-08-26).md` section 6.

## Working rules

<!-- four-rules: the Karpathy preamble, identical in every repo. Change it in agent-skills, never here. -->
- **Think before coding.** State assumptions; when a request has two readings, ask and propose the one you would pick. Name a simpler approach when you see one. Never code through confusion.
- **Simplicity first.** The minimum code that solves the problem: no speculative abstraction, configurability, or error handling for cases that cannot happen. If 200 lines could be 50, rewrite.
- **Surgical changes.** Every changed line traces to the request. Match the existing style, leave adjacent code alone, mention dead code rather than deleting it, and remove only the orphans your own change created.
- **Goal-driven execution.** Turn the task into a check before starting: "fix the bug" is "write the failing test, then make it pass". Multi-step work gets a short plan with a verification per step.
- **Self-check**: fewer unnecessary diff lines, fewer rewrites, questions before mistakes.

## Knowledge base

The Obsidian dev vault at `/Users/honzik/code/obsidian-dev-vault/coding_projects/` is the hub this repo hangs off. When a task needs background (a book, a paper, a technique, a decision made in another project), read `Wiki/_Meta/index.md` there first, then the doc it points to, and cite vault docs by path. This repo's vault-side notes are `Projects/lora-eval-lab/`: `CONTEXT.md` and `DECISIONS.md` are agent-maintained, `ideas.md` and `research.md` are the owner's. The vault is readable from here through `additionalDirectories` in `.claude/settings.local.json`; never edit it from this repo. Hand learnings worth keeping to the vault agent for `Wiki/3. Project Knowledge/`.
