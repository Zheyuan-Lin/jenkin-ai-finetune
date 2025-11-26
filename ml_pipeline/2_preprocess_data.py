"""
Step 2: Preprocess and prepare data for training.
Clean, format, and merge all data sources into training format.
"""
import pandas as pd
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict
import re

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Paths
RAW_DATA_DIR = Path("../datasets")
OUTPUT_DIR = Path(config['paths']['training_data'])
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Preprocessing settings
MAX_SEQ_LENGTH = config['preprocessing']['max_sequence_length']
REMOVE_CODE = config['preprocessing']['remove_code_blocks']
MIN_ANSWER_LEN = config['preprocessing']['min_answer_length']
MAX_ANSWER_LEN = config['preprocessing']['max_answer_length']


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    if pd.isna(text):
        return ""
    soup = BeautifulSoup(str(text), 'html.parser')
    # Remove code blocks if configured
    if REMOVE_CODE:
        for code_tag in soup.find_all('code'):
            code_tag.decompose()
    return soup.get_text(separator=' ', strip=True)


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()


def format_as_instruction(question: str, answer: str) -> str:
    """Format Q&A pair in Llama-2 instruction format."""
    return f"<s>[INST] {question.strip()} [/INST] {answer.strip()} </s>"


def load_and_process_dataset(
    file_path: Path,
    question_col: str,
    answer_col: str
) -> pd.DataFrame:
    """
    Load and process a single dataset.

    Args:
        file_path: Path to CSV file
        question_col: Name of question column
        answer_col: Name of answer column

    Returns:
        DataFrame with processed data
    """
    print(f"\nProcessing: {file_path.name}")

    if not file_path.exists():
        print(f"  ✗ File not found: {file_path}")
        return pd.DataFrame()

    # Load data
    df = pd.read_csv(file_path)
    print(f"  Loaded {len(df)} rows")

    # Check if columns exist
    if question_col not in df.columns or answer_col not in df.columns:
        print(f"  ✗ Required columns not found: {question_col}, {answer_col}")
        return pd.DataFrame()

    # Clean HTML
    df['question_clean'] = df[question_col].apply(clean_html)
    df['answer_clean'] = df[answer_col].apply(clean_html)

    # Filter out empty entries
    df = df[
        (df['question_clean'].str.len() > 10) &
        (df['answer_clean'].str.len() >= MIN_ANSWER_LEN)
    ]
    print(f"  After removing empty entries: {len(df)} rows")

    # Filter by answer length
    df = df[df['answer_clean'].str.len() <= MAX_ANSWER_LEN]
    print(f"  After answer length filter: {len(df)} rows")

    # Check for code blocks if configured
    if REMOVE_CODE:
        df = df[
            ~df['question_clean'].str.contains('<code>|```', case=False, na=False) &
            ~df['answer_clean'].str.contains('<code>|```', case=False, na=False)
        ]
        print(f"  After removing code blocks: {len(df)} rows")

    # Clean text
    df['question_clean'] = df['question_clean'].apply(clean_text)
    df['answer_clean'] = df['answer_clean'].apply(clean_text)

    # Format as instructions
    df['text'] = df.apply(
        lambda row: format_as_instruction(
            row['question_clean'],
            row['answer_clean']
        ),
        axis=1
    )

    # Filter by total sequence length
    df['text_length'] = df['text'].str.len()
    df = df[df['text_length'] <= MAX_SEQ_LENGTH]
    print(f"  After sequence length filter: {len(df)} rows")

    # Return only the text column
    return df[['text', 'text_length']]


def main():
    """Main preprocessing pipeline."""
    print("=" * 60)
    print("Jenkins Chatbot - Data Preprocessing")
    print("=" * 60)
    print(f"\nSettings:")
    print(f"  Max sequence length: {MAX_SEQ_LENGTH}")
    print(f"  Remove code blocks: {REMOVE_CODE}")
    print(f"  Min answer length: {MIN_ANSWER_LEN}")
    print(f"  Max answer length: {MAX_ANSWER_LEN}")

    # Define datasets to process
    datasets_to_process = [
        {
            'file': RAW_DATA_DIR / 'QueryResultsUpdated.csv',
            'question_col': 'Question Body',
            'answer_col': 'Answer Body',
            'name': 'Stack Overflow'
        },
        {
            'file': RAW_DATA_DIR / 'Jenkins Docs QA.csv',
            'question_col': 'Question',
            'answer_col': 'Answer',
            'name': 'Jenkins Docs'
        },
        {
            'file': RAW_DATA_DIR / 'Community Questions Refined.csv',
            'question_col': 'questions',
            'answer_col': 'answers',
            'name': 'Community Forums'
        }
    ]

    # Process each dataset
    processed_dfs = []
    for dataset_info in datasets_to_process:
        df = load_and_process_dataset(
            dataset_info['file'],
            dataset_info['question_col'],
            dataset_info['answer_col']
        )
        if not df.empty:
            processed_dfs.append(df)
            print(f"  ✓ {dataset_info['name']}: {len(df)} examples")

    if not processed_dfs:
        print("\n✗ No data processed! Check your data files.")
        return

    # Merge all datasets
    print("\nMerging datasets...")
    final_df = pd.concat(processed_dfs, ignore_index=True)
    print(f"Total examples: {len(final_df)}")

    # Shuffle
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save training data
    output_file = OUTPUT_DIR / 'training_data.csv'
    final_df[['text']].to_csv(output_file, index=False)
    print(f"\n✓ Saved training data to: {output_file}")

    # Print statistics
    print("\n" + "=" * 60)
    print("Statistics:")
    print("=" * 60)
    print(f"Total training examples: {len(final_df)}")
    print(f"Average sequence length: {final_df['text_length'].mean():.0f} characters")
    print(f"Min sequence length: {final_df['text_length'].min()}")
    print(f"Max sequence length: {final_df['text_length'].max()}")

    # Show sample
    print("\nSample training example:")
    print("-" * 60)
    print(final_df['text'].iloc[0][:500] + "...")
    print("-" * 60)

    print("\n✓ Preprocessing complete!")
    print(f"Ready for training with {len(final_df)} examples")


if __name__ == "__main__":
    main()
