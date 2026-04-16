"""
Quick setup verification script.
Run this to test that the environment is configured correctly before launching the full app.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    required_packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
        ('dotenv', 'Python-dotenv'),
        ('requests', 'Requests'),
        ('tenacity', 'Tenacity')
    ]

    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - MISSING")
            missing.append(name)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✓ All packages installed")
    return True


def test_config():
    """Test configuration files."""
    print("\nTesting configuration...")

    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("  ✗ .env file missing")
        print("  Copy .env.example to .env and fill in your API credentials")
        return False

    print("  ✓ .env file exists")

    # Try to load config
    try:
        from config import Config
        Config.validate()
        print("  ✓ Configuration valid")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_data_files():
    """Test that sample data files exist."""
    print("\nTesting data files...")

    sample_data_dir = Path("sample_data")
    if not sample_data_dir.exists():
        print("  ✗ sample_data directory missing")
        return False

    print("  ✓ sample_data directory exists")

    # Count files
    inquiries = list(sample_data_dir.glob("inquiries_*.json"))
    news = list(sample_data_dir.glob("news_articles_*.json"))
    social = list(sample_data_dir.glob("social_media_*.json"))
    templates = list(sample_data_dir.glob("response_templates_*.json"))

    print(f"  ✓ Found {len(inquiries)} inquiry files")
    print(f"  ✓ Found {len(news)} news files")
    print(f"  ✓ Found {len(social)} social media files")
    print(f"  ✓ Found {len(templates)} template files")

    if not inquiries or not news:
        print("  ⚠ Warning: Missing some data files (app will still work)")

    return True


def test_data_loading():
    """Test that data can be loaded."""
    print("\nTesting data loading...")

    try:
        from services.data_loader import DataLoader

        # Try to load each type
        inquiries = DataLoader.load_inquiries()
        print(f"  ✓ Loaded {len(inquiries)} inquiries")

        news = DataLoader.load_news_articles()
        print(f"  ✓ Loaded {len(news)} news articles")

        social = DataLoader.load_social_media()
        print(f"  ✓ Loaded {len(social)} social media posts")

        templates = DataLoader.load_response_templates()
        print(f"  ✓ Loaded {len(templates)} response templates")

        return True

    except Exception as e:
        print(f"  ✗ Data loading failed: {e}")
        return False


def test_api_connection():
    """Test API connection (optional)."""
    print("\nTesting API connection (optional)...")

    try:
        from services.bedrock_client import BedrockClient

        client = BedrockClient()
        print("  ✓ Bedrock client initialized")
        print("  ℹ Skipping actual API call to save tokens")
        print("  ℹ API will be tested when you first use the app")

        return True

    except Exception as e:
        print(f"  ✗ Client initialization failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Communication Intelligence Dashboard - Setup Verification")
    print("=" * 60)

    results = [
        test_imports(),
        test_config(),
        test_data_files(),
        test_data_loading(),
        test_api_connection()
    ]

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! You're ready to run the dashboard.")
        print("\nTo start the dashboard, run:")
        print("  streamlit run app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Configure .env: Copy .env.example to .env")
        print("  - Check data files: Ensure sample_data/ has JSON files")
    print("=" * 60)


if __name__ == "__main__":
    main()
