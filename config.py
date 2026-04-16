"""
Configuration management for the Communication Intelligence Dashboard.
Loads environment variables and provides centralized settings.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration class for the application."""

    # API Configuration
    API_KEY = os.getenv("API_KEY")
    API_ENDPOINT = os.getenv("API_ENDPOINT")
    MODEL_NAME = os.getenv("MODEL_NAME", "anthropic.claude-sonnet-4-5-20250929-v1:0")

    # Project paths
    BASE_DIR = Path(__file__).parent
    SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
    SYNTHETIC_DATA_DIR = BASE_DIR / "synthetic_data"
    ASSETS_DIR = BASE_DIR / "assets"

    # Token optimization settings
    CACHE_TTL_SECONDS = 300  # 5 minutes
    MAX_BATCH_SIZE = 10
    CHATBOT_HISTORY_WINDOW = 10  # Messages before summarization

    # UI Settings
    PAGE_SIZE = 20  # Items per page in tables
    CHART_HEIGHT = 400
    CHART_WIDTH = 600

    # Sentiment thresholds
    SENTIMENT_POSITIVE_THRESHOLD = 0.6
    SENTIMENT_NEGATIVE_THRESHOLD = 0.4

    # Risk severity levels
    RISK_LEVELS = ["low", "medium", "high"]

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY:
            raise ValueError("API_KEY not found in environment variables")
        if not cls.API_ENDPOINT:
            raise ValueError("API_ENDPOINT not found in environment variables")
        if not cls.SAMPLE_DATA_DIR.exists():
            raise ValueError(f"Sample data directory not found: {cls.SAMPLE_DATA_DIR}")

    @classmethod
    def get_sample_data_files(cls):
        """Get all JSON files. Uses ONLY synthetic_data if available, otherwise falls back to sample_data."""
        files = {
            "inquiries": [],
            "news": [],
            "social_media": [],
            "response_templates": []
        }

        # Use ONLY synthetic data if it exists (it has complete 6 months of data)
        if cls.SYNTHETIC_DATA_DIR.exists():
            files["inquiries"] = list(cls.SYNTHETIC_DATA_DIR.glob("inquiries_*.json"))
            files["news"] = list(cls.SYNTHETIC_DATA_DIR.glob("news_articles_*.json"))
            files["social_media"] = list(cls.SYNTHETIC_DATA_DIR.glob("social_media_*.json"))

            # Response templates still come from sample_data
            if cls.SAMPLE_DATA_DIR.exists():
                files["response_templates"] = list(cls.SAMPLE_DATA_DIR.glob("response_templates_*.json"))
        # Fallback to sample_data if synthetic doesn't exist
        elif cls.SAMPLE_DATA_DIR.exists():
            files["inquiries"] = list(cls.SAMPLE_DATA_DIR.glob("inquiries_*.json"))
            files["news"] = list(cls.SAMPLE_DATA_DIR.glob("news_articles_*.json"))
            files["social_media"] = list(cls.SAMPLE_DATA_DIR.glob("social_media_*.json"))
            files["response_templates"] = list(cls.SAMPLE_DATA_DIR.glob("response_templates_*.json"))

        return files


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration warning: {e}")
