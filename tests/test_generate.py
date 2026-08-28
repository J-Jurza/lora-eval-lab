"""Prompt construction and file handling only: no model."""
import json

from lora_eval_lab import data, generate


# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------

def row(id_, section, dialogue, note="A note."):
    return {"id": id_, "section": section, "dialogue": dialogue, "note": note}


HELD = row("test1:3", "ALLERGY", "Doctor: any allergies?\nPatient: penicillin.", "Penicillin.")
EXAMPLE = row("train:9", "GENHX", " ".join(["word"] * 100), "History example.")


# ----------------------------------------------------------------------------
# Prompts
# ----------------------------------------------------------------------------

def test_zero_shot_prompt_is_the_data_prompt_without_the_answer():
    msgs = generate.build_messages(HELD)
    assert msgs == data.format_example(HELD, with_answer=False)
    assert "Penicillin." not in json.dumps(msgs)


def test_one_shot_prompt_inserts_example_before_the_request():
    msgs = generate.build_messages(HELD, one_shot=EXAMPLE)
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]
    assert msgs[2]["content"] == "History example."
    assert "any allergies?" in msgs[3]["content"]
    assert "Penicillin." not in json.dumps(msgs)


def test_pick_one_shot_takes_first_genhx_in_the_word_window():
    train = [
        row("train:0", "GENHX", " ".join(["w"] * 20)),
        row("train:1", "CC", " ".join(["w"] * 100)),
        row("train:2", "GENHX", " ".join(["w"] * 100)),
        row("train:3", "GENHX", " ".join(["w"] * 120)),
    ]
    assert generate.pick_one_shot(train)["id"] == "train:2"


def test_prompt_hash_is_stable_and_sensitive():
    a = generate.prompt_hash(generate.build_messages(HELD))
    b = generate.prompt_hash(generate.build_messages(HELD))
    c = generate.prompt_hash(generate.build_messages(row("test1:4", "ALLERGY", "Doctor: hi.")))
    assert a == b and a != c and len(a) == 16


# ----------------------------------------------------------------------------
# Output file
# ----------------------------------------------------------------------------

def test_output_row_strips_and_records_settings():
    msgs = generate.build_messages(HELD)
    out = generate.output_row(HELD, "  Penicillin allergy.\n", msgs, "m", None, "base")
    assert out["output"] == "Penicillin allergy."
    assert out["decoding"]["do_sample"] is False
    assert out["adapter"] is None
    assert out["prompt_sha256"] == generate.prompt_hash(msgs)


def test_done_ids_reads_existing_file_and_tolerates_absence(tmp_path):
    assert generate.done_ids(tmp_path / "none.jsonl") == set()
    path = tmp_path / "g.jsonl"
    path.write_text('{"id": "test1:0"}\n{"id": "test1:5"}\n\n')
    assert generate.done_ids(path) == {"test1:0", "test1:5"}
