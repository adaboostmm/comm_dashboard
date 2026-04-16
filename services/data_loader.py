"""
Data loader service for loading and parsing sample JSON data.
Caches data in Streamlit session state for efficiency.
"""

import json
import pandas as pd
import pickle
from pathlib import Path
from typing import Dict, List, Any
import streamlit as st
from config import Config


class DataLoader:
    """Loads and manages sample data from JSON files."""

    def __init__(self):
        self.config = Config()

    @staticmethod
    @st.cache(ttl=3600, allow_output_mutation=True)  # Cache for 1 hour
    def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
        """
        Load a single JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of dictionaries from JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both list and dict formats
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return [data]
        except Exception as e:
            st.error(f"Error loading {file_path.name}: {str(e)}")
            return []

    @staticmethod
    @st.cache(ttl=3600, allow_output_mutation=True)
    def load_inquiries() -> pd.DataFrame:
        """
        Load all inquiry JSON files into a single DataFrame.
        Uses pre-loaded pickle cache if available for fast loading.

        Returns:
            DataFrame with inquiry data
        """
        # Try to load from pickle cache first (much faster)
        cache_path = Path(".cache/inquiries.pkl")
        if cache_path.exists():
            try:
                return pd.read_pickle(cache_path)
            except Exception as e:
                st.warning(f"Could not load cached data: {e}. Loading from JSON files...")

        # Fallback to loading from JSON files
        files = Config.get_sample_data_files()["inquiries"]
        all_inquiries = []

        for file_path in files:
            data = DataLoader.load_json_file(file_path)
            all_inquiries.extend(data)

        if not all_inquiries:
            return pd.DataFrame()

        df = pd.DataFrame(all_inquiries)

        # Map field names from actual data format
        field_mapping = {
            'id': 'inquiry_id',
            'timestamp': 'date_received'
        }

        for old_name, new_name in field_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]

        # Convert date strings to datetime
        if 'date_received' in df.columns:
            df['date_received'] = pd.to_datetime(df['date_received'], errors='coerce', utc=True)

        # Add status column if missing (not in sample data)
        if 'status' not in df.columns:
            df['status'] = 'open'

        # Ensure required columns exist
        required_columns = ['inquiry_id', 'sender_name', 'sender_organization',
                           'subject', 'body', 'source', 'priority']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df

    @staticmethod
    @st.cache(ttl=3600, allow_output_mutation=True)
    def load_news_articles() -> pd.DataFrame:
        """
        Load all news article JSON files into a single DataFrame.
        Uses pre-loaded pickle cache if available for fast loading.

        Returns:
            DataFrame with news article data
        """
        # Try to load from pickle cache first (much faster)
        cache_path = Path(".cache/news.pkl")
        if cache_path.exists():
            try:
                return pd.read_pickle(cache_path)
            except Exception as e:
                st.warning(f"Could not load cached news data: {e}. Loading from JSON files...")

        # Fallback to loading from JSON files
        files = Config.get_sample_data_files()["news"]
        all_articles = []

        for file_path in files:
            data = DataLoader.load_json_file(file_path)
            all_articles.extend(data)

        if not all_articles:
            return pd.DataFrame()

        df = pd.DataFrame(all_articles)

        # Map field names from actual data format
        field_mapping = {
            'id': 'article_id',
            'full_text': 'content',
            'entities_mentioned': 'entities'
        }

        for old_name, new_name in field_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]

        # Normalize sentiment_score to 0-1 range if it's -1 to 1
        if 'sentiment_score' in df.columns:
            # Check if values are in -1 to 1 range
            if df['sentiment_score'].min() < 0:
                # Convert from -1 to 1 range to 0 to 1 range
                df['sentiment_score'] = (df['sentiment_score'] + 1) / 2

        # Convert date strings to datetime
        if 'published_date' in df.columns:
            df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce', utc=True)

        # Add URL if missing
        if 'url' not in df.columns:
            df['url'] = None

        # Ensure required columns exist
        required_columns = ['article_id', 'headline', 'source', 'content', 'sentiment_score']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df

    @staticmethod
    @st.cache(ttl=3600, allow_output_mutation=True)
    def load_social_media() -> pd.DataFrame:
        """
        Load all social media JSON files into a single DataFrame.
        Uses pre-loaded pickle cache if available for fast loading.

        Returns:
            DataFrame with social media data
        """
        # Try to load from pickle cache first (much faster)
        cache_path = Path(".cache/social.pkl")
        if cache_path.exists():
            try:
                return pd.read_pickle(cache_path)
            except Exception as e:
                st.warning(f"Could not load cached social data: {e}. Loading from JSON files...")

        # Fallback to loading from JSON files
        files = Config.get_sample_data_files()["social_media"]
        all_posts = []

        for file_path in files:
            data = DataLoader.load_json_file(file_path)
            all_posts.extend(data)

        if not all_posts:
            return pd.DataFrame()

        df = pd.DataFrame(all_posts)

        # Map field names from actual data format
        field_mapping = {
            'id': 'post_id',
            'text': 'content'
        }

        for old_name, new_name in field_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]

        # Normalize sentiment_score to 0-1 range if it's -1 to 1
        if 'sentiment_score' in df.columns:
            # Check if values are in -1 to 1 range
            if df['sentiment_score'].min() < 0:
                # Convert from -1 to 1 range to 0 to 1 range
                df['sentiment_score'] = (df['sentiment_score'] + 1) / 2

        # Convert date strings to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)

        # Add engagement if missing
        if 'engagement' not in df.columns:
            df['engagement'] = 0

        # Ensure required columns exist
        required_columns = ['post_id', 'platform', 'author', 'content', 'sentiment_score']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df

    @staticmethod
    @st.cache(ttl=3600, allow_output_mutation=True)
    def load_response_templates() -> List[Dict[str, Any]]:
        """
        Load response templates from JSON files.
        Uses pre-loaded pickle cache if available for fast loading.

        Returns:
            List of response template dictionaries
        """
        # Try to load from pickle cache first (much faster)
        cache_path = Path(".cache/templates.pkl")
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                st.warning(f"Could not load cached templates: {e}. Loading from JSON files...")

        # Fallback to loading from JSON files
        files = Config.get_sample_data_files()["response_templates"]
        all_templates = []

        for file_path in files:
            data = DataLoader.load_json_file(file_path)
            all_templates.extend(data)

        return all_templates

    @staticmethod
    def load_all_data() -> Dict[str, Any]:
        """
        Load all data types into a dictionary.

        Returns:
            Dictionary with keys: inquiries, news, social_media, templates
        """
        return {
            "inquiries": DataLoader.load_inquiries(),
            "news": DataLoader.load_news_articles(),
            "social_media": DataLoader.load_social_media(),
            "templates": DataLoader.load_response_templates()
        }

    @staticmethod
    def get_data_summary(data: Dict[str, Any]) -> Dict[str, int]:
        """
        Get summary statistics for loaded data.

        Args:
            data: Dictionary from load_all_data()

        Returns:
            Dictionary with counts for each data type
        """
        summary = {
            "inquiries_count": len(data["inquiries"]) if isinstance(data["inquiries"], pd.DataFrame) else 0,
            "news_count": len(data["news"]) if isinstance(data["news"], pd.DataFrame) else 0,
            "social_media_count": len(data["social_media"]) if isinstance(data["social_media"], pd.DataFrame) else 0,
            "templates_count": len(data["templates"]) if isinstance(data["templates"], list) else 0
        }
        return summary

    @staticmethod
    def initialize_session_state():
        """Initialize Streamlit session state with loaded data."""
        if "data_loaded" not in st.session_state:
            with st.spinner("Loading data..."):
                st.session_state.data = DataLoader.load_all_data()
                st.session_state.data_summary = DataLoader.get_data_summary(st.session_state.data)
                st.session_state.data_loaded = True
