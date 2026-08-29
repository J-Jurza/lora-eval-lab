---
paths:
  - "**/*.md"
---
<!-- source: agent-skills/rules/prose-style.md, version 2026-08-29. Distilled from the
nb-annotate skill (rules 2, 3, 6 to 9), the vault CLAUDE.md style rules, and the
lora-eval-lab honesty rule. Edit the source and re-run bin/rules-export. -->

# Prose style (house rules, apply when writing or editing any .md file)

Written for a sceptical senior engineer reading fast.

- **Australian English** (modelling, colour, prioritise, catalogue). Quoted identifiers and
  library arguments keep their spelling.
- **No em dashes**, no `--` substitutes. Use a colon, a comma, or two sentences. **No
  semicolons in prose.**
- **No filler**: no throat-clearing openers ("It is worth noting", "Let's dive in"), no
  moralising closers ("This is a powerful result"), no recap loops, no hedging unless
  something is genuinely uncertain, no vague attribution ("studies show") without a
  citation. Every sentence carries information; if removing it loses nothing, remove it.
- **Concrete over abstract**: numbers, file names, commands. "3+ files" beats "several".
- **Never narrate the alternative you rejected in the running text.** State the fact and
  stop. Rejected alternatives belong in DECISIONS.md.
- **Structure**: tables for comparisons and mappings, bullets for lists of three or more,
  code blocks for every command, path and snippet, bold only for a term being defined or a
  decision rule, headings as noun phrases or short action phrases.
- **No blobs**: paragraphs of two or three sentences, blank line between them. A bullet
  that carries its own caveats becomes a bold lead-in with nested sub-bullets, one fact
  per sub-bullet, never a summary that drops a fact. One level of nesting normally, two at
  most; past that, use `###` sub-headings.
- **Honesty rule for anything public**: never word portfolio work as production
  experience. Every number traces to a command and a committed result. A negative result is
  reported as negative, an interval as an interval, a limitation next to the metric it
  limits.
- **Docs follow code**: a doc that describes behaviour is updated in the same commit as
  the behaviour. A stale guide misleads the next reader with more authority than code.
