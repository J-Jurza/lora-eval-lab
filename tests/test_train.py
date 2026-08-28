"""Config, dataset shaping and log export only: no GPU, no Unsloth."""
from lora_eval_lab import data, train


# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

def test_config_matches_decisions_record():
    c = train.CONFIG
    assert c["lora_rank"] == 16 and c["lora_alpha"] == 16 and c["lora_dropout"] == 0.0
    assert c["epochs"] == 2 and c["per_device_batch"] * c["grad_accumulation"] == 8
    assert c["max_seq_length"] == 2048 and c["fp16"] is True
    assert len(c["target_modules"]) == 7


def test_qwen_markers_are_chatml():
    assert train.QWEN_USER_MARK.startswith("<|im_start|>user")
    assert train.QWEN_ASSISTANT_MARK.startswith("<|im_start|>assistant")


# ----------------------------------------------------------------------------
# Datasets
# ----------------------------------------------------------------------------

def test_to_conversations_keeps_the_answer_turn():
    rows = [{"id": "train:0", "section": "CC", "dialogue": "Doctor: hi.", "note": "Headache."}]
    recs = train.to_conversations(rows)
    assert len(recs) == 1
    assert recs[0]["messages"] == data.format_example(rows[0], with_answer=True)
    assert recs[0]["messages"][-1] == {"role": "assistant", "content": "Headache."}


# ----------------------------------------------------------------------------
# Log export
# ----------------------------------------------------------------------------

def test_log_rows_keeps_loss_entries_only():
    history = [
        {"step": 25, "epoch": 0.17, "loss": 1.9, "learning_rate": 1e-4, "grad_norm": 0.5},
        {"step": 25, "epoch": 0.17, "eval_loss": 1.7, "eval_runtime": 3.2},
        {"step": 300, "train_runtime": 900.0},
    ]
    rows = train.log_rows(history)
    assert rows == [
        {"step": 25, "epoch": 0.17, "loss": 1.9, "learning_rate": 1e-4},
        {"step": 25, "epoch": 0.17, "eval_loss": 1.7},
    ]
