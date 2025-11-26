"""
Step 3: Fine-tune Llama-2 on Jenkins Q&A data.
Complete training script with QLoRA for efficient fine-tuning.

This script can run on:
- Google Colab (free T4 GPU)
- Local machine with 16GB+ VRAM GPU
- Cloud GPU instances

Usage:
    python 3_finetune_model.py [--local] [--epochs 5] [--batch_size 4]
"""
import os
import argparse
from pathlib import Path
import yaml
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


def setup_paths(local_mode=True):
    """Setup paths for local or Colab environment."""
    if local_mode:
        return {
            'data': Path(config['paths']['training_data']) / 'training_data.csv',
            'output': Path(config['paths']['models']) / config['training']['output_model_name'],
            'logs': Path(config['paths']['logs'])
        }
    else:
        # Colab paths with Google Drive
        return {
            'data': Path('/content/Enhancing-LLM-with-Jenkins-Knowledge/datasets/training/training_data.csv'),
            'output': Path(f'/content/drive/MyDrive/Models/{config["training"]["output_model_name"]}'),
            'logs': Path('./logs')
        }


def load_training_data(data_path: Path):
    """Load and prepare training dataset."""
    print(f"Loading training data from: {data_path}")

    if not data_path.exists():
        raise FileNotFoundError(
            f"Training data not found at {data_path}\n"
            f"Please run: python 2_preprocess_data.py"
        )

    dataset = load_dataset('csv', data_files=str(data_path), split='train')
    print(f"Loaded {len(dataset)} training examples")

    return dataset


def setup_model_and_tokenizer(model_name: str):
    """
    Setup model with 4-bit quantization and tokenizer.

    Args:
        model_name: HuggingFace model name

    Returns:
        model, tokenizer
    """
    print(f"\nLoading base model: {model_name}")
    print("This may take several minutes...")

    # Quantization config for 4-bit training
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config['training']['use_4bit'],
        bnb_4bit_quant_type=config['training']['bnb_4bit_quant_type'],
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print("✓ Model and tokenizer loaded")

    return model, tokenizer


def setup_lora(model):
    """
    Setup LoRA configuration for parameter-efficient fine-tuning.

    Args:
        model: Base model

    Returns:
        Model with LoRA adapters
    """
    lora_config_dict = config['training']['lora']

    peft_config = LoraConfig(
        r=lora_config_dict['r'],
        lora_alpha=lora_config_dict['alpha'],
        lora_dropout=lora_config_dict['dropout'],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=lora_config_dict['target_modules']
    )

    model = get_peft_model(model, peft_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nTrainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")

    return model


def create_training_arguments(output_dir: Path, num_epochs: int, batch_size: int):
    """Create training arguments."""
    output_dir.mkdir(parents=True, exist_ok=True)

    return TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=1,
        optim="paged_adamw_32bit",
        save_steps=0,  # Save only at the end
        logging_steps=25,
        learning_rate=config['training']['learning_rate'],
        weight_decay=0.001,
        fp16=False,
        bf16=False,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=config['training']['warmup_ratio'],
        group_by_length=True,
        lr_scheduler_type="cosine",
        report_to="tensorboard",
        save_total_limit=1,
    )


def train_model(
    model,
    tokenizer,
    dataset,
    training_args,
    max_seq_length=None
):
    """
    Train the model using SFTTrainer.

    Args:
        model: Model with LoRA adapters
        tokenizer: Tokenizer
        dataset: Training dataset
        training_args: Training arguments
        max_seq_length: Maximum sequence length

    Returns:
        Trained model
    """
    if max_seq_length is None:
        max_seq_length = config['training']['max_seq_length']

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
        packing=False,
    )

    print("\n" + "=" * 60)
    print("Starting Training")
    print("=" * 60)
    print(f"Number of examples: {len(dataset)}")
    print(f"Number of epochs: {training_args.num_train_epochs}")
    print(f"Batch size: {training_args.per_device_train_batch_size}")
    print(f"Total steps: ~{len(dataset) * training_args.num_train_epochs // training_args.per_device_train_batch_size}")
    print("=" * 60)

    # Train
    trainer.train()

    print("\n✓ Training complete!")

    return trainer


def save_model(trainer, model_path: Path):
    """Save the fine-tuned model."""
    print(f"\nSaving model to: {model_path}")
    model_path.mkdir(parents=True, exist_ok=True)

    trainer.model.save_pretrained(model_path)
    trainer.tokenizer.save_pretrained(model_path)

    print("✓ Model saved successfully")


def main():
    parser = argparse.ArgumentParser(description='Fine-tune Llama-2 for Jenkins Q&A')
    parser.add_argument('--local', action='store_true', help='Run in local mode (not Colab)')
    parser.add_argument('--epochs', type=int, default=5, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=4, help='Training batch size')
    parser.add_argument('--model', type=str, default=None, help='Base model name')

    args = parser.parse_args()

    # Setup environment
    print("=" * 60)
    print("Jenkins Chatbot - Model Fine-Tuning")
    print("=" * 60)

    # Check for GPU
    if not torch.cuda.is_available():
        print("\n⚠ WARNING: No GPU detected!")
        print("Training on CPU will be extremely slow.")
        print("Consider using Google Colab with GPU runtime.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    # Setup paths
    paths = setup_paths(local_mode=args.local)

    # Load data
    dataset = load_training_data(paths['data'])

    # Get base model name
    base_model = args.model or config['training']['base_model']

    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(base_model)

    # Add LoRA adapters
    model = setup_lora(model)

    # Create training arguments
    training_args = create_training_arguments(
        output_dir=paths['output'],
        num_epochs=args.epochs,
        batch_size=args.batch_size
    )

    # Train
    trainer = train_model(model, tokenizer, dataset, training_args)

    # Save
    save_model(trainer, paths['output'])

    print("\n" + "=" * 60)
    print("Fine-Tuning Complete!")
    print("=" * 60)
    print(f"Model saved to: {paths['output']}")
    print("\nNext steps:")
    print("1. Test the model")
    print("2. Merge LoRA weights: python 4_merge_and_convert.py")
    print("3. Convert to GGML for deployment")


if __name__ == "__main__":
    main()
