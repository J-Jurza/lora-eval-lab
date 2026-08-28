"""Every metric pinned to a value worked by hand; no files, no API."""
import pytest

from lora_eval_lab import evaluate as ev


# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------

def v(id_, swapped, pref, a=None, b=None, reason=""):
    row = {"id": id_, "swapped": swapped, "preferred_model": pref, "reason": reason}
    if a:
        row["A"] = dict(zip(ev.judge.DIMENSIONS, a))
        row["B"] = dict(zip(ev.judge.DIMENSIONS, b))
    return row


# ----------------------------------------------------------------------------
# Swap consistency
# ----------------------------------------------------------------------------

def test_consensus_keeps_agreeing_pairs_and_counts_each_drop_reason():
    verdicts = [
        v("p1", False, "tuned"), v("p1", True, "tuned"),      # kept: tuned
        v("p2", False, "tie"), v("p2", True, "tie"),          # kept: tie
        v("p3", False, "tuned"), v("p3", True, "base"),       # position bias: dropped
        v("p4", False, "tie"), v("p4", True, "tuned"),        # tie + preference: dropped
        v("p5", False, "base"),                               # only one ordering
        v("p6", False, None), v("p6", True, "base"),          # unparsed reply
    ]
    kept, dropped = ev.consensus(verdicts)
    assert kept == {"p1": "tuned", "p2": "tie"}
    assert dropped == {"inconsistent across swap": 2, "missing one ordering": 1, "unparsed reply": 1}


# ----------------------------------------------------------------------------
# Rates and bootstrap
# ----------------------------------------------------------------------------

def test_rates_by_hand():
    # 3 tuned, 1 base, 1 tie out of 5
    r = ev.rates(["tuned", "tuned", "tuned", "base", "tie"])
    assert r == {"tuned": 0.6, "base": 0.2, "tie": 0.2, "n": 5}
    assert ev.rates([]) == {"tuned": 0.0, "base": 0.0, "tie": 0.0, "n": 0}


def test_bootstrap_ci_degenerate_and_containment():
    assert ev.bootstrap_ci([1.0] * 20) == (1.0, 1.0)
    assert ev.bootstrap_ci([]) == (0.0, 0.0)
    wins = [1.0] * 60 + [0.0] * 40           # point estimate 0.60, n = 100
    lo, hi = ev.bootstrap_ci(wins, samples=2000)
    assert lo < 0.60 < hi
    assert 0.48 < lo < 0.56 and 0.64 < hi < 0.72   # normal approx: 0.60 +/- 1.96 * 0.049


def test_bootstrap_is_seeded():
    wins = [1.0, 0.0, 1.0, 1.0, 0.0]
    assert ev.bootstrap_ci(wins, samples=500) == ev.bootstrap_ci(wins, samples=500)


# ----------------------------------------------------------------------------
# Dimension scores
# ----------------------------------------------------------------------------

def test_model_scores_unswaps_correctly():
    row = v("p", True, "tuned", a=(1, 1, 1, 1), b=(5, 5, 5, 5))
    ms = ev.model_scores(row, tuned_side="A")   # swapped, so tuned was shown as B
    assert ms["tuned"]["faithfulness"] == 5 and ms["base"]["faithfulness"] == 1


def test_dimension_table_averages_both_orderings_by_hand():
    key = {"p": "A"}
    verdicts = [
        v("p", False, "tuned", a=(5, 4, 4, 4), b=(3, 4, 2, 4)),   # tuned=A: tuned 5,4,4,4 base 3,4,2,4
        v("p", True, "tuned", a=(3, 2, 2, 4), b=(5, 4, 4, 4)),    # swapped: tuned=B: tuned 5,4,4,4 base 3,2,2,4
    ]
    t = ev.dimension_table(verdicts, key, {"p": "tuned"})
    assert t["faithfulness"]["tuned"] == 5.0 and t["faithfulness"]["base"] == 3.0
    assert t["completeness"]["base"] == pytest.approx(3.0)        # (4 + 2) / 2
    assert t["format"]["diff"] == pytest.approx(2.0)              # 4 - (2 + 2) / 2
    assert t["concision"]["diff"] == 0.0


