"""
Simple API test to verify LLM connectivity.
"""

import os
from services.bedrock_client import BedrockClient, BedrockClientError

def test_api_connection():
    """Test a simple API call."""
    print("Testing AWS Bedrock API connection...")
    print(f"Endpoint: {os.getenv('API_ENDPOINT')}")
    print(f"Model: {os.getenv('MODEL_NAME')}")
    print()

    try:
        # Initialize client
        client = BedrockClient()
        print("✓ Client initialized")

        # Make a simple test call
        print("\nSending test prompt...")
        response = client.simple_completion(
            prompt="Say 'Hello! API connection successful.' in exactly those words.",
            system="You are a helpful assistant.",
            temperature=0.0,
            max_tokens=50,
            cache_system=False
        )

        print(f"\n✓ API Response received:")
        print(f"  {response}")

        # Check token usage
        tokens = client.get_token_usage()
        print(f"\n✓ Token usage: {tokens}")

        print("\n" + "="*60)
        print("✅ API connection test PASSED")
        print("="*60)
        return True

    except BedrockClientError as e:
        print(f"\n❌ API Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check API_KEY in .env file")
        print("  2. Verify API_ENDPOINT is correct")
        print("  3. Check network connectivity")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection()
