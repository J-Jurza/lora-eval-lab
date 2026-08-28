"""data: fetch MTS-Dialog at a pinned commit, apply the official split, check for cross-split
duplicate dialogues, freeze the held-out ids, and format rows as chat examples.

Owns: the source pin, the split, the duplicate rule, the prompt template.
Breaks if: the upstream repo rewrites history (checksums below catch it), or a row's
section header is not in SECTION_NAMES (fails loudly rather than guessing).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
HOLDOUT_PATH = ROOT / "eval" / "holdout_ids.json"

SOURCE_REPO = "abachaa/MTS-Dialog"
SOURCE_COMMIT = "3ff0801933608d6f570468c13125125fb5cabdea"
SOURCE_LICENCE = "CC BY 4.0"
FILES = {
    "train": "MTS-Dialog-TrainingSet.csv",
    "valid": "MTS-Dialog-ValidationSet.csv",
    "test1": "MTS-Dialog-TestSet-1-MEDIQA-Chat-2023.csv",
}
# sha256 of each file at SOURCE_COMMIT; a mismatch means the snapshot moved.
CHECKSUMS = {
    "train": "65a28681dd59fc159681ea026e44610f2af7bc64a0e7f892d763eb03d9f503dc",
    "valid": "227206520c4534381c0d7fba6d3f09319a9af5a6d9603a93c0341af1198e3958",
    "test1": "b4d38dd2c99b2e9860099abcf653f1e0f3e9b69f9fcc45be2a2699b37a4d2f37",
}
HELDOUT_SPLIT = "test1"

# The dataset's 20 section codes and what a clinician calls them.
SECTION_NAMES = {
    "CC": "Chief Complaint",
    "GENHX": "History of Present Illness",
    "FAM/SOCHX": "Family and Social History",
    "PASTMEDICALHX": "Past Medical History",
    "PASTSURGICAL": "Past Surgical History",
    "ROS": "Review of Systems",
    "ALLERGY": "Allergies",
    "MEDICATIONS": "Medications",
    "ASSESSMENT": "Assessment",
    "EXAM": "Physical Examination",
    "DIAGNOSIS": "Diagnosis",
    "DISPOSITION": "Disposition",
    "PLAN": "Plan",
    "EDCOURSE": "Emergency Department Course",
    "IMMUNIZATIONS": "Immunisations",
    "IMAGING": "Imaging",
    "GYNHX": "Gynaecological History",
    "OTHER_HISTORY": "Other History",
    "PROCEDURES": "Procedures",
    "LABS": "Laboratory Results",
}

SYSTEM_PROMPT = (
    "You are a clinical documentation assistant. Given a doctor-patient conversation, write "
    "the requested section of the clinical note. Use only information stated in the "
    "conversation. Write in the concise third-person style of a clinical note. Output the "
    "section text only, with no heading and no commentary."
)
USER_TEMPLATE = "Section to write: {section}\n\nConversation:\n{dialogue}"


def row_id(split: str, raw_id: str) -> str:
    """Ids restart at 0 in every split file, so a usable id carries the split name."""
    return f"{split}:{raw_id}"


def download(dest: Path = RAW_DIR, verify: bool = True) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for split, name in FILES.items():
        path = dest / name
        if not path.exists():
            url = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/Main-Dataset/{name}"
            urllib.request.urlretrieve(url, path)
        if verify:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != CHECKSUMS[split]:
                raise RuntimeError(f"{name}: checksum {digest} != pinned {CHECKSUMS[split]}")


def load_split(split: str, raw_dir: Path = RAW_DIR) -> list[dict]:
    with open(raw_dir / FILES[split], newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if r["section_header"] not in SECTION_NAMES:
            raise ValueError(f"unknown section header {r['section_header']!r} in {split}")
        out.append(
            {
                "id": row_id(split, r["ID"]),
                "section": r["section_header"],
                "dialogue": r["dialogue"].strip(),
                "note": r["section_text"].strip(),
            }
        )
    return out


def normalise(text: str) -> str:
    """Collapse whitespace and case so a re-pasted dialogue still matches."""
    return " ".join(text.lower().split())


def cross_split_duplicates(reference: list[dict], other: list[dict]) -> list[str]:
    """Ids in `other` whose dialogue also appears in `reference`."""
    seen = {normalise(r["dialogue"]) for r in reference}
    return [r["id"] for r in other if normalise(r["dialogue"]) in seen]


def format_example(row: dict, with_answer: bool = True) -> list[dict]:
    """Chat messages for one row. The held-out prompt is the same list without the answer."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_TEMPLATE.format(
                section=SECTION_NAMES[row["section"]], dialogue=row["dialogue"]
            ),
        },
    ]
    if with_answer:
        messages.append({"role": "assistant", "content": row["note"]})
    return messages


