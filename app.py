"""
Communication Intelligence Dashboard
Main Streamlit application entry point.
"""

import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from services.data_loader import DataLoader
from agents.classifier_agent import ClassifierAgent
from agents.risk_agent import RiskAgent
from components.dashboard import render_dashboard
from components.inquiry_queue import render_inquiry_queue
from components.news_monitor import render_news_monitor
from components.chatbot import render_chatbot
from utils.data_processing import filter_by_date_range, get_date_ranges


# Page configuration
st.set_page_config(
    page_title="Communication Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Load custom CSS for dark theme."""
    css_file = Config.ASSETS_DIR / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            css_content = f.read()
            # Add timestamp comment to force browser to reload CSS
            import time
            css_content += f"\n/* Cache bust: {time.time()} */"
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def initialize_app():
    """Initialize the application and load data."""
    # Load custom CSS
    load_custom_css()

    # Initialize session state
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    # Load data on first run
    if not st.session_state.initialized:
        with st.spinner("Initializing dashboard..."):
            # Load all data
            DataLoader.initialize_session_state()

            # Initialize agents
            initialize_agents()

            st.session_state.initialized = True


def initialize_agents():
    """Initialize and run agents to process data."""
    if "data" not in st.session_state:
        return

    data = st.session_state.data

    # Initialize classifier agent
    if "classifier_agent" not in st.session_state:
        st.session_state.classifier_agent = ClassifierAgent()

    # Initialize risk agent
    if "risk_agent" not in st.session_state:
        st.session_state.risk_agent = RiskAgent()

    # Process data with agents (on first load only)
    if "data_processed" not in st.session_state:
        classifier = st.session_state.classifier_agent
        risk_agent = st.session_state.risk_agent

        # Add mock data for demo mode (fast initialization)
        # Set DEMO_MODE=true in .env to skip LLM processing on startup
        import os
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

        inquiries_df = data.get("inquiries")
        if inquiries_df is not None and not inquiries_df.empty:
            # Add mock categories and risk flags if in demo mode
            if demo_mode:
                if "category" not in inquiries_df.columns or inquiries_df["category"].isna().all():
                    categories = ["monetary_policy", "inflation", "banking_regulation", "interest_rates",
                                  "employment", "financial_stability", "housing", "consumer_protection"]
                    inquiries_df["category"] = [categories[i % len(categories)] for i in range(len(inquiries_df))]

                if "risk_flag" not in inquiries_df.columns or inquiries_df["risk_flag"].isna().all():
                    # Mark some as risks with varied severities
                    inquiries_df["risk_flag"] = [i % 10 == 0 or i % 13 == 0 or i % 17 == 0 for i in range(len(inquiries_df))]

                    # Assign varied severities: low, medium, high
                    def assign_severity(idx, is_risk):
                        if not is_risk:
                            return None
                        severity_cycle = idx % 3
                        return ["low", "medium", "high"][severity_cycle]

                    inquiries_df["severity"] = [assign_severity(i, inquiries_df["risk_flag"].iloc[i]) for i in range(len(inquiries_df))]
                    inquiries_df["risk_description"] = inquiries_df.apply(
                        lambda row: {
                            "low": "Minor concern - monitoring recommended",
                            "medium": "Moderate risk - review needed",
                            "high": "Requires immediate attention"
                        }.get(row["severity"], None) if row["risk_flag"] else None,
                        axis=1
                    )
                data["inquiries"] = inquiries_df
            else:
                # Full LLM processing (slow)
                # Only classify if not already classified
                if "category" not in inquiries_df.columns or inquiries_df["category"].isna().any():
                    with st.spinner("Classifying inquiries..."):
                        data["inquiries"] = classifier.classify_inquiries(inquiries_df)

                # Analyze risks in inquiries
                if "risk_flag" not in inquiries_df.columns or inquiries_df["risk_flag"].isna().any():
                    with st.spinner("Analyzing inquiry risks..."):
                        data["inquiries"] = risk_agent.analyze_inquiry_risks(data["inquiries"])

        # Classify news articles
        news_df = data.get("news")
        if news_df is not None and not news_df.empty:
            if demo_mode:
                if "category" not in news_df.columns or news_df["category"].isna().all():
                    categories = ["monetary_policy", "inflation", "banking_regulation", "interest_rates",
                                  "financial_stability", "housing"]
                    news_df["category"] = [categories[i % len(categories)] for i in range(len(news_df))]

                if "risk_flag" not in news_df.columns or news_df["risk_flag"].isna().all():
                    # Mark some as risks with varied severities
                    news_df["risk_flag"] = [i % 7 == 0 or i % 11 == 0 for i in range(len(news_df))]

                    # Assign varied severities: low, medium, high
                    def assign_news_severity(idx, is_risk):
                        if not is_risk:
                            return None
                        severity_cycle = idx % 3
                        return ["low", "medium", "high"][severity_cycle]

                    news_df["severity"] = [assign_news_severity(i, news_df["risk_flag"].iloc[i]) for i in range(len(news_df))]
                    news_df["risk_description"] = news_df.apply(
                        lambda row: {
                            "low": "Potential minor reputational concern",
                            "medium": "Moderate reputational risk",
                            "high": "Significant reputational concern"
                        }.get(row["severity"], None) if row["risk_flag"] else None,
                        axis=1
                    )
                data["news"] = news_df
            else:
                # Full LLM processing (slow)
                if "category" not in news_df.columns or news_df["category"].isna().any():
                    with st.spinner("Classifying news articles..."):
                        data["news"] = classifier.classify_news(news_df)

                # Analyze risks in news
                if "risk_flag" not in news_df.columns or news_df["risk_flag"].isna().any():
                    with st.spinner("Analyzing news risks..."):
                        data["news"] = risk_agent.analyze_news_risks(data["news"])

        st.session_state.data = data
        st.session_state.data_processed = True


def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        st.title("🏛️ Fed Comms Dashboard")

        st.markdown("---")

        # Navigation first
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📬 Inquiry Queue", "📰 News Monitor", "💬 AI Assistant"],
            key="nav_radio"
        )

        st.markdown("---")

        # Data summary
        if "data_summary" in st.session_state:
            st.subheader("📊 Data Summary")
            summary = st.session_state.data_summary

            st.metric("Inquiries", summary.get("inquiries_count", 0))
            st.metric("News Articles", summary.get("news_count", 0))
            st.metric("Social Posts", summary.get("social_media_count", 0))
            st.metric("Templates", summary.get("templates_count", 0))

        st.markdown("---")

        # System Status
        st.subheader("⚙️ System Status")
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        if demo_mode:
            st.info("🚀 Demo Mode: Fast loading")
        else:
            st.success("✓ Full AI Mode: Active")

        st.markdown("---")

        # Token usage
        if "bedrock_client" in st.session_state:
            st.subheader("💡 Token Usage")
            client = st.session_state.bedrock_client
            total_tokens = client.get_token_usage()

            st.metric("Total Tokens", f"{total_tokens:,}")

            # Warning if getting high
            if total_tokens > 15000:
                st.warning("⚠️ High token usage")
            elif total_tokens > 10000:
                st.info("ℹ️ Moderate token usage")

            # Reset button
            if st.button("Reset Token Counter"):
                client.reset_token_counter()
                st.success("Token counter reset")
                st.experimental_rerun()

        st.markdown("---")

        # Quick Stats
        if "data" in st.session_state:
            st.subheader("📈 Quick Stats")
            data = st.session_state.data

            # Count risks
            risk_count = 0
            inquiries_df = data.get("inquiries")
            news_df = data.get("news")

            if inquiries_df is not None and not inquiries_df.empty and "risk_flag" in inquiries_df.columns:
                risk_count += inquiries_df["risk_flag"].sum() if inquiries_df["risk_flag"].dtype == bool else 0
            if news_df is not None and not news_df.empty and "risk_flag" in news_df.columns:
                risk_count += news_df["risk_flag"].sum() if news_df["risk_flag"].dtype == bool else 0

            st.metric("Active Risks", risk_count)

        st.markdown("---")

        # Info
        st.caption("Communication Intelligence Dashboard v1.0")
        st.caption("Powered by Claude Sonnet 4.5")

    return page  # Return the selected page


