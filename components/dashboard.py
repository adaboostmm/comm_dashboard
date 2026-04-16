"""
Main Dashboard Component - Overview with charts and AI insights.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from utils.chart_utils import (
    create_sentiment_trend_chart,
    create_category_pie_chart,
    create_source_bar_chart,
    create_sentiment_gauge,
    create_risk_distribution_chart
)
from utils.data_processing import calculate_summary_stats
from agents.insights_agent import InsightsAgent


def render_dashboard(data: Dict[str, Any]):
    """
    Render the main dashboard page.

    Args:
        data: Dictionary with inquiries, news, social_media DataFrames
    """
    # Summary metrics at the top are now in main app.py
    # No duplicate metrics here

    # Main charts in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("7-Day Sentiment Trend")

        # Sentiment legend
        st.markdown(
            """
            <div style="background-color: #f8fafc; padding: 10px; border-radius: 6px; margin-bottom: 10px; font-size: 13px;">
                <b>Sentiment Scale:</b>
                <span style="color: #ef4444;">■</span> Negative (0.0-0.4) |
                <span style="color: #f59e0b;">■</span> Neutral (0.4-0.6) |
                <span style="color: #10b981;">■</span> Positive (0.6-1.0)
            </div>
            """,
            unsafe_allow_html=True
        )

        sentiment_chart = create_sentiment_trend_chart(
            data.get("inquiries", pd.DataFrame()),
            data.get("news", pd.DataFrame()),
            data.get("social_media", pd.DataFrame())
        )
        st.plotly_chart(sentiment_chart)

    with col2:
        st.subheader("Inquiry Categories")
        category_chart = create_category_pie_chart(
            data.get("inquiries", pd.DataFrame())
        )
        st.plotly_chart(category_chart)

    # Second row
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Source Breakdown")
        source_chart = create_source_bar_chart(
            data.get("inquiries", pd.DataFrame())
        )
        st.plotly_chart(source_chart)

    with col4:
        st.subheader("Risk Distribution")
        # Combine news and inquiries for risk analysis
        news_df = data.get("news", pd.DataFrame())
        inquiries_df = data.get("inquiries", pd.DataFrame())

        risk_df = pd.DataFrame()
        if not news_df.empty and "severity" in news_df.columns:
            risk_df = pd.concat([risk_df, news_df[["severity"]]], ignore_index=True)
        if not inquiries_df.empty and "severity" in inquiries_df.columns:
            risk_df = pd.concat([risk_df, inquiries_df[["severity"]]], ignore_index=True)

        risk_chart = create_risk_distribution_chart(risk_df)
        st.plotly_chart(risk_chart)

    st.markdown("---")

    # AI Insights section
    render_ai_insights(data)


def render_summary_metrics(data: Dict[str, Any]):
    """
    Render summary metric cards.

    Args:
        data: Dictionary with DataFrames
    """
    inquiries_df = data.get("inquiries", pd.DataFrame())
    news_df = data.get("news", pd.DataFrame())
    social_df = data.get("social_media", pd.DataFrame())

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

    # Display metrics in columns (4 columns instead of 5)
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


def render_ai_insights(data: Dict[str, Any]):
    """
    Render AI-generated insights section.

    Args:
        data: Dictionary with DataFrames
    """
    st.subheader("🤖 AI-Generated Insights")

    # Create columns for insights and controls
    col1, col2 = st.columns([4, 1])

    with col2:
        refresh_button = st.button("🔄 Refresh")

        # Show cache status
        if "insights_agent" in st.session_state:
            agent = st.session_state.insights_agent
            cache_status = agent.get_cache_status()
            if cache_status["cached"]:
                expires_in = int(cache_status["expires_in_seconds"])
                st.caption(f"Cache expires in {expires_in}s")

    with col1:
        # Get or create insights agent
        if "insights_agent" not in st.session_state:
            st.session_state.insights_agent = InsightsAgent()

        agent = st.session_state.insights_agent

        # Generate insights
        try:
            with st.spinner("Generating insights..."):
                insights = agent.generate_insights(data, force_refresh=refresh_button)

            # Display insights in a nice box
            st.markdown(
                f"""
                <div style="background-color: #e0f2fe; padding: 24px; border-radius: 12px; border-left: 5px solid #3b82f6; color: #1e293b; line-height: 1.8; font-size: 15px;">
                {insights}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Show token usage
            tokens_used = agent.get_token_usage()
            if tokens_used > 0:
                st.caption(f"💡 Tokens used by insights agent: {tokens_used:,}")

        except Exception as e:
            st.error(f"Failed to generate insights: {str(e)}")
            st.markdown(
                """
                <div style="background-color: #262730; padding: 20px; border-radius: 8px;">
                • Dashboard loaded successfully with all data sources
                • Use the refresh button to generate AI insights
                • Check other tabs for detailed analysis
                </div>
                """,
                unsafe_allow_html=True
            )


def show_data_quality_info(data: Dict[str, Any]):
    """
    Show data quality information in an expander.

    Args:
        data: Dictionary with DataFrames
    """
    with st.expander("📋 Data Quality & Coverage"):
        inquiries_df = data.get("inquiries", pd.DataFrame())
        news_df = data.get("news", pd.DataFrame())
        social_df = data.get("social_media", pd.DataFrame())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Inquiries**")
            if not inquiries_df.empty:
                st.write(f"- Total: {len(inquiries_df)}")
                if "date_received" in inquiries_df.columns:
                    date_range = inquiries_df["date_received"].agg(["min", "max"])
                    st.write(f"- Date range: {date_range['min'].date()} to {date_range['max'].date()}")
                if "category" in inquiries_df.columns:
                    categorized = inquiries_df["category"].notna().sum()
                    st.write(f"- Categorized: {categorized}/{len(inquiries_df)}")
            else:
                st.write("No data available")

        with col2:
            st.write("**News Articles**")
            if not news_df.empty:
                st.write(f"- Total: {len(news_df)}")
                if "published_date" in news_df.columns:
                    date_range = news_df["published_date"].agg(["min", "max"])
                    st.write(f"- Date range: {date_range['min'].date()} to {date_range['max'].date()}")
                if "sentiment_score" in news_df.columns:
                    avg_sent = news_df["sentiment_score"].mean()
                    st.write(f"- Avg sentiment: {avg_sent:.2f}")
            else:
                st.write("No data available")

        with col3:
            st.write("**Social Media**")
            if not social_df.empty:
                st.write(f"- Total: {len(social_df)}")
                if "platform" in social_df.columns:
                    platforms = social_df["platform"].nunique()
                    st.write(f"- Platforms: {platforms}")
                if "sentiment_score" in social_df.columns:
                    avg_sent = social_df["sentiment_score"].mean()
                    st.write(f"- Avg sentiment: {avg_sent:.2f}")
            else:
                st.write("No data available")
