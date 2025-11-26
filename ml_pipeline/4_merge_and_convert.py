"""
Step 4: Merge LoRA weights and convert to GGML format.
This prepares the model for CPU inference in production.

Usage:
    python 4_merge_and_convert.py [--skip-merge] [--skip-quantize]
"""
import os
import argparse
import subprocess
from pathlib import Path
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


def merge_lora_weights(
    base_model_name: str,
    lora_weights_path: Path,
    output_path: Path
):
    """
    Merge LoRA adapter weights with base model.

    Args:
        base_model_name: Name of base model
        lora_weights_path: Path to LoRA weights
        output_path: Where to save merged model
    """
    print("\n" + "=" * 60)
    print("Step 1: Merging LoRA Weights with Base Model")
    print("=" * 60)

    if not lora_weights_path.exists():
        raise FileNotFoundError(
            f"LoRA weights not found at {lora_weights_path}\n"
            f"Please run: python 3_finetune_model.py"
        )

    print(f"Loading base model: {base_model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    print(f"Loading LoRA weights from: {lora_weights_path}")
    model = PeftModel.from_pretrained(base_model, str(lora_weights_path))

    print("Merging weights...")
    model = model.merge_and_unload()

    print(f"Saving merged model to: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)

    # Save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.save_pretrained(output_path)

    print("✓ Model merged and saved")

    return output_path


def convert_to_gguf(model_path: Path, output_path: Path, quantization: str = "q8_0"):
    """
    Convert model to GGUF format and quantize.

    Args:
        model_path: Path to merged model
        output_path: Where to save GGUF model
        quantization: Quantization type (q4_0, q5_0, q5_1, q8_0)
    """
    print("\n" + "=" * 60)
    print("Step 2: Converting to GGUF Format")
    print("=" * 60)

    # Check if llama.cpp is available
    llama_cpp_dir = Path("llama.cpp")

    if not llama_cpp_dir.exists():
        print("\nllama.cpp not found. Cloning repository...")
        subprocess.run([
            "git", "clone",
            "https://github.com/ggerganov/llama.cpp.git"
        ], check=True)

    # Convert to GGUF (f16)
    print("\nConverting to GGUF format (fp16)...")
    f16_output = output_path / "model-f16.gguf"
    output_path.mkdir(parents=True, exist_ok=True)

    convert_script = llama_cpp_dir / "convert_hf_to_gguf.py"

    subprocess.run([
        "python", str(convert_script),
        str(model_path),
        "--outtype", "f16",
        "--outfile", str(f16_output)
    ], check=True)

    print(f"✓ F16 model saved to: {f16_output}")

    # Build quantization tools if needed
    quantize_tool = llama_cpp_dir / "build" / "bin" / "llama-quantize"

    if not quantize_tool.exists():
        print("\nBuilding llama.cpp quantization tools...")
        build_dir = llama_cpp_dir / "build"
        build_dir.mkdir(exist_ok=True)

        subprocess.run(["cmake", "-B", str(build_dir)], cwd=llama_cpp_dir, check=True)
        subprocess.run(["cmake", "--build", str(build_dir), "--config", "Release"], check=True)

    # Quantize model
    print(f"\nQuantizing to {quantization}...")
    quantized_output = output_path / f"model-{quantization}.gguf"

    subprocess.run([
        str(quantize_tool),
        str(f16_output),
        str(quantized_output),
        quantization
    ], check=True)

    print(f"✓ Quantized model saved to: {quantized_output}")

    # Show file sizes
    f16_size = f16_output.stat().st_size / (1024**3)
    quant_size = quantized_output.stat().st_size / (1024**3)

    print("\n" + "=" * 60)
    print("Model Sizes:")
    print("=" * 60)
    print(f"F16 model: {f16_size:.2f} GB")
    print(f"{quantization.upper()} model: {quant_size:.2f} GB")
    print(f"Size reduction: {100 * (1 - quant_size/f16_size):.1f}%")

    return quantized_output


def upload_to_huggingface(model_path: Path, repo_id: str):
    """
    Upload model to HuggingFace Hub.

    Args:
        model_path: Path to model
        repo_id: HuggingFace repository ID (username/model-name)
    """
    print("\n" + "=" * 60)
    print("Step 3: Uploading to HuggingFace Hub")
    print("=" * 60)

    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("huggingface_hub not installed. Install with:")
        print("pip install huggingface_hub")
        return

    print(f"Repository: {repo_id}")
    print("\nYou need to be logged in to HuggingFace.")
    print("Run: huggingface-cli login")

    api = HfApi()

    print(f"\nUploading {model_path.name}...")
    api.upload_file(
        path_or_fileobj=str(model_path),
        path_in_repo="model.bin",
        repo_id=repo_id,
        repo_type="model"
    )

    print(f"✓ Model uploaded to: https://huggingface.co/{repo_id}")


def main():
    parser = argparse.ArgumentParser(description='Merge LoRA and convert to GGML')
    parser.add_argument('--skip-merge', action='store_true', help='Skip merging step')
    parser.add_argument('--skip-quantize', action='store_true', help='Skip quantization step')
    parser.add_argument('--upload', type=str, help='Upload to HuggingFace (provide repo_id)')
    parser.add_argument('--quant', type=str, default='q8_0',
                        choices=['q4_0', 'q5_0', 'q5_1', 'q8_0'],
                        help='Quantization type')

    args = parser.parse_args()

    print("=" * 60)
    print("Jenkins Chatbot - Model Conversion")
    print("=" * 60)

    # Paths
    models_dir = Path(config['paths']['models'])
    model_name = config['training']['output_model_name']
    lora_path = models_dir / model_name
    merged_path = models_dir / f"{model_name}-merged"
    gguf_path = models_dir / "gguf"

    # Step 1: Merge LoRA weights
    if not args.skip_merge:
        base_model = config['training']['base_model']
        merged_path = merge_lora_weights(base_model, lora_path, merged_path)
    else:
        print("\n⏭ Skipping merge step")
        if not merged_path.exists():
            print(f"❌ Merged model not found at {merged_path}")
            return

    # Step 2: Convert to GGUF and quantize
    if not args.skip_quantize:
        quantized_model = convert_to_gguf(merged_path, gguf_path, args.quant)
    else:
        print("\n⏭ Skipping quantization step")
        quantized_model = None

    # Step 3: Upload to HuggingFace (optional)
    if args.upload and quantized_model:
        upload_to_huggingface(quantized_model, args.upload)

    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"\nMerged model: {merged_path}")
    if quantized_model:
        print(f"Quantized model: {quantized_model}")
        print("\nTo use in production, update backend config:")
        print(f"  MODEL_NAME=path/to/gguf")
        print(f"  MODEL_FILE=model-{args.quant}.gguf")


if __name__ == "__main__":
    main()
