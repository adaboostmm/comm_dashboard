"""
Test the multi-agent system with real API calls.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.classifier_agent import ClassifierAgent
from agents.risk_agent import RiskAgent
from services.bedrock_client import BedrockClient

# Initialize session state mock (since we're not running in Streamlit)
if not hasattr(st, 'session_state'):
    class SessionState:
        def __init__(self):
            self.bedrock_client = None
            self.agent_logs = []
        def __contains__(self, key):
            return hasattr(self, key)
        def __getitem__(self, key):
            return getattr(self, key)
        def __setitem__(self, key, value):
            setattr(self, key, value)
    st.session_state = SessionState()

def test_classifier_agent():
    """Test the classifier agent."""
    print("\n" + "="*60)
    print("Testing Classifier Agent")
    print("="*60)

    # Initialize shared client
    st.session_state.bedrock_client = BedrockClient()

    # Initialize agent
    agent = ClassifierAgent()
    print("✓ Classifier agent initialized")

    # Test classification
    test_text = "What is the Federal Reserve's current stance on interest rates and inflation?"
    print(f"\nTest input: '{test_text}'")

    try:
        category = agent.classify_single(test_text)
        print(f"✓ Classification result: {category}")

        tokens = agent.get_token_usage()
        print(f"✓ Tokens used: {tokens}")

        return True
    except Exception as e:
        print(f"❌ Classification failed: {str(e)}")
        return False

def test_risk_agent():
    """Test the risk detection agent."""
    print("\n" + "="*60)
    print("Testing Risk Detection Agent")
    print("="*60)

    # Initialize agent
    agent = RiskAgent()
    print("✓ Risk agent initialized")

    # Test risk detection
    test_text = "Breaking: Major bank failure raises concerns about systemic risk in the financial system"
    print(f"\nTest input: '{test_text}'")

    try:
        result = agent.detect_risk(test_text)
        print(f"✓ Risk detection result:")
        print(f"  - Risk Flag: {result.get('risk_flag', False)}")
        print(f"  - Severity: {result.get('severity', 'N/A')}")
        print(f"  - Description: {result.get('risk_description', 'N/A')}")

        tokens = agent.get_token_usage()
        print(f"✓ Tokens used: {tokens}")

        return True
    except Exception as e:
        print(f"❌ Risk detection failed: {str(e)}")
        return False

def main():
    """Run all agent tests."""
    print("="*60)
    print("Multi-Agent System Test")
    print("="*60)

    results = []

    # Test classifier
    results.append(test_classifier_agent())

    # Test risk detector
    results.append(test_risk_agent())

    # Summary
    print("\n" + "="*60)
    if all(results):
        print("✅ All agent tests PASSED")
        total_tokens = st.session_state.bedrock_client.get_token_usage()
        print(f"✅ Total tokens used: {total_tokens}")
    else:
        print("❌ Some agent tests FAILED")
    print("="*60)

if __name__ == "__main__":
    main()
