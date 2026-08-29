"""
Figures for the README and Post 2, from committed results only.

Regenerate: python tools/make_figures.py (needs the dev extra: pip install -e ".[dev]").
The judging-loop diagram is Mermaid (docs/figures/fig4_judging_loop.mmd); render it with
`npx -y -p @mermaid-js/mermaid-cli mmdc -i docs/figures/fig4_judging_loop.mmd -o docs/figures/fig4_judging_loop.png -c docs/figures/mermaid.config.json -s 3 -b white -w 1500`.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ----------------------------------------------------------------------------
# Data and style tokens
# ----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
m = json.load(open(ROOT / "results/metrics.json"))
log = [json.loads(l) for l in open(ROOT / "results/train_log.jsonl")]

SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8b8a86"
GRID = "#e6e5e1"
BASE, TUNED = "#2a78d6", "#eb6834"      # categorical slots 1 and 2, validated
DEEMPH = "#c9c8c3"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 12,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "axes.edgecolor": GRID,
    "axes.linewidth": 1,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRID,
    "grid.linewidth": 1,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
})


def rounded_bar(ax, x, height, width, color, bottom=0.0):
    """A bar with a 4px-style rounded data end and a square baseline."""
    r = min(width * 0.18, height * 0.5) if height > 0 else 0
    ax.add_patch(FancyBboxPatch(
        (x - width / 2, bottom), width, height,
        boxstyle=f"round,pad=0,rounding_size={r}", fc=color, ec="none", mutation_aspect=1,
    ))
    ax.add_patch(plt.Rectangle((x - width / 2, bottom), width, min(height, r), fc=color, ec="none"))


def title(fig, claim, sub):
    """Claim as the title, one muted line under it, both left-aligned."""
    fig.text(0.04, 0.95, claim, fontsize=14, weight="semibold", color=INK, ha="left", va="top")
    fig.text(0.04, 0.885, sub, fontsize=11, color=INK2, ha="left", va="top")


# ----------------------------------------------------------------------------
# Figure 1: ROUGE-L and blind preference, base vs tuned
# ----------------------------------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), dpi=200)
fig.subplots_adjust(top=0.78, bottom=0.14, left=0.08, right=0.97, wspace=0.35)
r = m["rates"]; lo, hi = m["win_rate_ci"]
W = 0.34

ax = axes[0]
ax.bar([0, 1], [m["rouge_l"]["base"], m["rouge_l"]["tuned"]], width=W, color=[BASE, TUNED])
for i, v in enumerate([m["rouge_l"]["base"], m["rouge_l"]["tuned"]]):
    ax.text(i, v + 0.012, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=12)
ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, 0.34)
ax.set_xticks([0, 1], ["Base model", "Fine-tuned"]); ax.set_yticks([0, 0.1, 0.2, 0.3])
ax.set_ylabel("ROUGE-L F1")
ax.set_title("ROUGE-L against the reference note", loc="left", fontsize=12, color=INK, pad=10)

ax = axes[1]
ax.bar([0, 1], [r["base"], r["tuned"]], width=W, color=[BASE, TUNED])
ax.errorbar([1], [r["tuned"]], yerr=[[r["tuned"] - lo], [hi - r["tuned"]]], fmt="none", ecolor=INK, elinewidth=1.5, capsize=5, capthick=1.5)
ax.text(0, r["base"] + 0.015, f"{r['base']*100:.1f}%", ha="center", va="bottom", color=INK, fontsize=12)
ax.text(1.28, r["tuned"], f"{r['tuned']*100:.1f}%", ha="left", va="center", color=INK, fontsize=12)
ax.axhline(0.5, color=INK2, lw=1); ax.text(-0.55, 0.512, "50%", color=INK2, fontsize=10, va="bottom")
ax.set_xlim(-0.6, 1.9); ax.set_ylim(0, 0.62)
ax.set_xticks([0, 1], ["Base model", "Fine-tuned"]); ax.set_yticks([0, 0.2, 0.4, 0.6], ["0%", "20%", "40%", "60%"])
ax.set_ylabel("Share of kept pairs preferred")
ax.set_title("Blind preference (95% interval shown)", loc="left", fontsize=12, color=INK, pad=10)

title(fig, "Overlap with the reference and blind preference, base model versus fine-tuned",
      "171 held-out pairs, each judged twice with the order swapped.")
fig.savefig(OUT / "fig1_rouge_vs_preference.png"); plt.close(fig)

# ----------------------------------------------------------------------------
# Figure 2: loss curve
# ----------------------------------------------------------------------------

tr = [(e["step"], e["loss"]) for e in log if "loss" in e]
ev = [(e["step"], e["eval_loss"]) for e in log if "eval_loss" in e]
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200)
fig.subplots_adjust(top=0.78, bottom=0.14, left=0.08, right=0.9)
for pts, c, name in [(tr, DEEMPH, "training loss"), (ev, TUNED, "validation loss, 98 held-back pairs")]:
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=2, solid_joinstyle="round", solid_capstyle="round", label=name, zorder=2)
    ax.plot(xs, ys, "o", ms=8, mfc=c, mec=SURFACE, mew=2, zorder=3)
ax.text(302, ev[-1][1], f"{ev[-1][1]:.2f}", color=INK, va="center", ha="left", fontsize=11)
ax.text(302, tr[-1][1], f"{tr[-1][1]:.2f}", color=INK2, va="center", ha="left", fontsize=11)
ax.axvline(150, color=GRID, lw=1, zorder=1); ax.text(152, 1.86, "epoch 2", color=MUTED, fontsize=10)
ax.set_xlim(15, 330); ax.set_ylim(1.2, 1.9); ax.set_yticks([1.2, 1.4, 1.6, 1.8])
ax.set_xlabel("training step")
ax.set_ylabel("cross-entropy loss")
ax.legend(frameon=False, loc="lower left", fontsize=11)
title(fig, "Training and validation loss over 300 steps",
      "QLoRA on Qwen2.5-1.5B-Instruct, 1,200 training pairs, validation on 98 held-back pairs, one free T4.")
fig.savefig(OUT / "fig2_loss_curve.png"); plt.close(fig)

# ----------------------------------------------------------------------------
# Figure 3: taxonomy
# ----------------------------------------------------------------------------

tax = m["taxonomy"]
order = ["hallucinated fact", "omitted fact", "format break", "other", "wrong section"]
labels = ["Invented a fact the patient never said", "Left out a relevant fact", "Repetition loop or not a note", "Style only", "Wrong section"]
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
fig.subplots_adjust(top=0.78, bottom=0.14, left=0.36, right=0.95)
ax.grid(False); ax.grid(True, axis="x", color=GRID, lw=1)
ys = list(range(len(order)))[::-1]
for y, k, lab in zip(ys, order, labels):
    v = tax.get(k, 0); c = TUNED if k == "hallucinated fact" else DEEMPH
    ax.add_patch(FancyBboxPatch((0, y - 0.28), v, 0.56, boxstyle="round,pad=0,rounding_size=0.28", fc=c, ec="none"))
    ax.add_patch(plt.Rectangle((0, y - 0.28), min(v, 0.5), 0.56, fc=c, ec="none"))
    ax.text(v + 0.8, y, str(v), va="center", color=INK, fontsize=12)
ax.set_yticks(ys, labels); ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 48); ax.set_ylim(-0.7, len(order) - 0.3); ax.set_xticks([0, 10, 20, 30, 40])
ax.set_xlabel("pairs the fine-tuned model lost, 88 in total")
title(fig, "Dominant failure in the 88 pairs the fine-tuned model lost",
      "One label per pair, assigned by reading the conversation and both notes.")
fig.savefig(OUT / "fig3_taxonomy.png"); plt.close(fig)

# ----------------------------------------------------------------------------
# Figure 4: judging loop (Mermaid source; render with the CLI, see the docstring)
# ----------------------------------------------------------------------------

# The Mermaid source and config live in docs/figures and are rendered by the CLI (see docstring).

print("wrote", sorted(p.name for p in OUT.glob("fig*")))
