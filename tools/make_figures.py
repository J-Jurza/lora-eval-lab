"""Figures for Post 2, from committed results only. Regenerate: python tools/make_figures.py (needs the dev extra: pip install -e ".[dev]")"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
m = json.load(open(ROOT / "results/metrics.json"))
log = [json.loads(l) for l in open(ROOT / "results/train_log.jsonl")]

BASE, TUNED, INK, GREY = "#4a6fa5", "#d9822b", "#222222", "#8a8a8a"
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white"})

# 1. ROUGE up, preference down
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), dpi=200)
r = m["rates"]; lo, hi = m["win_rate_ci"]
ax = axes[0]
ax.bar(["Base", "Tuned"], [m["rouge_l"]["base"], m["rouge_l"]["tuned"]], color=[BASE, TUNED], width=0.55)
for i, v in enumerate([m["rouge_l"]["base"], m["rouge_l"]["tuned"]]): ax.text(i, v + 0.008, f"{v:.2f}", ha="center", color=INK)
ax.set_title("Overlap with the reference (ROUGE-L F1)\nwent up by half", loc="left", fontsize=12)
ax.set_ylim(0, 0.36); ax.set_ylabel("ROUGE-L F1")
ax = axes[1]
vals = [r["base"], r["tuned"]]
ax.bar(["Base", "Tuned"], vals, color=[BASE, TUNED], width=0.55)
ax.errorbar([1], [r["tuned"]], yerr=[[r["tuned"] - lo], [hi - r["tuned"]]], fmt="none", ecolor=INK, capsize=6, lw=1.5)
ax.text(0, vals[0] + 0.012, f"{vals[0]*100:.1f}%", ha="center", color=INK)
ax.text(0.68, vals[1] + 0.005, f"{vals[1]*100:.1f}%", ha="center", color=INK)
ax.axhline(0.5, color=GREY, ls=":", lw=1); ax.text(1.42, 0.505, "parity", color=GREY, fontsize=10, va="bottom", ha="right")
ax.set_title("Blind preference over 171 pairs\nwent down (95% interval shown)", loc="left", fontsize=12)
ax.set_ylim(0, 0.66); ax.set_ylabel("Share of pairs preferred")
fig.suptitle("The overlap metric rewarded the fine-tune. Blind readers did not.", x=0.02, ha="left", fontsize=14, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(OUT / "fig1_rouge_vs_preference.png"); plt.close(fig)

# 2. Loss curve
tr = [(e["step"], e["loss"]) for e in log if "loss" in e]; ev = [(e["step"], e["eval_loss"]) for e in log if "eval_loss" in e]
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
ax.plot(*zip(*tr), marker="o", color=GREY, label="training loss")
ax.plot(*zip(*ev), marker="o", color=TUNED, label="validation loss (98 held-back pairs)")
ax.axvline(150, color=GREY, ls=":", lw=1); ax.text(152, 1.86, "epoch 2 starts", color=GREY, fontsize=10)
ax.set_xlabel("training step (300 total, 15 minutes on a T4)"); ax.set_ylabel("cross-entropy loss"); ax.set_ylim(1.2, 1.9)
ax.legend(frameon=False, loc="lower left")
ax.set_title("Validation loss fell from 1.62 to 1.38 and flattened. It measured the wrong question.", loc="left", fontsize=13)
fig.tight_layout(); fig.savefig(OUT / "fig2_loss_curve.png"); plt.close(fig)

# 3. Taxonomy
tax = m["taxonomy"]; order = ["hallucinated fact", "omitted fact", "format break", "other", "wrong section"]
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
vals = [tax.get(k, 0) for k in order]
colors = [TUNED if k == "hallucinated fact" else GREY for k in order]
ax.barh(order[::-1], vals[::-1], color=colors[::-1])
for i, v in enumerate(vals[::-1]): ax.text(v + 0.8, i, str(v), va="center", color=INK)
ax.set_xlim(0, 50); ax.set_xlabel("pairs the fine-tuned model lost (88 in total)")
ax.set_title("Why it lost: 41 of 88 losses were a fact the patient never said", loc="left", fontsize=13)
fig.tight_layout(); fig.savefig(OUT / "fig3_taxonomy.png"); plt.close(fig)

# 4. Blind judging loop diagram (boxes, no mermaid CLI available)
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200); ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
def box(x, y, w, h, text, fc="#f4f4f4", ec=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11, color=INK)
def arrow(x1, y1, x2, y2): ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=INK, lw=1.3))
box(0.2, 3.3, 2.2, 1.2, "194 sealed exam\nconversations")
box(3.0, 4.0, 2.0, 0.8, "base note", fc="#e3ebf5"); box(3.0, 2.6, 2.0, 0.8, "tuned note", fc="#fbe9d6")
arrow(2.4, 4.1, 3.0, 4.4); arrow(2.4, 3.7, 3.0, 3.0)
box(5.4, 3.0, 2.6, 1.6, "judge sees A and B,\nkey sealed,\njudged twice with\nthe order swapped")
arrow(5.0, 4.4, 5.4, 4.1); arrow(5.0, 3.0, 5.4, 3.4)
box(8.3, 3.2, 1.6, 1.2, "kept only if\nboth verdicts\nagree"); arrow(8.0, 3.8, 8.3, 3.8)
box(5.4, 1.0, 2.6, 0.9, "owner scores 30 pairs\nblind, before the judge", fc="#eef5e9"); arrow(6.7, 1.9, 6.7, 3.0)
ax.text(8.3, 2.3, "23 of 194 dropped:\nall favoured the\nleft slot", fontsize=10, color=GREY, va="center")
ax.set_title("Blind judging: the key stays sealed, every pair is judged twice, a human anchors the judge", loc="left", fontsize=13)
fig.tight_layout(); fig.savefig(OUT / "fig4_judging_loop.png"); plt.close(fig)
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
