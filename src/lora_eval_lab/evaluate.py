"""
Turn verdicts into numbers: swap-consistency filter, win rate with a bootstrap interval,
per-dimension scores, per-section breakdown, ROUGE-L sanity check, human-judge agreement,
and the hand-labelled failure taxonomy over every loss.

Every metric is written from its definition and pinned by a hand-computed test.

Owns: metric definitions, results/metrics.json and results/metrics.md, results/losses.md.
Breaks if: verdict rows lack `preferred_model` (unparsed judge replies are counted as
dropped, never silently skipped).
"""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from lora_eval_lab import data, judge

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------

RESULTS_DIR = data.ROOT / "results"
LOSSES_PATH = RESULTS_DIR / "losses.md"
METRICS_JSON = RESULTS_DIR / "metrics.json"
METRICS_MD = RESULTS_DIR / "metrics.md"

BOOT_SAMPLES = 10_000
BOOT_SEED = 20260828
OUTCOMES = ("tuned", "base", "tie")
TAXONOMY = ("hallucinated fact", "omitted fact", "wrong section", "format break", "other")


# ----------------------------------------------------------------------------
# Swap-consistency filter
# ----------------------------------------------------------------------------

def consensus(verdicts: list[dict]) -> tuple[dict[str, str], Counter]:
    """
    Keep one outcome per pair when both orderings agree.

    Args:
        verdicts (list[dict]): Rows from judge_verdicts.jsonl.

    Returns:
        tuple: ({id: tuned|base|tie} for kept pairs, Counter of drop reasons).
    """
    by_id: dict[str, dict[bool, str | None]] = defaultdict(dict)
    for v in verdicts:
        by_id[v["id"]][v["swapped"]] = v.get("preferred_model")

    kept, dropped = {}, Counter()
    for i, both in by_id.items():
        if len(both) < 2:
            dropped["missing one ordering"] += 1
        elif None in both.values():
            dropped["unparsed reply"] += 1
        elif both[False] != both[True]:
            dropped["inconsistent across swap"] += 1
        else:
            kept[i] = both[False]
    return kept, dropped


# ----------------------------------------------------------------------------
# Rates and the bootstrap
# ----------------------------------------------------------------------------

def rates(outcomes: list[str]) -> dict[str, float]:
    """Share of tuned wins, base wins and ties; zeros on an empty list."""
    n = len(outcomes)
    c = Counter(outcomes)
    return {k: (c[k] / n if n else 0.0) for k in OUTCOMES} | {"n": n}


def bootstrap_ci(values: list[float], samples: int = BOOT_SAMPLES, seed: int = BOOT_SEED) -> tuple[float, float]:
    """
    Percentile bootstrap 95% interval for the mean of `values`.

    Args:
        values (list[float]): One number per pair (1.0 for a win, 0.0 otherwise, or a
            paired difference).
        samples (int): Resamples.
        seed (int): RNG seed.

    Returns:
        tuple[float, float]: (2.5th, 97.5th) percentiles of the resampled means.
    """
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(rng.choice(values) for _ in range(n)) / n for _ in range(samples))
    lo = means[int(0.025 * samples)]
    hi = means[min(samples - 1, int(0.975 * samples))]
    return (lo, hi)


# ----------------------------------------------------------------------------
# Per-dimension scores
# ----------------------------------------------------------------------------

def model_scores(v: dict, tuned_side: str) -> dict[str, dict[str, int]]:
    """
    Read one verdict's A/B scores back into tuned/base terms.

    Args:
        v (dict): A verdict row with A, B score dicts and `swapped`.
        tuned_side (str): "A" or "B" from the blinding key.

    Returns:
        dict: {"tuned": {dim: score}, "base": {dim: score}}.
    """
    side = tuned_side
    if v["swapped"]:
        side = "B" if side == "A" else "A"
    other = "B" if side == "A" else "A"
    return {"tuned": v[side], "base": v[other]}


def dimension_table(verdicts: list[dict], key: dict[str, str], kept: dict[str, str]) -> dict:
    """
    Mean score per dimension for each model over kept pairs, with the paired difference.

    Args:
        verdicts (list[dict]): All verdict rows.
        key (dict[str, str]): Blinding key.
        kept (dict[str, str]): Kept pair ids (from consensus).

    Returns:
        dict: {dim: {"tuned": mean, "base": mean, "diff": mean, "diff_ci": (lo, hi)}}.
    """
    per_pair: dict[str, dict[str, dict[str, list[int]]]] = defaultdict(
        lambda: {"tuned": defaultdict(list), "base": defaultdict(list)}
    )
    for v in verdicts:
        if v["id"] not in kept or "A" not in v:
            continue
        ms = model_scores(v, key[v["id"]])
        for model in ("tuned", "base"):
            for d in judge.DIMENSIONS:
                per_pair[v["id"]][model][d].append(ms[model][d])

    table = {}
    for d in judge.DIMENSIONS:
        tuned = [sum(p["tuned"][d]) / len(p["tuned"][d]) for p in per_pair.values()]
        base = [sum(p["base"][d]) / len(p["base"][d]) for p in per_pair.values()]
        diffs = [t - b for t, b in zip(tuned, base)]
        n = len(diffs)
        table[d] = {
            "tuned": sum(tuned) / n if n else 0.0,
            "base": sum(base) / n if n else 0.0,
            "diff": sum(diffs) / n if n else 0.0,
            "diff_ci": bootstrap_ci(diffs),
        }
    return table