def main():
    """Main application function."""
    # Initialize app
    initialize_app()

    # Render sidebar and get selected page
    page = render_sidebar()

    # Check if data is loaded
    if "data" not in st.session_state or not st.session_state.data:
        st.error("Failed to load data. Please check your data files.")
        return

    # Main content area with navigation (compatible with older Streamlit)
    data = st.session_state.data

    # Page title at the top - Use ID selector with gradient
    st.markdown("""
        <style>
        #page-title {
            font-size: 32px !important;
            font-weight: 900 !important;
            color: #4c51bf;
            background: -webkit-linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
            background: linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 20px 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

    if page == "📊 Dashboard":
        st.markdown('<div id="page-title">📊 Communication Intelligence Dashboard</div>', unsafe_allow_html=True)
    elif page == "📬 Inquiry Queue":
        st.markdown('<div id="page-title">📬 Inquiry Queue</div>', unsafe_allow_html=True)
    elif page == "📰 News Monitor":
        st.markdown('<div id="page-title">📰 News Monitor</div>', unsafe_allow_html=True)
    elif page == "💬 AI Assistant":
        st.markdown('<div id="page-title">💬 AI Assistant</div>', unsafe_allow_html=True)

    # Date Range Selector below title
    col_date, col_space = st.columns([3, 1])

    with col_date:
        date_ranges = get_date_ranges(data)
        date_options = [r["label"] for r in date_ranges]

        # Initialize selected range if not set
        if "selected_date_range_idx" not in st.session_state:
            st.session_state.selected_date_range_idx = 0

        selected_label = st.selectbox(
            "📅 Select 7-Day Period:",
            options=date_options,
            index=st.session_state.selected_date_range_idx,
            key="date_range_selector"
        )

        # Get selected date range
        selected_idx = date_options.index(selected_label)
        st.session_state.selected_date_range_idx = selected_idx
        selected_range = date_ranges[selected_idx]

    # Filter data by selected date range
    filtered_data = filter_by_date_range(data, selected_range["start_date"], selected_range["end_date"])

    # Display top-level summary metrics
    st.markdown("---")

    inquiries_df = filtered_data.get("inquiries", pd.DataFrame())
    news_df = filtered_data.get("news", pd.DataFrame())
    social_df = filtered_data.get("social_media", pd.DataFrame())

    # Calculate metrics
    total_inquiries = len(inquiries_df)
    total_news = len(news_df)
    total_social = len(social_df)

    # Calculate risk counts
    risk_count = 0
    if not inquiries_df.empty and "risk_flag" in inquiries_df.columns:
        risk_count += inquiries_df["risk_flag"].sum() if inquiries_df["risk_flag"].dtype == bool else 0
    if not news_df.empty and "risk_flag" in news_df.columns:
        risk_count += news_df["risk_flag"].sum() if news_df["risk_flag"].dtype == bool else 0

    # Calculate high priority inquiries
    high_priority = 0
    if not inquiries_df.empty and "priority" in inquiries_df.columns:
        high_priority = len(inquiries_df[inquiries_df["priority"].str.lower() == "high"])

    # Display metrics in columns (4 columns)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Inquiries",
            value=total_inquiries,
            delta=f"{high_priority} high priority" if high_priority > 0 else None
        )

    with col2:
        st.metric(
            label="News Articles",
            value=total_news
        )

    with col3:
        st.metric(
            label="Social Media Posts",
            value=total_social
        )

    with col4:
        st.metric(
            label="Risk Flags",
            value=risk_count,
            delta="Requires attention" if risk_count > 0 else "None detected",
            delta_color="inverse"
        )

    st.markdown("---")

    # Render selected page with filtered data (titles already shown above)
    if page == "📊 Dashboard":
        render_dashboard(filtered_data)
    elif page == "📬 Inquiry Queue":
        render_inquiry_queue(filtered_data)
    elif page == "📰 News Monitor":
        render_news_monitor(filtered_data)
    elif page == "💬 AI Assistant":
        render_chatbot(filtered_data)


if __name__ == "__main__":
    main()
