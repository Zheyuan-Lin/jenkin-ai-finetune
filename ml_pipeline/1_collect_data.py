"""
Step 1: Collect training data from various sources.
Simple, clean data collection for Jenkins Q&A pairs.
"""
import os
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import yaml
from pathlib import Path

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

OUTPUT_DIR = Path(config['paths']['raw_data'])
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def collect_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """Load existing CSV data."""
    data = []
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return data

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    print(f"Loaded {len(data)} rows from {csv_path}")
    return data


def scrape_jenkins_docs_qa(max_pages: int = 50) -> List[Dict[str, str]]:
    """
    Scrape Jenkins documentation to create Q&A pairs.
    This is a simple example - expand based on actual doc structure.
    """
    qa_pairs = []
    print("Scraping Jenkins documentation...")

    # Example: scrape from specific Jenkins docs pages
    # In production, you'd iterate through documentation pages
    # For now, this is a placeholder showing the structure

    return qa_pairs


def scrape_stackoverflow(tag: str = "jenkins", max_pages: int = 10) -> List[Dict[str, str]]:
    """
    Scrape Stack Overflow questions with Jenkins tag.
    Note: Respect Stack Overflow's API rate limits and terms of service.
    Consider using their official API instead.
    """
    qa_pairs = []
    print(f"Scraping Stack Overflow (tag: {tag})...")

    # Placeholder - in production, use Stack Overflow API
    # https://api.stackexchange.com/docs

    print("Note: Use Stack Overflow API for production scraping")
    print("Example: https://api.stackexchange.com/2.3/questions?tagged=jenkins")

    return qa_pairs


def save_to_csv(data: List[Dict[str, str]], filename: str):
    """Save collected data to CSV."""
    if not data:
        print(f"No data to save for {filename}")
        return

    output_path = OUTPUT_DIR / filename
    fieldnames = list(data[0].keys())

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} rows to {output_path}")


def main():
    """Main data collection pipeline."""
    print("=" * 60)
    print("Jenkins Chatbot - Data Collection")
    print("=" * 60)

    # Check if we already have data in datasets/
    existing_data_path = Path("../datasets")

    if existing_data_path.exists():
        print("\nFound existing datasets directory.")
        print("Using existing data files:")

        # Load existing CSV files
        datasets = {}

        query_results = existing_data_path / "QueryResultsUpdated.csv"
        if query_results.exists():
            datasets['query_results'] = collect_from_csv(str(query_results))
            print(f"  ✓ QueryResultsUpdated.csv: {len(datasets['query_results'])} rows")

        jenkins_docs = existing_data_path / "Jenkins Docs QA.csv"
        if jenkins_docs.exists():
            datasets['jenkins_docs'] = collect_from_csv(str(jenkins_docs))
            print(f"  ✓ Jenkins Docs QA.csv: {len(datasets['jenkins_docs'])} rows")

        community_qs = existing_data_path / "Community Questions Refined.csv"
        if community_qs.exists():
            datasets['community'] = collect_from_csv(str(community_qs))
            print(f"  ✓ Community Questions Refined.csv: {len(datasets['community'])} rows")

        if datasets:
            print(f"\nTotal available data: {sum(len(d) for d in datasets.values())} rows")
            print("\nData collection complete! Using existing datasets.")
            print("If you want to collect new data, implement the scraping functions.")
            return

    print("\nNo existing data found.")
    print("\nTo collect data, you can:")
    print("1. Add CSV files to ../datasets/")
    print("2. Implement web scraping functions in this script")
    print("3. Use the Jenkins API and Stack Overflow API")

    print("\nRecommended data sources:")
    print("  - Jenkins official documentation")
    print("  - Jenkins community forums")
    print("  - Stack Overflow (jenkins tag)")
    print("  - GitHub issues from Jenkins repos")


if __name__ == "__main__":
    main()
