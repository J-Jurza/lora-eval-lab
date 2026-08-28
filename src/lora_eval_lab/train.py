"""
QLoRA fine-tune of the base model on the training split, adapter saved, validation loss logged.

Runs on the Colab T4 through Unsloth. The pure parts (config, dataset shaping, log export)
are testable on CPU; the model parts import Unsloth lazily.

Owns: the hyperparameters, the train/validation dataset shape, the adapter and log outputs.
Breaks if: Unsloth's chat-template helpers change their marker strings for Qwen (the
response-only loss silently trains on everything; the logged token counts catch it).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from lora_eval_lab import data

# ----------------------------------------------------------------------------
# Hyperparameters (see DECISIONS.md "Training hyperparameters")
# ----------------------------------------------------------------------------

CONFIG = {
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "load_in_4bit": True,
    "max_seq_length": 2048,
    "lora_rank": 16,
    "lora_alpha": 16,
    "lora_dropout": 0.0,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "learning_rate": 2e-4,
    "warmup_fraction": 0.05,
    "lr_scheduler": "linear",
    "epochs": 2,
    "per_device_batch": 2,
    "grad_accumulation": 4,
    "eval_every_steps": 25,
    "fp16": True,
    "seed": 3407,
    "loss_on": "assistant tokens only",
}

# Qwen2.5 ChatML markers used to mask everything but the assistant turn
QWEN_USER_MARK = "<|im_start|>user\n"
QWEN_ASSISTANT_MARK = "<|im_start|>assistant\n"

RESULTS_DIR = data.ROOT / "results"


# ----------------------------------------------------------------------------
# Datasets
# ----------------------------------------------------------------------------

def to_conversations(rows: list[dict]) -> list[dict]:
    """
    Shape rows as TRL conversational records.

    Args:
        rows (list[dict]): Rows from data.load_split.

    Returns:
        list[dict]: One {"messages": [...]} per row, with the reference note as the answer.
    """
    return [{"messages": data.format_example(r, with_answer=True)} for r in rows]


def log_rows(log_history: list[dict]) -> list[dict]:
    """
    Keep the loss entries from a trainer's log history.

    Args:
        log_history (list[dict]): `trainer.state.log_history`.

    Returns:
        list[dict]: Entries with step and either `loss` or `eval_loss`, other keys dropped.
    """
    keep = ("step", "epoch", "loss", "eval_loss", "learning_rate")
    return [
        {k: e[k] for k in keep if k in e}
        for e in log_history
        if "loss" in e or "eval_loss" in e
    ]


# ----------------------------------------------------------------------------
# Training
# ----------------------------------------------------------------------------

def train(out_dir: Path, model_name: str | None = None) -> dict:
    """
    Fine-tune and save the adapter.

    Args:
        out_dir (Path): Where the adapter is written.
        model_name (str or None): Override CONFIG["model"].

    Returns:
        dict: The config actually used, plus timing and step counts.
    """
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only

    cfg = dict(CONFIG)
    if model_name:
        cfg["model"] = model_name

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg["model"],
        max_seq_length=cfg["max_seq_length"],
        load_in_4bit=cfg["load_in_4bit"],
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora_rank"],
        lora_alpha=cfg["lora_alpha"],
        lora_dropout=cfg["lora_dropout"],
        target_modules=cfg["target_modules"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=cfg["seed"],
    )

    train_rows, valid_rows = data.training_rows()
    train_ds = Dataset.from_list(to_conversations(train_rows))
    valid_ds = Dataset.from_list(to_conversations(valid_rows))

    effective_batch = cfg["per_device_batch"] * cfg["grad_accumulation"]
    total_steps = math.ceil(len(train_rows) / effective_batch) * cfg["epochs"]
    warmup_steps = math.ceil(cfg["warmup_fraction"] * total_steps)

    args = SFTConfig(
        output_dir=str(out_dir / "checkpoints"),
        per_device_train_batch_size=cfg["per_device_batch"],
        per_device_eval_batch_size=cfg["per_device_batch"],
        gradient_accumulation_steps=cfg["grad_accumulation"],
        num_train_epochs=cfg["epochs"],
        learning_rate=cfg["learning_rate"],
        warmup_steps=warmup_steps,
        lr_scheduler_type=cfg["lr_scheduler"],
        fp16=cfg["fp16"],
        bf16=False,
        logging_steps=cfg["eval_every_steps"],
        eval_strategy="steps",
        eval_steps=cfg["eval_every_steps"],
        save_strategy="steps",
        save_steps=cfg["eval_every_steps"],
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        max_length=cfg["max_seq_length"],
        seed=cfg["seed"],
        report_to="none",
    )
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        args=args,
    )
    trainer = train_on_responses_only(
        trainer,
        instruction_part=QWEN_USER_MARK,
        response_part=QWEN_ASSISTANT_MARK,
    )

    started = time.time()
    result = trainer.train()
    elapsed = time.time() - started

    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "train_log.jsonl", "w", encoding="utf-8") as fh:
        for e in log_rows(trainer.state.log_history):
            fh.write(json.dumps(e) + "\n")

    record = {
        **cfg,
        "train_rows": len(train_rows),
        "valid_rows": len(valid_rows),
        "warmup_steps": warmup_steps,
        "steps": trainer.state.global_step,
        "best_checkpoint": trainer.state.best_model_checkpoint,
        "best_eval_loss": trainer.state.best_metric,
        "final_train_loss": result.training_loss,
        "seconds": round(elapsed),
    }
    (RESULTS_DIR / "train_config.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("adapter"))
    ap.add_argument("--model", default=None, help="override CONFIG['model']")
    args = ap.parse_args()

    record = train(args.out, args.model)
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
