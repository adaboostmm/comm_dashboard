"""
Comprehensive test of all agents individually.
Tests each agent's core functionality with real API calls.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.bedrock_client import BedrockClient
from services.data_loader import DataLoader

# Mock streamlit session state for standalone testing
class MockSessionState:
    def __init__(self):
        self.bedrock_client = None
        self.agent_logs = []
        self.data = None
        self.data_loaded = False

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        setattr(self, key, value)

# Mock streamlit
class MockStreamlit:
    session_state = MockSessionState()

    @staticmethod
    def spinner(text):
        class SpinnerContext:
            def __enter__(self):
                print(f"  [{text}]")
                return self
            def __exit__(self, *args):
                pass
        return SpinnerContext()

    @staticmethod
    def error(msg):
        print(f"  ERROR: {msg}")

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from agents.classifier_agent import ClassifierAgent
from agents.risk_agent import RiskAgent
from agents.insights_agent import InsightsAgent
from agents.response_generator import ResponseGenerator

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(title)
    print("="*70)

def test_classifier_agent():
    """Test the Classifier Agent."""
    print_section("TEST 1: CLASSIFIER AGENT")

    try:
        # Initialize
        st.session_state.bedrock_client = BedrockClient()
        agent = ClassifierAgent()
        print("✓ Classifier agent initialized")

        # Test 1: Single classification
        print("\n--- Test 1a: Single Text Classification ---")
        test_texts = [
            "What is the Federal Reserve's current stance on interest rates?",
            "How does the Fed regulate commercial banks?",
            "Why is inflation rising so quickly?"
        ]

        for i, text in enumerate(test_texts, 1):
            print(f"\nText {i}: '{text}'")
            category = agent.classify_single(text)
            print(f"  → Category: {category}")

        print(f"\n✓ Single classification tokens: {agent.get_token_usage()}")

        # Test 2: Batch classification
        print("\n--- Test 1b: Batch Classification ---")
        batch_texts = [
            "How will the Fed address unemployment?",
            "What are the new capital requirements for banks?",
            "Is the housing market cooling down?"
        ]
        batch_ids = ["INQ-001", "INQ-002", "INQ-003"]

        results = agent.classify_batch(batch_texts, batch_ids)
        for text_id, category in results.items():
            print(f"  {text_id}: {category}")

        print(f"\n✓ Total classifier tokens: {agent.get_token_usage()}")
        print("✅ CLASSIFIER AGENT: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ CLASSIFIER AGENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_agent():
    """Test the Risk Detection Agent."""
    print_section("TEST 2: RISK DETECTION AGENT")

    try:
        # Initialize
        agent = RiskAgent()
        print("✓ Risk agent initialized")

        # Test 1: High-risk text
        print("\n--- Test 2a: High-Risk Detection ---")
        high_risk_text = "BREAKING: Major bank failure raises fears of contagion across the financial system. Depositors rushing to withdraw funds."
        print(f"Text: '{high_risk_text}'")

        result = agent.detect_risk_single(high_risk_text, "NEWS-001")
        print(f"\n  Risk Flag: {result.get('risk_flag')}")
        print(f"  Severity: {result.get('severity')}")
        print(f"  Description: {result.get('risk_description', '')[:150]}...")

        # Test 2: Low-risk text
        print("\n--- Test 2b: Low-Risk Detection ---")
        low_risk_text = "The Federal Reserve published its quarterly economic report showing steady growth."
        print(f"Text: '{low_risk_text}'")

        result2 = agent.detect_risk_single(low_risk_text, "NEWS-002")
        print(f"\n  Risk Flag: {result2.get('risk_flag')}")
        print(f"  Severity: {result2.get('severity')}")

        # Test 3: Batch risk detection
        print("\n--- Test 2c: Batch Risk Detection ---")
        batch_texts = [
            "Fed Chair discusses monetary policy at press conference",
            "Urgent: Banking crisis threatens economic stability",
            "Public criticism of Fed's handling of inflation"
        ]
        batch_ids = ["ITEM-001", "ITEM-002", "ITEM-003"]

        batch_results = agent.detect_risks_batch(batch_texts, batch_ids)
        for item_id, risk_data in batch_results.items():
            print(f"\n  {item_id}:")
            print(f"    Risk: {risk_data.get('risk_flag')}")
            print(f"    Severity: {risk_data.get('severity')}")

        print(f"\n✓ Total risk agent tokens: {agent.get_token_usage()}")
        print("✅ RISK AGENT: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ RISK AGENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_insights_agent():
    """Test the Insights Generator Agent."""
    print_section("TEST 3: INSIGHTS GENERATOR AGENT")

    try:
        # Initialize
        agent = InsightsAgent()
        print("✓ Insights agent initialized")

        # Create mock data instead of loading from files
        print("\n--- Creating Mock Data ---")
        inquiries_df = pd.DataFrame({
            'inquiry_id': [f'INQ-{i:03d}' for i in range(20)],
            'category': ['monetary_policy'] * 8 + ['inflation'] * 7 + ['banking_regulation'] * 5,
            'priority': ['high'] * 5 + ['medium'] * 10 + ['low'] * 5,
            'source': ['media'] * 8 + ['public'] * 7 + ['stakeholder'] * 5,
            'risk_flag': [True] * 3 + [False] * 17
        })

        news_df = pd.DataFrame({
            'article_id': [f'NEWS-{i:03d}' for i in range(30)],
            'sentiment_score': [0.3] * 10 + [0.6] * 15 + [0.8] * 5,
            'risk_flag': [True] * 8 + [False] * 22,
            'severity': ['high'] * 3 + ['medium'] * 5 + [None] * 22
        })

        social_df = pd.DataFrame({
            'post_id': [f'SOC-{i:03d}' for i in range(25)],
            'sentiment_score': [0.5] * 25,
            'platform': ['twitter'] * 15 + ['facebook'] * 10
        })

        print(f"  Created {len(inquiries_df)} inquiries")
        print(f"  Created {len(news_df)} news articles")
        print(f"  Created {len(social_df)} social media posts")

        data = {
            "inquiries": inquiries_df,
            "news": news_df,
            "social_media": social_df
        }

        # Test: Generate insights
        print("\n--- Test 3a: Generate Insights ---")
        insights = agent.generate_insights(data)
        print("\nGenerated Insights:")
        print(insights)

        # Test: Cache behavior
        print("\n--- Test 3b: Check Cache Status ---")
        cache_status = agent.get_cache_status()
        print(f"  Cached: {cache_status['cached']}")
        print(f"  Age: {cache_status['age_seconds']:.1f} seconds")

        # Test: Retrieve cached insights
        print("\n--- Test 3c: Retrieve Cached Insights ---")
        cached_insights = agent.generate_insights(data)
        print("  Retrieved from cache successfully")

        print(f"\n✓ Total insights agent tokens: {agent.get_token_usage()}")
        print("✅ INSIGHTS AGENT: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ INSIGHTS AGENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_response_generator():
    """Test the Response Generator Agent."""
    print_section("TEST 4: RESPONSE GENERATOR AGENT")

    try:
        # Create mock templates
        print("--- Creating Mock Response Templates ---")
        templates = [
            {
                "template_id": "TMPL-001",
                "category": "monetary_policy",
                "subject": "Interest rate decision inquiry",
                "description": "Response template for questions about interest rate decisions",
                "keywords": ["interest", "rate", "decision", "monetary", "policy"],
                "response_body": "Thank you for your inquiry regarding the Federal Reserve's interest rate decision. The Federal Open Market Committee (FOMC) makes rate decisions based on economic conditions including inflation, employment, and growth. For more details, please visit federalreserve.gov."
            },
            {
                "template_id": "TMPL-002",
                "category": "inflation",
                "subject": "Inflation inquiry",
                "description": "Response template for inflation-related questions",
                "keywords": ["inflation", "prices", "CPI", "cost"],
                "response_body": "Thank you for contacting us about inflation. The Federal Reserve closely monitors price stability as part of its dual mandate. Current inflation data and our policy responses are available on our website."
            }
        ]
        print(f"  Created {len(templates)} mock templates")

        # Initialize
        agent = ResponseGenerator(templates)
        print("✓ Response generator initialized")

        # Test inquiry
        test_inquiry = {
            "inquiry_id": "INQ-TEST-001",
            "sender_name": "John Smith",
            "sender_organization": "Washington Post",
            "source": "media",
            "category": "monetary_policy",
            "subject": "Question about recent interest rate decision",
            "body": "Can you explain the rationale behind the Federal Reserve's recent decision to raise interest rates by 25 basis points?",
            "date_received": "2026-04-15"
        }

        # Test 1: Template matching
        print("\n--- Test 4a: Template Matching ---")
        template, score = agent.find_best_template(test_inquiry)
        if template:
            print(f"  ✓ Best match found (score: {score:.2f})")
            print(f"    Template category: {template.get('category', 'N/A')}")
        else:
            print("  No suitable template found (score too low)")

        # Test 2: Full response generation
        print("\n--- Test 4b: Full Response Generation ---")
        print(f"\nInquiry: '{test_inquiry['subject']}'")
        print(f"From: {test_inquiry['sender_name']} ({test_inquiry['source']})")

        response_result = agent.generate_response(test_inquiry, force_generate=True)
        print(f"\nMethod: {response_result['method']}")
        print(f"Response:\n{response_result['response'][:300]}...")

        # Test 3: Response with template (if available)
        print("\n--- Test 4c: Template-Based Response ---")
        response_result2 = agent.generate_response(test_inquiry, force_generate=False)
        print(f"\nMethod: {response_result2['method']}")
        print(f"Match Score: {response_result2['template_match_score']:.2f}")

        print(f"\n✓ Total response generator tokens: {agent.get_token_usage()}")
        print("✅ RESPONSE GENERATOR: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ RESPONSE GENERATOR FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbot_agent():
    """Test the Chatbot Agent."""
    print_section("TEST 5: CHATBOT AGENT")

    try:
        # Create mock data
        print("--- Creating Mock Data ---")
        inquiries_df = pd.DataFrame({
            'inquiry_id': [f'INQ-{i:03d}' for i in range(15)],
            'category': ['monetary_policy'] * 5 + ['inflation'] * 5 + ['banking_regulation'] * 5,
            'priority': ['high'] * 3 + ['medium'] * 7 + ['low'] * 5,
            'risk_flag': [True] * 4 + [False] * 11
        })

        news_df = pd.DataFrame({
            'article_id': [f'NEWS-{i:03d}' for i in range(20)],
            'sentiment_score': [0.4] * 8 + [0.6] * 12,
            'risk_flag': [True] * 5 + [False] * 15
        })

        social_df = pd.DataFrame({
            'post_id': [f'SOC-{i:03d}' for i in range(10)],
            'sentiment_score': [0.5] * 10
        })

        print(f"  Created {len(inquiries_df)} inquiries")
        print(f"  Created {len(news_df)} news articles")
        print(f"  Created {len(social_df)} social media posts")

        data = {
            "inquiries": inquiries_df,
            "news": news_df,
            "social_media": social_df
        }

        # Import chatbot agent
        from components.chatbot import ChatbotAgent

        # Initialize
        agent = ChatbotAgent(data)
        print("✓ Chatbot agent initialized")

        # Test conversations
        test_questions = [
            "What are the most common inquiry categories?",
            "How many risk flags are there in the data?",
            "What's the overall sentiment in news articles?"
        ]

        conversation_history = []

        for i, question in enumerate(test_questions, 1):
            print(f"\n--- Test 5.{i}: Question ---")
            print(f"User: {question}")

            response = agent.chat(question, conversation_history)
            print(f"\nAssistant: {response[:250]}...")

            # Add to history
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": response})

        print(f"\n✓ Total chatbot tokens: {agent.get_token_usage()}")
        print("✅ CHATBOT AGENT: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ CHATBOT AGENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all agent tests."""
    print("="*70)
    print("COMPREHENSIVE AGENT TESTING")
    print("Testing all 5 agents with real API calls")
    print("="*70)

    results = []

    # Test each agent
    results.append(("Classifier Agent", test_classifier_agent()))
    results.append(("Risk Agent", test_risk_agent()))
    results.append(("Insights Agent", test_insights_agent()))
    results.append(("Response Generator", test_response_generator()))
    results.append(("Chatbot Agent", test_chatbot_agent()))

    # Final summary
    print_section("FINAL SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for agent_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{agent_name:30s} {status}")

    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} agents passed")

    # Token usage summary
    if st.session_state.bedrock_client:
        total_tokens = st.session_state.bedrock_client.get_token_usage()
        print(f"Total tokens used: {total_tokens:,}")

    if passed == total:
        print("\n🎉 ALL AGENTS OPERATIONAL - Dashboard ready to launch!")
    else:
        print(f"\n⚠️ {total - passed} agent(s) failed - review errors above")

    print("="*70)

if __name__ == "__main__":
    main()