# ----------------------------------------------------------------------------
# ROUGE-L
# ----------------------------------------------------------------------------

def lcs_length(a: list[str], b: list[str]) -> int:
    """Length of the longest common subsequence of two token lists."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def rouge_l(candidate: str, reference: str) -> float:
    """
    ROUGE-L F1 on whitespace tokens, lower-cased.

    Args:
        candidate (str): Model output.
        reference (str): Reference note.

    Returns:
        float: F1 of LCS-based precision and recall, 0.0 if either side is empty.
    """
    c, r = candidate.lower().split(), reference.lower().split()
    if not c or not r:
        return 0.0
    lcs = lcs_length(c, r)
    if lcs == 0:
        return 0.0
    p, rec = lcs / len(c), lcs / len(r)
    return 2 * p * rec / (p + rec)


# ----------------------------------------------------------------------------
# Agreement
# ----------------------------------------------------------------------------

def agreement(a: list[str], b: list[str]) -> dict[str, float]:
    """
    Raw agreement and Cohen's kappa between two raters' labels.

    Args:
        a, b (list[str]): Labels from OUTCOMES, same length and order.

    Returns:
        dict: {"n", "raw", "kappa"}; kappa is 0.0 when expected agreement is 1.
    """
    n = len(a)
    if n == 0:
        return {"n": 0, "raw": 0.0, "kappa": 0.0}
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in OUTCOMES) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 0.0
    return {"n": n, "raw": po, "kappa": kappa}


def human_outcomes(pack_text: str, key: dict[str, str]) -> dict[str, str]:
    """Human preferences from the filled pack, mapped to tuned/base/tie by the key."""
    return {v["id"]: judge.to_model(v["preference"], key[v["id"]]) for v in judge.parse_human_pack(pack_text)}


# ----------------------------------------------------------------------------
# Failure taxonomy
# ----------------------------------------------------------------------------

LABEL_RE = re.compile(r"^LABEL:\s*(.+?)\s*$", re.IGNORECASE)


def losses_pack(pairs: list[dict], kept: dict[str, str], verdicts: list[dict]) -> str:
    """
    Markdown listing every kept pair the tuned model lost, with a LABEL line to fill.

    Args:
        pairs (list[dict]): From judge.build_pairs.
        kept (dict[str, str]): Consensus outcomes.
        verdicts (list[dict]): For the judge's reasons.

    Returns:
        str: The pack.
    """
    reasons = defaultdict(list)
    for v in verdicts:
        if v.get("reason"):
            reasons[v["id"]].append(v["reason"])
    out = [
        "# Losses: pairs where the base model was preferred\n",
        f"Label each with one of: {', '.join(TAXONOMY)}. Fill the LABEL line exactly.\n",
    ]
    for p in pairs:
        if kept.get(p["id"]) != "base":
            continue
        out += [
            f"\n## Loss {p['id']}\n",
            f"**Section:** {data.SECTION_NAMES[p['section']]}\n",
            f"**Conversation:**\n\n```\n{p['dialogue']}\n```\n",
            f"**Reference:**\n\n```\n{p['reference']}\n```\n",
            f"**Tuned (lost):**\n\n```\n{p['tuned']}\n```\n",
            f"**Base (won):**\n\n```\n{p['base']}\n```\n",
            "**Judge said:** " + " / ".join(reasons.get(p["id"], [])) + "\n",
            "LABEL: \n",
        ]
    return "\n".join(out)


def parse_labels(text: str) -> dict[str, str]:
    """Read filled LABEL lines back out of the losses pack, keyed by pair id."""
    labels, current = {}, None
    for line in text.splitlines():
        if line.startswith("## Loss "):
            current = line[len("## Loss "):].strip()
            continue
        m = LABEL_RE.match(line.strip())
        if m and current and m.group(1):
            label = m.group(1).lower()
            if label not in TAXONOMY:
                raise ValueError(f"{current}: label {label!r} not in taxonomy")
            labels[current] = label
    return labels


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------

def per_section(pairs: list[dict], kept: dict[str, str]) -> dict[str, dict]:
    """Win, tie and base rates per section over kept pairs, sorted by n."""
    groups = defaultdict(list)
    for p in pairs:
        if p["id"] in kept:
            groups[p["section"]].append(kept[p["id"]])
    table = {s: rates(o) for s, o in groups.items()}
    return dict(sorted(table.items(), key=lambda kv: -kv[1]["n"]))


def compute(pairs: list[dict], verdicts: list[dict], key: dict[str, str], human: dict[str, str], labels: dict[str, str]) -> dict:
    """Assemble every metric into one dict."""
    kept, dropped = consensus(verdicts)
    outcomes = [kept[p["id"]] for p in pairs if p["id"] in kept]
    wins = [1.0 if o == "tuned" else 0.0 for o in outcomes]

    all_ids = [p["id"] for p in pairs if p["id"] in {v["id"] for v in verdicts}]
    sens_outcomes = [kept.get(i, "tie") for i in all_ids]

    human_ids = [i for i in human if i in kept]
    return {
        "pairs_judged": len(all_ids),
        "kept": len(kept),
        "dropped": dict(dropped),
        "rates": rates(outcomes),
        "win_rate_ci": bootstrap_ci(wins),
        "sensitivity_dropped_as_ties": rates(sens_outcomes),
        "dimensions": dimension_table(verdicts, key, kept),
        "per_section": per_section(pairs, kept),
        "rouge_l": {
            "base": sum(rouge_l(p["base"], p["reference"]) for p in pairs) / len(pairs) if pairs else 0.0,
            "tuned": sum(rouge_l(p["tuned"], p["reference"]) for p in pairs) / len(pairs) if pairs else 0.0,
        },
        "human_vs_judge": agreement([human[i] for i in human_ids], [kept[i] for i in human_ids]),
        "human_rates": rates(list(human.values())),
        "taxonomy": dict(Counter(labels.values())),
        "losses_labelled": f"{len(labels)}/{sum(o == 'base' for o in outcomes)}",
    }


def render(m: dict) -> str:
    """Markdown tables for the README."""
    r, lo, hi = m["rates"], *m["win_rate_ci"]
    lines = [
        "# Metrics\n",
        f"Pairs judged {m['pairs_judged']}, kept after swap consistency {m['kept']}, dropped {m['dropped']}.\n",
        "| Outcome | Rate | 95% CI |",
        "|---|---|---|",
        f"| Tuned preferred | {r['tuned']:.3f} | {lo:.3f} to {hi:.3f} |",
        f"| Base preferred | {r['base']:.3f} | |",
        f"| Tie | {r['tie']:.3f} | |",
        f"\nSensitivity, dropped pairs counted as ties: tuned {m['sensitivity_dropped_as_ties']['tuned']:.3f}, "
        f"base {m['sensitivity_dropped_as_ties']['base']:.3f}, tie {m['sensitivity_dropped_as_ties']['tie']:.3f}.\n",
        "| Dimension | Base | Tuned | Diff | 95% CI |",
        "|---|---|---|---|---|",
    ]
    for d, t in m["dimensions"].items():
        lines.append(f"| {d} | {t['base']:.2f} | {t['tuned']:.2f} | {t['diff']:+.2f} | {t['diff_ci'][0]:+.2f} to {t['diff_ci'][1]:+.2f} |")
    lines += ["", "| Section | n | Tuned | Base | Tie |", "|---|---|---|---|---|"]
    for s, t in m["per_section"].items():
        lines.append(f"| {data.SECTION_NAMES[s]} | {t['n']} | {t['tuned']:.2f} | {t['base']:.2f} | {t['tie']:.2f} |")
    h = m["human_vs_judge"]
    lines += [
        "",
        f"ROUGE-L F1 against the reference: base {m['rouge_l']['base']:.3f}, tuned {m['rouge_l']['tuned']:.3f}. "
        "ROUGE rewards overlap, not correctness.\n",
        f"Human vs judge on {h['n']} kept pairs: raw agreement {h['raw']:.2f}, Cohen's kappa {h['kappa']:.2f}.\n",
        f"Failure taxonomy over losses ({m['losses_labelled']} labelled):\n",
        "| Failure | Count |",
        "|---|---|",
    ]
    for label in TAXONOMY:
        lines.append(f"| {label} | {m['taxonomy'].get(label, 0)} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--taxonomy", action="store_true", help="write results/losses.md for hand labelling")
    args = ap.parse_args()

    pairs, key = judge.load_everything()
    verdicts = judge.read_jsonl(judge.VERDICTS_PATH)
    kept, _ = consensus(verdicts)
    if args.taxonomy:
        LOSSES_PATH.write_text(losses_pack(pairs, kept, verdicts))
        print(f"losses pack at {LOSSES_PATH}")
        return

    human = human_outcomes(judge.HUMAN_PACK_PATH.read_text(), key) if judge.HUMAN_PACK_PATH.exists() else {}
    labels = parse_labels(LOSSES_PATH.read_text()) if LOSSES_PATH.exists() else {}
    m = compute(pairs, verdicts, key, human, labels)
    METRICS_JSON.write_text(json.dumps(m, indent=1) + "\n")
    METRICS_MD.write_text(render(m))
    print(render(m))


if __name__ == "__main__":
    main()
