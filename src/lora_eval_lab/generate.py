"""
Generate a note section for every held-out dialogue with one model configuration.

Runs once for the base model (the control) and once with the adapter (the candidate),
with the same prompt and the same greedy decoding. Each output row carries the settings
that produced it, and the run resumes from an existing file.

Owns: the prompt as sent, the decoding settings, the generations file format.
Breaks if: the chat template changes between runs (prompt_sha256 in each row catches it).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from lora_eval_lab import data

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------

DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
RESULTS_DIR = data.ROOT / "results"
DECODING = {"do_sample": False, "max_new_tokens": 320, "repetition_penalty": 1.0}

# One fixed training example for the optional one-shot control (step 8): the first
# History of Present Illness row whose dialogue is 80 to 150 words.
ONE_SHOT_SECTION = "GENHX"
ONE_SHOT_WORDS = (80, 150)


# ----------------------------------------------------------------------------
# Prompts
# ----------------------------------------------------------------------------

def pick_one_shot(train: list[dict]) -> dict:
    """
    Choose the fixed one-shot example deterministically.

    Args:
        train (list[dict]): Training rows in file order.

    Returns:
        dict: The first GENHX row with a dialogue of 80 to 150 words.
    """
    lo, hi = ONE_SHOT_WORDS
    for r in train:
        if r["section"] == ONE_SHOT_SECTION and lo <= len(r["dialogue"].split()) <= hi:
            return r
    raise ValueError("no training row satisfies the one-shot rule")


def build_messages(row: dict, one_shot: dict | None = None) -> list[dict]:
    """
    Build the prompt messages for one held-out row.

    Args:
        row (dict): The held-out row.
        one_shot (dict or None): If given, a worked example inserted as a user/assistant
            pair before the real request.

    Returns:
        list[dict]: Messages without an assistant answer for `row`.
    """
    messages = data.format_example(row, with_answer=False)
    if one_shot is None:
        return messages
    example = data.format_example(one_shot, with_answer=True)
    return [messages[0], example[1], example[2], messages[1]]


def prompt_hash(messages: list[dict]) -> str:
    """Stable fingerprint of the exact messages sent."""
    return hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------
# Output file
# ----------------------------------------------------------------------------

def done_ids(path: Path) -> set[str]:
    """Ids already present in a generations file, so a rerun can skip them."""
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as fh:
        return {json.loads(line)["id"] for line in fh if line.strip()}


def output_row(row: dict, text: str, messages: list[dict], model: str, adapter: str | None, tag: str) -> dict:
    """One line of the generations file."""
    return {
        "id": row["id"],
        "section": row["section"],
        "tag": tag,
        "output": text.strip(),
        "model": model,
        "adapter": adapter,
        "decoding": DECODING,
        "prompt_sha256": prompt_hash(messages),
    }


# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------

def load_model(model_name: str, adapter: str | None):
    """
    Load tokenizer and model: 4-bit on a CUDA GPU, full precision on CPU for smoke tests.

    Args:
        model_name (str): Hugging Face model id.
        adapter (str or None): Path to a saved LoRA adapter, attached if given.

    Returns:
        tuple: (tokenizer, model) ready for batched left-padded generation.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if torch.cuda.is_available():
        from transformers import BitsAndBytesConfig

        quant = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant, device_map="auto")
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)

    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return tokenizer, model


def generate_batch(tokenizer, model, batch_messages: list[list[dict]]) -> list[str]:
    """
    Greedy-generate one batch of prompts and return only the new text.

    Args:
        tokenizer, model: From load_model.
        batch_messages (list[list[dict]]): One messages list per prompt.

    Returns:
        list[str]: Decoded completions, special tokens removed.
    """
    import torch

    texts = [
        tokenizer.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in batch_messages
    ]
    enc = tokenizer(texts, return_tensors="pt", padding=True).to(model.device)
    with torch.no_grad():
        out = model.generate(**enc, pad_token_id=tokenizer.pad_token_id, **DECODING)
    new_tokens = out[:, enc["input_ids"].shape[1]:]
    return tokenizer.batch_decode(new_tokens, skip_special_tokens=True)


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------

def run(
    tag: str,
    model_name: str,
    adapter: str | None,
    one_shot: bool,
    batch_size: int,
    limit: int | None,
    out_path: Path | None = None,
) -> Path:
    """
    Generate for every held-out row not already in the output file.

    Args:
        tag (str): Output file suffix: base, tuned or oneshot.
        model_name (str): Hugging Face model id.
        adapter (str or None): LoRA adapter path.
        one_shot (bool): Insert the fixed worked example into the prompt.
        batch_size (int): Prompts per generate call.
        limit (int or None): Stop after this many rows (smoke tests).
        out_path (Path or None): Override the output file (smoke tests).

    Returns:
        Path: The generations file.
    """
    out_path = out_path or RESULTS_DIR / f"generations_{tag}.jsonl"
    rows = data.heldout_rows()
    if limit:
        rows = rows[:limit]
    example = pick_one_shot(data.load_split("train")) if one_shot else None

    skip = done_ids(out_path)
    todo = [r for r in rows if r["id"] not in skip]
    print(f"{tag}: {len(skip)} done, {len(todo)} to generate")
    if not todo:
        return out_path

    tokenizer, model = load_model(model_name, adapter)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as fh:
        for start in range(0, len(todo), batch_size):
            batch = todo[start:start + batch_size]
            messages = [build_messages(r, example) for r in batch]
            for r, m, text in zip(batch, messages, generate_batch(tokenizer, model, messages)):
                fh.write(json.dumps(output_row(r, text, m, model_name, adapter, tag)) + "\n")
            fh.flush()
            print(f"  {min(start + batch_size, len(todo))}/{len(todo)}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True, choices=["base", "tuned", "oneshot"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--adapter", default=None, help="LoRA adapter directory (tuned runs)")
    ap.add_argument("--one-shot", action="store_true", help="step 8 control")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None, help="smoke test: first N rows only")
    ap.add_argument("--out", type=Path, default=None, help="smoke test: write elsewhere than results/")
    args = ap.parse_args()

    if args.tag == "tuned" and not args.adapter:
        ap.error("--tag tuned needs --adapter")
    if args.tag == "oneshot" and not args.one_shot:
        ap.error("--tag oneshot needs --one-shot")
    path = run(
        args.tag,
        args.model,
        args.adapter,
        args.one_shot,
        args.batch_size,
        args.limit,
        args.out,
    )
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
