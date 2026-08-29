"""
Blinded side-by-side judging: build the pairs, hide which side is the tuned model, write
the human pack, and call the LLM judge twice per pair with A and B swapped.

Owns: the blinding key, the pair layout, the judge prompt, the verdict file format.
Breaks if: the two generations files were made with different prompts (prompt_sha256
mismatch raises), or the judge stops returning parseable JSON (raw text is kept per row).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from pathlib import Path

from lora_eval_lab import data

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------

RESULTS_DIR = data.ROOT / "results"
RUBRIC_PATH = data.ROOT / "eval" / "rubric.md"
PROMPT_PATH = data.ROOT / "eval" / "judge_prompt.md"
KEY_PATH = RESULTS_DIR / "blinding_key.json"
HUMAN_PACK_PATH = RESULTS_DIR / "human_pack.md"
VERDICTS_PATH = RESULTS_DIR / "judge_verdicts.jsonl"

BLIND_SEED = 20260828
HUMAN_PAIRS = 30
DIMENSIONS = ("faithfulness", "completeness", "format", "concision")
DEFAULT_JUDGE = "gemini-3.6-flash"
SECONDS_BETWEEN_CALLS = 6.5


# ----------------------------------------------------------------------------
# Pairs and blinding
# ----------------------------------------------------------------------------

def read_jsonl(path: Path) -> list[dict]:
    """Read a JSON-lines file, skipping blank lines."""
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_pairs(base: list[dict], tuned: list[dict], rows: list[dict]) -> list[dict]:
    """
    Join base and tuned generations with the held-out rows, checking the prompts match.

    Args:
        base, tuned (list[dict]): Rows from the two generations files.
        rows (list[dict]): Held-out rows from data.heldout_rows.

    Returns:
        list[dict]: One pair per id with dialogue, reference, section, base and tuned text.
    """
    base_by = {r["id"]: r for r in base}
    tuned_by = {r["id"]: r for r in tuned}
    pairs = []
    for row in rows:
        b, t = base_by.get(row["id"]), tuned_by.get(row["id"])
        if b is None or t is None:
            continue
        if b["prompt_sha256"] != t["prompt_sha256"]:
            raise ValueError(f"{row['id']}: base and tuned were generated from different prompts")
        pairs.append(
            {
                "id": row["id"],
                "section": row["section"],
                "dialogue": row["dialogue"],
                "reference": row["note"],
                "base": b["output"],
                "tuned": t["output"],
            }
        )
    return pairs


def make_key(ids: list[str], seed: int = BLIND_SEED) -> dict[str, str]:
    """
    Decide, per id, whether the tuned output is shown as A or B.

    Args:
        ids (list[str]): Pair ids in a fixed order.
        seed (int): RNG seed, so the key is reproducible.

    Returns:
        dict[str, str]: id to "A" or "B" (the side that is the tuned model).
    """
    rng = random.Random(seed)
    return {i: rng.choice("AB") for i in ids}


def shown(pair: dict, tuned_side: str, swapped: bool = False) -> tuple[str, str]:
    """
    The texts to show as A and B for one pair.

    Args:
        pair (dict): From build_pairs.
        tuned_side (str): "A" or "B" from the key.
        swapped (bool): Present the opposite ordering (the position-bias control).

    Returns:
        tuple[str, str]: (text for A, text for B).
    """
    side = tuned_side
    if swapped:
        side = "B" if side == "A" else "A"
    return (pair["tuned"], pair["base"]) if side == "A" else (pair["base"], pair["tuned"])


def to_model(preference: str, tuned_side: str, swapped: bool = False) -> str:
    """Map a shown-label preference (A, B, tie) back to tuned, base or tie."""
    if preference == "tie":
        return "tie"
    side = tuned_side
    if swapped:
        side = "B" if side == "A" else "A"
    return "tuned" if preference == side else "base"


# ----------------------------------------------------------------------------
# Human pack
# ----------------------------------------------------------------------------

def choose_human_ids(ids: list[str], n: int = HUMAN_PAIRS, seed: int = BLIND_SEED) -> list[str]:
    """A seeded random subset of ids for the human pass, in id order."""
    rng = random.Random(seed + 1)
    chosen = set(rng.sample(ids, min(n, len(ids))))
    return [i for i in ids if i in chosen]


def human_pack(pairs: list[dict], key: dict[str, str], ids: list[str]) -> str:
    """
    Markdown for the human blind pass: dialogue, reference, A, B, and a scoring line.

    Args:
        pairs (list[dict]): From build_pairs.
        key (dict[str, str]): The blinding key; used only to order A and B.
        ids (list[str]): Which pairs to include.

    Returns:
        str: The pack. Contains no indication of which side is tuned.
    """
    by_id = {p["id"]: p for p in pairs}
    out = [
        "# Human blind pass\n",
        "Score each side 1 to 5 per dimension, then a preference, before running the judge.",
        "Fill the SCORES line exactly: `SCORES: A f c fo co | B f c fo co | PREF: A|B|tie | REASON: ...`\n",
        RUBRIC_PATH.read_text(),
        "\n---\n",
    ]
    for i in ids:
        p = by_id[i]
        a, b = shown(p, key[i])
        out += [
            f"\n## Pair {i}\n",
            f"**Section:** {data.SECTION_NAMES[p['section']]}\n",
            f"**Conversation:**\n\n```\n{p['dialogue']}\n```\n",
            f"**Reference (calibration only):**\n\n```\n{p['reference']}\n```\n",
            f"**A:**\n\n```\n{a}\n```\n",
            f"**B:**\n\n```\n{b}\n```\n",
            "SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: \n",
        ]
    return "\n".join(out)


SCORES_RE = re.compile(
    r"SCORES:\s*A\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*\|\s*B\s+(\d)\s+(\d)\s+(\d)\s+(\d)"
    r"\s*\|\s*PREF:\s*(A|B|tie)\s*\|\s*REASON:\s*(.*)",
    re.IGNORECASE,
)


def parse_human_pack(text: str) -> list[dict]:
    """
    Read filled SCORES lines back out of the human pack.

    Args:
        text (str): The pack after the human has filled it in.

    Returns:
        list[dict]: One verdict per completed pair, in shown-label terms.
    """
    verdicts = []
    current = None
    for line in text.splitlines():
        if line.startswith("## Pair "):
            current = line[len("## Pair "):].strip()
            continue
        m = SCORES_RE.match(line.strip())
        if m and current:
            g = m.groups()
            verdicts.append(
                {
                    "id": current,
                    "A": dict(zip(DIMENSIONS, map(int, g[0:4]))),
                    "B": dict(zip(DIMENSIONS, map(int, g[4:8]))),
                    "preference": g[8].lower() if g[8].lower() == "tie" else g[8].upper(),
                    "reason": g[9].strip(),
                }
            )
    return verdicts


# ----------------------------------------------------------------------------
# LLM judge
# ----------------------------------------------------------------------------

def judge_prompt(pair: dict, a: str, b: str) -> str:
    """Fill the prompt template with the rubric and one pair."""
    template = PROMPT_PATH.read_text()
    return template.format(
        rubric=RUBRIC_PATH.read_text().strip(),
        section=data.SECTION_NAMES[pair["section"]],
        dialogue=pair["dialogue"],
        reference=pair["reference"],
        a=a,
        b=b,
    )


def parse_verdict(text: str) -> dict:
    """
    Parse the judge's JSON reply, tolerating a code fence.

    Args:
        text (str): Raw model reply.

    Returns:
        dict: Scores for A and B, preference, reason. Raises ValueError if malformed.
    """
    body = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", body, re.DOTALL)
    if fence:
        body = fence.group(1)
    obj = json.loads(body)
    pref = str(obj["preference"]).strip()
    pref = pref.lower() if pref.lower() == "tie" else pref.upper()
    if pref not in ("A", "B", "tie"):
        raise ValueError(f"bad preference {pref!r}")
    for side in ("A", "B"):
        for d in DIMENSIONS:
            v = int(obj[side][d])
            if not 1 <= v <= 5:
                raise ValueError(f"score out of range: {side} {d} {v}")
            obj[side][d] = v
    return {"A": obj["A"], "B": obj["B"], "preference": pref, "reason": str(obj.get("reason", ""))}


def done_keys(path: Path) -> set[tuple[str, bool]]:
    """(id, swapped) pairs already judged, for resuming."""
    if not path.exists():
        return set()
    return {(r["id"], r["swapped"]) for r in read_jsonl(path)}


def call_gemini(model: str, prompt: str, client, retries: int = 5) -> str:
    """
    One judge call with backoff on rate limits.

    Args:
        model (str): Gemini model name.
        prompt (str): Filled judge prompt.
        client: An open google.genai Client, shared across the run.
        retries (int): Attempts before giving up on a 429 or transient error.

    Returns:
        str: Raw reply text.
    """
    for attempt in range(retries):
        try:
            reply = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"temperature": 0, "response_mime_type": "application/json"},
            )
            return reply.text
        except Exception as exc:  # noqa: BLE001 (the client raises many types for 429)
            wait = 20 * (attempt + 1)
            print(f"  retry {attempt + 1}/{retries} after {wait}s: {exc}")
            time.sleep(wait)
    raise RuntimeError("judge call failed after retries")


def load_api_key() -> str:
    """GEMINI_API_KEY from the environment, else from .env in the repo root."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        env = data.ROOT / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        raise SystemExit("GEMINI_API_KEY not set (see .env.example)")
    return key


