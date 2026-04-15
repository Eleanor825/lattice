from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import GPT2Config, GPT2LMHeadModel, Trainer, TrainingArguments

from lattice.sources.common import timestamp_now
from lattice.training.tokenization import CharTokenizer
from lattice.utils import ensure_dir, write_json


class HFDataset(Dataset):
    def __init__(self, texts: list[str], tokenizer: CharTokenizer, max_length: int) -> None:
        self.examples = []
        for text in texts:
            ids = tokenizer.encode(text, max_length=max_length)
            if len(ids) < 2:
                continue
            tensor = torch.tensor(ids, dtype=torch.long)
            self.examples.append(
                {
                    "input_ids": tensor,
                    "attention_mask": torch.ones_like(tensor),
                    "labels": tensor.clone(),
                }
            )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int):
        return self.examples[index]


class HFDataCollator:
    def __init__(self, pad_id: int) -> None:
        self.pad_id = pad_id

    def __call__(self, features: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        keys = ("input_ids", "attention_mask", "labels")
        max_len = max(feature["input_ids"].size(0) for feature in features)
        batch: dict[str, torch.Tensor] = {}
        for key in keys:
            padded = []
            for feature in features:
                tensor = feature[key]
                pad_value = 0 if key == "attention_mask" else self.pad_id
                if tensor.size(0) < max_len:
                    tensor = torch.nn.functional.pad(tensor, (0, max_len - tensor.size(0)), value=pad_value)
                padded.append(tensor)
            batch[key] = torch.stack(padded)
        return batch


@dataclass(slots=True)
class HFTrainingResult:
    workflow: str
    run_name: str
    output_dir: str
    sample_count: int
    final_loss: float
    backend: str


def _build_or_load_model(
    *,
    model_name: str,
    checkpoint_dir: str,
    tokenizer: CharTokenizer,
    hidden_size: int,
) -> GPT2LMHeadModel:
    checkpoint_path = Path(checkpoint_dir) / "hf_model" if checkpoint_dir else None
    if checkpoint_path and checkpoint_path.exists():
        return GPT2LMHeadModel.from_pretrained(checkpoint_path)

    if model_name == "hf-gpt2-tiny-local":
        config = GPT2Config(
            vocab_size=tokenizer.vocab_size,
            n_positions=256,
            n_ctx=256,
            n_embd=hidden_size,
            n_layer=2,
            n_head=2,
            bos_token_id=tokenizer.bos_id,
            eos_token_id=tokenizer.eos_id,
        )
        return GPT2LMHeadModel(config)

    return GPT2LMHeadModel.from_pretrained(model_name)


def run_hf_causal_lm_workflow(
    *,
    workflow: str,
    texts: list[str],
    output_dir: str,
    run_name: str,
    model_name: str,
    checkpoint_dir: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    max_length: int,
    hidden_size: int,
) -> HFTrainingResult:
    ensure_dir(output_dir)
    ensure_dir(Path(output_dir) / "hf_model")
    ensure_dir(Path(output_dir) / "reports")

    tokenizer = CharTokenizer.build(texts)
    model = _build_or_load_model(
        model_name=model_name,
        checkpoint_dir=checkpoint_dir,
        tokenizer=tokenizer,
        hidden_size=hidden_size,
    )
    dataset = HFDataset(texts, tokenizer=tokenizer, max_length=max_length)

    training_args = TrainingArguments(
        output_dir=str(Path(output_dir) / "hf_tmp"),
        overwrite_output_dir=True,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        save_strategy="no",
        logging_strategy="no",
        report_to=[],
        disable_tqdm=True,
        fp16=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=HFDataCollator(tokenizer.pad_id),
    )
    train_result = trainer.train()
    model.save_pretrained(Path(output_dir) / "hf_model")
    tokenizer.save(Path(output_dir) / "hf_model" / "char_tokenizer.json")

    manifest = {
        "generated_at": timestamp_now(),
        "workflow": workflow,
        "run_name": run_name,
        "backend": "hf_causal_lm",
        "model_name": model_name,
        "checkpoint_dir": str(Path(checkpoint_dir).resolve()) if checkpoint_dir else "",
        "output_dir": str(Path(output_dir).resolve()),
        "sample_count": len(dataset),
        "final_loss": float(train_result.training_loss),
    }
    write_json(Path(output_dir) / "reports" / "manifest.json", manifest)
    return HFTrainingResult(
        workflow=workflow,
        run_name=run_name,
        output_dir=str(Path(output_dir).resolve()),
        sample_count=len(dataset),
        final_loss=float(train_result.training_loss),
        backend="hf_causal_lm",
    )