# ----------------------------------------------------------------------------
# ROUGE-L
# ----------------------------------------------------------------------------

def test_lcs_by_hand():
    assert ev.lcs_length("a b c d".split(), "a c d e".split()) == 3   # a c d
    assert ev.lcs_length("a b".split(), "c d".split()) == 0


def test_rouge_l_by_hand():
    # LCS("the cat sat", "the cat ran") = 2; P = R = 2/3; F1 = 2/3
    assert ev.rouge_l("the cat sat", "The cat ran") == pytest.approx(2 / 3)
    # LCS("a b c", "a b c d") = 3; P = 1, R = 3/4; F1 = 2 * 1 * 0.75 / 1.75 = 0.857142...
    assert ev.rouge_l("a b c", "a b c d") == pytest.approx(6 / 7)
    assert ev.rouge_l("", "a") == 0.0 and ev.rouge_l("x", "a") == 0.0


# ----------------------------------------------------------------------------
# Agreement
# ----------------------------------------------------------------------------

def test_kappa_by_hand():
    # 10 items. Human: 6 tuned, 3 base, 1 tie. Judge: 5 tuned, 4 base, 1 tie.
    # Agreements: positions 0-4 tuned/tuned (5), 6-8 base/base (3), 9 tie/tie (1): po = 0.9
    # pe = (6*5 + 3*4 + 1*1) / 100 = 0.43 ; kappa = (0.9 - 0.43) / 0.57 = 0.824561...
    human = ["tuned"] * 6 + ["base"] * 3 + ["tie"]
    judge_ = ["tuned"] * 5 + ["base"] * 4 + ["tie"]
    a = ev.agreement(human, judge_)
    assert a["n"] == 10 and a["raw"] == pytest.approx(0.9)
    assert a["kappa"] == pytest.approx(0.47 / 0.57)


def test_kappa_zero_when_chance_explains_everything():
    a = ev.agreement(["tuned"] * 4, ["tuned"] * 4)
    assert a["raw"] == 1.0 and a["kappa"] == 0.0


# ----------------------------------------------------------------------------
# Taxonomy pack
# ----------------------------------------------------------------------------

def test_losses_pack_lists_only_losses_and_labels_parse_back():
    pairs = [
        {"id": "p1", "section": "CC", "dialogue": "d", "reference": "r", "base": "b1", "tuned": "t1"},
        {"id": "p2", "section": "CC", "dialogue": "d", "reference": "r", "base": "b2", "tuned": "t2"},
    ]
    kept = {"p1": "base", "p2": "tuned"}
    text = ev.losses_pack(pairs, kept, [v("p1", False, "base", reason="tuned invented a dose")])
    assert "## Loss p1" in text and "## Loss p2" not in text
    assert "tuned invented a dose" in text

    filled = text.replace("LABEL: \n", "LABEL: hallucinated fact\n", 1)
    assert ev.parse_labels(filled) == {"p1": "hallucinated fact"}
    with pytest.raises(ValueError):
        ev.parse_labels(text.replace("LABEL: \n", "LABEL: vibes\n", 1))


# ----------------------------------------------------------------------------
# Per section
# ----------------------------------------------------------------------------

def test_per_section_by_hand():
    pairs = [{"id": f"p{i}", "section": s} for i, s in enumerate(["CC", "CC", "GENHX", "CC"])]
    kept = {"p0": "tuned", "p1": "base", "p2": "tie", "p3": "tuned"}
    t = ev.per_section(pairs, kept)
    assert list(t) == ["CC", "GENHX"]
    assert t["CC"] == {"tuned": 2 / 3, "base": 1 / 3, "tie": 0.0, "n": 3}