def run_judge(pairs: list[dict], key: dict[str, str], model: str, limit: int | None, out: Path) -> None:
    """
    Judge every pair twice (key ordering, then swapped), resuming from the verdicts file.

    Args:
        pairs (list[dict]): From build_pairs.
        key (dict[str, str]): The blinding key.
        model (str): Judge model name.
        limit (int or None): Judge only the first N pairs (the quota fallback).
        out (Path): Verdicts file, appended to.
    """
    from google import genai

    done = done_keys(out)
    todo = [(p, s) for p in pairs[:limit] for s in (False, True) if (p["id"], s) not in done]
    print(f"judge: {len(done)} verdicts done, {len(todo)} to do")

    out.parent.mkdir(exist_ok=True)
    with genai.Client(api_key=load_api_key()) as client, open(out, "a", encoding="utf-8") as fh:
        for n, (p, swapped) in enumerate(todo, 1):
            a, b = shown(p, key[p["id"]], swapped)
            raw = call_gemini(model, judge_prompt(p, a, b), client)
            row = {"id": p["id"], "swapped": swapped, "judge": model, "raw": raw}
            try:
                v = parse_verdict(raw)
                row.update(v)
                row["preferred_model"] = to_model(v["preference"], key[p["id"]], swapped)
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                row["parse_error"] = str(exc)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(f"  {n}/{len(todo)} {p['id']} swapped={swapped} -> {row.get('preferred_model', 'unparsed')}")
            time.sleep(SECONDS_BETWEEN_CALLS)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def load_everything() -> tuple[list[dict], dict[str, str]]:
    """Pairs and the blinding key, creating the key on first use."""
    pairs = build_pairs(
        read_jsonl(RESULTS_DIR / "generations_base.jsonl"),
        read_jsonl(RESULTS_DIR / "generations_tuned.jsonl"),
        data.heldout_rows(),
    )
    if KEY_PATH.exists():
        key = json.loads(KEY_PATH.read_text())
    else:
        key = make_key([p["id"] for p in pairs])
        KEY_PATH.write_text(json.dumps(key, indent=1) + "\n")
    return pairs, key


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--human", action="store_true", help="write the human pack")
    ap.add_argument("--judge", action="store_true", help="run the LLM judge")
    ap.add_argument("--model", default=DEFAULT_JUDGE)
    ap.add_argument("--limit", type=int, default=None, help="judge only the first N pairs")
    ap.add_argument("--force", action="store_true", help="overwrite an existing human pack")
    args = ap.parse_args()

    pairs, key = load_everything()
    print(f"{len(pairs)} pairs, key at {KEY_PATH}")
    if args.human:
        if HUMAN_PACK_PATH.exists() and not args.force:
            raise SystemExit(
                f"{HUMAN_PACK_PATH} exists and may hold filled-in scores; pass --force to overwrite"
            )
        ids = choose_human_ids([p["id"] for p in pairs])
        HUMAN_PACK_PATH.write_text(human_pack(pairs, key, ids))
        print(f"human pack: {len(ids)} pairs at {HUMAN_PACK_PATH}")
    if args.judge:
        run_judge(pairs, key, args.model, args.limit, VERDICTS_PATH)


if __name__ == "__main__":
    main()
