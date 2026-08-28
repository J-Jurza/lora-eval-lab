"""Blinding, pair layout, pack parsing and verdict parsing: no API."""
import json

import pytest

from lora_eval_lab import judge


# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------

def gen(id_, output, sha="abc"):
    return {"id": id_, "output": output, "prompt_sha256": sha}


ROWS = [
    {"id": "test1:0", "section": "CC", "dialogue": "Doctor: why here?\nPatient: cough.", "note": "Cough."},
    {"id": "test1:1", "section": "ALLERGY", "dialogue": "Doctor: allergies?\nPatient: none.", "note": "NKDA."},
]
BASE = [gen("test1:0", "north0"), gen("test1:1", "north1")]
TUNED = [gen("test1:0", "south0"), gen("test1:1", "south1")]


# ----------------------------------------------------------------------------
# Pairs and blinding
# ----------------------------------------------------------------------------

def test_build_pairs_joins_on_id_and_keeps_both_texts():
    pairs = judge.build_pairs(BASE, TUNED, ROWS)
    assert [p["id"] for p in pairs] == ["test1:0", "test1:1"]
    assert pairs[0]["base"] == "north0" and pairs[0]["tuned"] == "south0"
    assert pairs[1]["reference"] == "NKDA."


def test_build_pairs_refuses_mismatched_prompts():
    with pytest.raises(ValueError):
        judge.build_pairs(BASE, [gen("test1:0", "x", sha="other"), TUNED[1]], ROWS)


def test_key_is_reproducible_and_roughly_balanced():
    ids = [f"test1:{i}" for i in range(200)]
    k1, k2 = judge.make_key(ids), judge.make_key(ids)
    assert k1 == k2
    n_a = sum(v == "A" for v in k1.values())
    assert 70 <= n_a <= 130


def test_shown_and_to_model_round_trip():
    pair = {"base": "B-text", "tuned": "T-text"}
    assert judge.shown(pair, "A") == ("T-text", "B-text")
    assert judge.shown(pair, "A", swapped=True) == ("B-text", "T-text")
    assert judge.to_model("A", "A") == "tuned"
    assert judge.to_model("A", "A", swapped=True) == "base"
    assert judge.to_model("B", "A", swapped=True) == "tuned"
    assert judge.to_model("tie", "B") == "tie"


# ----------------------------------------------------------------------------
# Human pack
# ----------------------------------------------------------------------------

def test_human_pack_hides_the_key_and_parses_back():
    pairs = judge.build_pairs(BASE, TUNED, ROWS)
    key = {"test1:0": "B", "test1:1": "A"}
    text = judge.human_pack(pairs, key, ["test1:0", "test1:1"])
    assert "tuned" not in text.lower().replace("fine-tuned", "")
    assert "## Pair test1:0" in text and "**A:**\n\n```\nnorth0" in text

    filled = text.replace(
        "SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: ",
        "SCORES: A 5 4 4 5 | B 3 4 2 4 | PREF: A | REASON: A stuck to the dialogue.",
        1,
    )
    verdicts = judge.parse_human_pack(filled)
    assert len(verdicts) == 1
    assert verdicts[0]["id"] == "test1:0"
    assert verdicts[0]["A"] == {"faithfulness": 5, "completeness": 4, "format": 4, "concision": 5}
    assert verdicts[0]["preference"] == "A"
    assert judge.to_model("A", key["test1:0"]) == "base"


def test_choose_human_ids_is_seeded_subset_in_order():
    ids = [f"test1:{i}" for i in range(199)]
    a, b = judge.choose_human_ids(ids), judge.choose_human_ids(ids)
    assert a == b and len(a) == 30
    assert a == [i for i in ids if i in set(a)]


# ----------------------------------------------------------------------------
# Verdict parsing and resume
# ----------------------------------------------------------------------------

GOOD = {"A": {"faithfulness": 5, "completeness": 4, "format": 5, "concision": 4},
        "B": {"faithfulness": 2, "completeness": 5, "format": 3, "concision": 3},
        "preference": "a", "reason": "B invented a medication."}


def test_parse_verdict_accepts_fenced_json_and_normalises_preference():
    v = judge.parse_verdict("```json\n" + json.dumps(GOOD) + "\n```")
    assert v["preference"] == "A" and v["B"]["faithfulness"] == 2


def test_parse_verdict_rejects_bad_scores_and_labels():
    bad = dict(GOOD, preference="C")
    with pytest.raises(ValueError):
        judge.parse_verdict(json.dumps(bad))
    bad = json.loads(json.dumps(GOOD)); bad["A"]["format"] = 7
    with pytest.raises(ValueError):
        judge.parse_verdict(json.dumps(bad))


def test_done_keys_reads_id_and_swap(tmp_path):
    p = tmp_path / "v.jsonl"
    p.write_text('{"id": "test1:0", "swapped": false}\n{"id": "test1:0", "swapped": true}\n')
    assert judge.done_keys(p) == {("test1:0", False), ("test1:0", True)}
    assert judge.done_keys(tmp_path / "none.jsonl") == set()
