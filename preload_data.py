"""
Pre-load all JSON data and save to pickle files for fast loading.
Run this once after generating synthetic data.
"""

import json
import pandas as pd
import pickle
from pathlib import Path
from config import Config
from typing import Dict, List, Any


def load_all_json_files(file_list: List[Path]) -> List[Dict[str, Any]]:
    """Load all JSON files from a list."""
    all_data = []
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'data' in data:
                    all_data.extend(data['data'])
                elif isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"Error loading {file_path.name}: {str(e)}")
    return all_data


def preprocess_inquiries(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess inquiries DataFrame."""
    # Convert timestamp to datetime FIRST, before any mapping
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)

    # Map field names
    field_mapping = {
        'id': 'inquiry_id',
        'timestamp': 'date_received'
    }
    for old_name, new_name in field_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]

    # Date conversion already done above
    if 'date_received' in df.columns:
        print(f'     After mapping: {df["date_received"].notna().sum()} non-null, {df["date_received"].isna().sum()} null')

    # Add status
    if 'status' not in df.columns:
        df['status'] = 'open'

    # Ensure required columns
    required_columns = ['inquiry_id', 'sender_name', 'sender_organization',
                       'subject', 'body', 'source', 'priority']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    return df


def preprocess_news(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess news DataFrame."""
    # Map field names
    field_mapping = {
        'id': 'article_id',
        'full_text': 'content',
        'entities_mentioned': 'entities'
    }
    for old_name, new_name in field_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]

    # Normalize sentiment
    if 'sentiment_score' in df.columns:
        if df['sentiment_score'].min() < 0:
            df['sentiment_score'] = (df['sentiment_score'] + 1) / 2

    # Convert dates
    if 'published_date' in df.columns:
        df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce', utc=True)

    # Add URL
    if 'url' not in df.columns:
        df['url'] = None

    # Ensure required columns
    required_columns = ['article_id', 'headline', 'source', 'content', 'sentiment_score']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    return df


def preprocess_social(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess social media DataFrame."""
    # Map field names
    field_mapping = {
        'id': 'post_id',
        'text': 'content'
    }
    for old_name, new_name in field_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]

    # Normalize sentiment
    if 'sentiment_score' in df.columns:
        if df['sentiment_score'].min() < 0:
            df['sentiment_score'] = (df['sentiment_score'] + 1) / 2

    # Convert dates
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)

    # Add engagement
    if 'engagement' not in df.columns:
        df['engagement'] = 0

    # Ensure required columns
    required_columns = ['post_id', 'platform', 'author', 'content', 'sentiment_score']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    return df


def main():
    """Pre-load all data and save to pickle files."""
    print("="*80)
    print("PRE-LOADING DATA")
    print("="*80)

    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)

    files = Config.get_sample_data_files()

    # Load inquiries
    print("\n1. Loading inquiries...")
    inquiry_data = load_all_json_files(files["inquiries"])
    df_inquiries = pd.DataFrame(inquiry_data)
    df_inquiries = preprocess_inquiries(df_inquiries)
    print(f"   Loaded {len(df_inquiries)} inquiries")
    print(f"   Date range: {df_inquiries['date_received'].min()} to {df_inquiries['date_received'].max()}")

    # Save to pickle
    pickle_path = cache_dir / "inquiries.pkl"
    df_inquiries.to_pickle(pickle_path)
    print(f"   Saved to {pickle_path}")

    # Load news
    print("\n2. Loading news articles...")
    news_data = load_all_json_files(files["news"])
    df_news = pd.DataFrame(news_data)
    df_news = preprocess_news(df_news)
    print(f"   Loaded {len(df_news)} news articles")
    print(f"   Date range: {df_news['published_date'].min()} to {df_news['published_date'].max()}")

    pickle_path = cache_dir / "news.pkl"
    df_news.to_pickle(pickle_path)
    print(f"   Saved to {pickle_path}")

    # Load social media
    print("\n3. Loading social media posts...")
    social_data = load_all_json_files(files["social_media"])
    df_social = pd.DataFrame(social_data)
    df_social = preprocess_social(df_social)
    print(f"   Loaded {len(df_social)} social media posts")
    print(f"   Date range: {df_social['timestamp'].min()} to {df_social['timestamp'].max()}")

    pickle_path = cache_dir / "social.pkl"
    df_social.to_pickle(pickle_path)
    print(f"   Saved to {pickle_path}")

    # Load templates
    print("\n4. Loading response templates...")
    template_data = load_all_json_files(files["response_templates"])
    print(f"   Loaded {len(template_data)} templates")

    pickle_path = cache_dir / "templates.pkl"
    with open(pickle_path, 'wb') as f:
        pickle.dump(template_data, f)
    print(f"   Saved to {pickle_path}")

    print("\n" + "="*80)
    print("✅ PRE-LOADING COMPLETE!")
    print("="*80)
    print("\nPickle files created in .cache/ directory")
    print("Streamlit will now load instantly from these cached files.")
    print("\nRe-run this script if you:")
    print("  - Add new JSON data files")
    print("  - Modify existing JSON files")
    print("  - Change data preprocessing logic")


if __name__ == "__main__":
    main()
