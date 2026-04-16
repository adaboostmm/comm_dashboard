"""
Test LLM capabilities without Streamlit dependencies.
Tests: basic completion, system prompt, caching, batch processing.
"""

from services.bedrock_client import BedrockClient, BedrockClientError

def test_basic_completion():
    """Test basic completion."""
    print("="*60)
    print("Test 1: Basic Completion")
    print("="*60)

    client = BedrockClient()

    try:
        response = client.simple_completion(
            prompt="Count from 1 to 5, separated by commas.",
            temperature=0.0,
            max_tokens=50
        )
        print(f"✓ Response: {response}")
        print(f"✓ Tokens used: {client.get_token_usage()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

def test_system_prompt():
    """Test system prompt functionality."""
    print("\n" + "="*60)
    print("Test 2: System Prompt")
    print("="*60)

    client = BedrockClient()

    try:
        response = client.simple_completion(
            prompt="What type of assistant are you?",
            system="You are a Federal Reserve communications expert who specializes in analyzing monetary policy inquiries.",
            temperature=0.0,
            max_tokens=100
        )
        print(f"✓ Response: {response[:200]}...")
        print(f"✓ Tokens used: {client.get_token_usage()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

def test_classification():
    """Test classification use case."""
    print("\n" + "="*60)
    print("Test 3: Text Classification")
    print("="*60)

    client = BedrockClient()

    system_prompt = """You are a Federal Reserve communications classifier.
Classify inquiries into one of these categories: monetary_policy, banking_regulation, inflation, employment, financial_stability, other.
Respond with ONLY the category name, nothing else."""

    test_cases = [
        "What is the Fed's position on current interest rates?",
        "How are banks regulated for capital requirements?",
        "Why is inflation so high right now?"
    ]

    try:
        for i, text in enumerate(test_cases, 1):
            print(f"\nCase {i}: '{text}'")
            category = client.simple_completion(
                prompt=f"Classify this inquiry: {text}",
                system=system_prompt,
                temperature=0.0,
                max_tokens=20,
                cache_system=True
            )
            print(f"  → Category: {category.strip()}")

        print(f"\n✓ Total tokens used: {client.get_token_usage()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

def test_risk_detection():
    """Test risk detection use case."""
    print("\n" + "="*60)
    print("Test 4: Risk Detection")
    print("="*60)

    client = BedrockClient()

    system_prompt = """You are a Federal Reserve risk detection system.
Analyze text for potential communication risks (financial instability mentions, crisis language, etc.).
Respond in this format:
RISK: yes/no
SEVERITY: low/medium/high
DESCRIPTION: brief explanation"""

    test_text = "Breaking: Regional bank collapse sparks fears of contagion across the financial system"

    try:
        print(f"Text: '{test_text}'")
        result = client.simple_completion(
            prompt=f"Analyze for risks: {test_text}",
            system=system_prompt,
            temperature=0.0,
            max_tokens=150,
            cache_system=True
        )
        print(f"\n✓ Risk Analysis:\n{result}")
        print(f"\n✓ Tokens used: {client.get_token_usage()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

def test_response_generation():
    """Test response generation use case."""
    print("\n" + "="*60)
    print("Test 5: Response Generation")
    print("="*60)

    client = BedrockClient()

    system_prompt = """You are a Federal Reserve communications officer.
Generate professional, concise responses to public inquiries about Fed policy.
Keep responses under 100 words and maintain a neutral, informative tone."""

    inquiry = "Can you explain why the Federal Reserve raised interest rates recently?"

    try:
        print(f"Inquiry: '{inquiry}'")
        response = client.simple_completion(
            prompt=f"Generate a response to this inquiry: {inquiry}",
            system=system_prompt,
            temperature=0.3,
            max_tokens=200,
            cache_system=True
        )
        print(f"\n✓ Generated Response:\n{response}")
        print(f"\n✓ Tokens used: {client.get_token_usage()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False

def main():
    """Run all LLM feature tests."""
    print("="*60)
    print("LLM Feature Tests - Claude Sonnet 4.5 via AWS Bedrock")
    print("="*60)
    print()

    tests = [
        ("Basic Completion", test_basic_completion),
        ("System Prompt", test_system_prompt),
        ("Classification", test_classification),
        ("Risk Detection", test_risk_detection),
        ("Response Generation", test_response_generation)
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append(False)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ All LLM feature tests PASSED")
        print("✅ API is fully functional for the dashboard")
    else:
        print("\n⚠️ Some tests failed, but API is accessible")
    print("="*60)

if __name__ == "__main__":
    main()