def build_holdout(raw_dir: Path = RAW_DIR, path: Path = HOLDOUT_PATH) -> dict:
    """Freeze the held-out ids: the official test split minus any dialogue seen in train."""
    train = load_split("train", raw_dir)
    heldout = load_split(HELDOUT_SPLIT, raw_dir)
    dropped = cross_split_duplicates(train, heldout)
    kept = [r["id"] for r in heldout if r["id"] not in set(dropped)]
    record = {
        "source": SOURCE_REPO,
        "commit": SOURCE_COMMIT,
        "licence": SOURCE_LICENCE,
        "split_file": FILES[HELDOUT_SPLIT],
        "rule": "official test split, minus rows whose normalised dialogue appears in train",
        "kept": kept,
        "dropped_duplicate_of_train": dropped,
    }
    path.write_text(json.dumps(record, indent=1) + "\n")
    return record


def load_holdout_ids(path: Path = HOLDOUT_PATH) -> list[str]:
    return json.loads(path.read_text())["kept"]


def training_rows(raw_dir: Path = RAW_DIR) -> tuple[list[dict], list[dict]]:
    """Train and validation rows, with validation rows that duplicate train removed."""
    train = load_split("train", raw_dir)
    valid = load_split("valid", raw_dir)
    dup = set(cross_split_duplicates(train, valid))
    return train, [r for r in valid if r["id"] not in dup]


def stats(raw_dir: Path = RAW_DIR) -> str:
    lines = []
    train, valid = training_rows(raw_dir)
    holdout = load_holdout_ids()
    lines.append(f"train {len(train)}  valid {len(valid)} (after dedup)  held-out {len(holdout)} (after dedup)")
    for name, rows in (("train", train), ("valid", valid)):
        words_d = sorted(len(r["dialogue"].split()) for r in rows)
        words_n = sorted(len(r["note"].split()) for r in rows)
        q = lambda xs, p: xs[min(len(xs) - 1, int(p * len(xs)))]
        lines.append(
            f"{name}: dialogue words p50/p90/p95/max {q(words_d,.5)}/{q(words_d,.9)}/{q(words_d,.95)}/{words_d[-1]}; "
            f"note words p50/p90/p95/max {q(words_n,.5)}/{q(words_n,.9)}/{q(words_n,.95)}/{words_n[-1]}"
        )
    counts = Counter(r["section"] for r in train)
    lines.append("train sections: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()))
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--download", action="store_true", help="fetch the pinned CSVs into data/raw")
    ap.add_argument("--build-holdout", action="store_true", help="write eval/holdout_ids.json")
    ap.add_argument("--stats", action="store_true", help="split sizes, lengths, section mix")
    args = ap.parse_args()
    if args.download:
        download()
    if args.build_holdout:
        rec = build_holdout()
        print(f"held-out kept {len(rec['kept'])}, dropped {rec['dropped_duplicate_of_train']}")
    if args.stats:
        print(stats())


if __name__ == "__main__":
    main()
