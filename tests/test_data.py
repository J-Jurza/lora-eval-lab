"""Pure-logic tests: no download, no model."""
import csv
import json

from lora_eval_lab import data


# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------

def row(id_, section, dialogue, note="A note."):
    """Build a minimal row dict in the shape load_split returns."""
    return {"id": id_, "section": section, "dialogue": dialogue, "note": note}


def write_csv(path, rows):
    """Write rows in the upstream CSV layout."""
    fieldnames = ["ID", "section_header", "section_text", "dialogue"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ----------------------------------------------------------------------------
# Ids, normalisation, duplicate rule
# ----------------------------------------------------------------------------

def test_row_id_carries_split_name():
    assert data.row_id("test1", "0") == "test1:0"
    assert data.row_id("train", "0") != data.row_id("test1", "0")


def test_normalise_collapses_case_and_whitespace():
    assert data.normalise("Doctor:  Hi.\n Patient: HI ") == "doctor: hi. patient: hi"


def test_cross_split_duplicates_catches_planted_duplicate_only():
    train = [
        row("train:0", "CC", "Doctor: what brings you in?\nPatient: chest pain."),
        row("train:1", "CC", "Doctor: hello."),
    ]
    other = [
        row("test1:0", "CC", "doctor: what brings you in? patient: chest pain."),
        row("test1:1", "CC", "Doctor: goodbye."),
    ]
    assert data.cross_split_duplicates(train, other) == ["test1:0"]


# ----------------------------------------------------------------------------
# Chat formatting
# ----------------------------------------------------------------------------

def test_format_example_uses_full_section_name_and_dialogue():
    r = row("train:7", "GENHX", "Doctor: how long?\nPatient: two days.", "Symptoms for two days.")
    msgs = data.format_example(r)

    assert [m["role"] for m in msgs] == ["system", "user", "assistant"]
    assert msgs[0]["content"] == data.SYSTEM_PROMPT
    assert "History of Present Illness" in msgs[1]["content"]
    assert "Patient: two days." in msgs[1]["content"]
    assert msgs[2]["content"] == "Symptoms for two days."


def test_format_example_prompt_only_has_no_answer():
    r = row("train:7", "ALLERGY", "Doctor: allergies?\nPatient: none.", "NKDA.")
    msgs = data.format_example(r, with_answer=False)

    assert [m["role"] for m in msgs] == ["system", "user"]
    assert "NKDA" not in json.dumps(msgs)


# ----------------------------------------------------------------------------
# Held-out freeze
# ----------------------------------------------------------------------------

def test_every_section_code_has_a_name():
    assert len(data.SECTION_NAMES) == 20


def test_build_holdout_drops_train_duplicates(tmp_path):
    write_csv(
        tmp_path / data.FILES["train"],
        [{"ID": "0", "section_header": "CC", "section_text": "n", "dialogue": "Doctor: A?"}],
    )
    write_csv(
        tmp_path / data.FILES["test1"],
        [
            {"ID": "0", "section_header": "CC", "section_text": "n", "dialogue": "doctor:  a?"},
            {"ID": "1", "section_header": "CC", "section_text": "n", "dialogue": "Doctor: B?"},
        ],
    )
    rec = data.build_holdout(raw_dir=tmp_path, path=tmp_path / "h.json")

    assert rec["kept"] == ["test1:1"]
    assert rec["dropped_duplicate_of_train"] == ["test1:0"]
