"""
News Monitor Component - Monitor news articles with sentiment and risk analysis.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from utils.data_processing import (
    filter_dataframe,
    search_dataframe,
    get_sentiment_label,
    get_sentiment_color,
    get_severity_color,
    format_date,
    truncate_text
)
from utils.chart_utils import create_source_bar_chart
import plotly.graph_objects as go


def render_news_monitor(data: Dict[str, Any]):
    """
    Render the news monitor page.

    Args:
        data: Dictionary with news DataFrame
    """
    # Title is now shown in main app.py

    news_df = data.get("news", pd.DataFrame())

    if news_df.empty:
        st.warning("No news articles available")
        return

    # Filters and search
    filters = render_news_filters(news_df)

    # Apply filters
    filtered_df = apply_news_filters(news_df, filters)

    # Display summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Articles", len(filtered_df))

    with col2:
        if "sentiment_score" in filtered_df.columns:
            avg_sentiment = filtered_df["sentiment_score"].mean()
            sentiment_label = get_sentiment_label(avg_sentiment)
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", sentiment_label)

    with col3:
        if "risk_flag" in filtered_df.columns:
            risk_count = filtered_df["risk_flag"].sum() if filtered_df["risk_flag"].dtype == bool else 0
            st.metric("Risk Flags", risk_count)

    with col4:
        if "source" in filtered_df.columns:
            source_count = filtered_df["source"].nunique()
            st.metric("News Sources", source_count)

    st.markdown("---")

    # Source sentiment chart
    if not filtered_df.empty and "source" in filtered_df.columns and "sentiment_score" in filtered_df.columns:
        render_source_sentiment_chart(filtered_df)

    st.markdown("---")

    # Display articles in card layout
    st.subheader(f"📄 Articles ({len(filtered_df)})")

    # Display in 2 columns for card layout
    articles_list = filtered_df.to_dict('records')

    for i in range(0, len(articles_list), 2):
        cols = st.columns(2)

        for col_idx, col in enumerate(cols):
            article_idx = i + col_idx
            if article_idx < len(articles_list):
                with col:
                    render_news_card(articles_list[article_idx])


def render_news_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Render filter controls for news.

    Args:
        df: News DataFrame

    Returns:
        Dictionary with filter values
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        # Source filter
        sources = ["All"] + sorted(df["source"].dropna().unique().tolist())
        source_filter = st.selectbox("Source", sources, key="news_source_filter")

    with col2:
        # Sentiment filter
        sentiment_options = ["All", "Positive", "Neutral", "Negative"]
        sentiment_filter = st.selectbox("Sentiment", sentiment_options, key="news_sentiment_filter")

    with col3:
        # Risk filter
        risk_options = ["All", "With Risks", "No Risks"]
        risk_filter = st.selectbox("Risk Status", risk_options, key="news_risk_filter")

    # Search box
    search_term = st.text_input(
        "🔍 Search articles",
        placeholder="Search by headline or content...",
        key="news_search"
    )

    return {
        "source": None if source_filter == "All" else source_filter,
        "sentiment": sentiment_filter,
        "risk": risk_filter,
        "search": search_term
    }


def apply_news_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to news DataFrame.

    Args:
        df: News DataFrame
        filters: Filter dictionary

    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()

    # Source filter
    if filters.get("source"):
        filtered_df = filter_dataframe(filtered_df, {"source": filters["source"]})

    # Sentiment filter
    sentiment = filters.get("sentiment", "All")
    if sentiment != "All" and "sentiment_score" in filtered_df.columns:
        if sentiment == "Positive":
            filtered_df = filtered_df[filtered_df["sentiment_score"] >= 0.6]
        elif sentiment == "Neutral":
            filtered_df = filtered_df[(filtered_df["sentiment_score"] >= 0.4) & (filtered_df["sentiment_score"] < 0.6)]
        elif sentiment == "Negative":
            filtered_df = filtered_df[filtered_df["sentiment_score"] < 0.4]

    # Risk filter
    risk = filters.get("risk", "All")
    if risk != "All" and "risk_flag" in filtered_df.columns:
        if risk == "With Risks":
            filtered_df = filtered_df[filtered_df["risk_flag"] == True]
        elif risk == "No Risks":
            filtered_df = filtered_df[filtered_df["risk_flag"] == False]

    # Search
    search_term = filters.get("search", "")
    if search_term:
        search_columns = ["headline", "content", "source"]
        filtered_df = search_dataframe(filtered_df, search_term, search_columns)

    # Sort by date (most recent first)
    if "published_date" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("published_date", ascending=False)

    return filtered_df


def render_news_card(article: Dict[str, Any]):
    """
    Render a single news article card.

    Args:
        article: Article dictionary
    """
    # Card container
    with st.container():
        # Risk flag at the top if present
        if article.get("risk_flag", False):
            severity = article.get("severity", "medium")
            st.markdown(
                f"""
                <div style="background-color: {get_severity_color(severity)}; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                    ⚠️ <b>RISK DETECTED</b> - {severity.upper()}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Article header
        st.markdown(f"### {article.get('headline', 'No headline')}")

        # Metadata row (no nested columns)
        source = article.get('source', 'Unknown')
        published_date = format_date(article.get('published_date'))
        st.markdown(f"**Source:** {source} | **Date:** {published_date}")

        # Sentiment indicator
        sentiment_score = article.get('sentiment_score')
        if pd.notna(sentiment_score):
            sentiment_label = get_sentiment_label(sentiment_score)
            sentiment_color = get_sentiment_color(sentiment_score)
            st.markdown(f"**Sentiment:** :{sentiment_color}[{sentiment_label} ({sentiment_score:.2f})]")

        # Expandable content
        with st.expander("Read full article"):
            content = article.get('content', 'No content available')
            st.write(content)

            # Risk description if available
            if article.get("risk_flag", False) and article.get("risk_description"):
                st.warning(f"**Risk Analysis:** {article['risk_description']}")

            # Entities if available
            if "entities" in article and article["entities"]:
                st.markdown("**Mentioned Entities:**")
                entities = article["entities"]
                if isinstance(entities, list):
                    st.write(", ".join(entities))
                else:
                    st.write(entities)

            # URL if available
            if "url" in article and article["url"]:
                st.markdown(f"[Read original article]({article['url']})")

        st.markdown("---")


def render_source_sentiment_chart(df: pd.DataFrame):
    """
    Render a chart showing sentiment by news source.

    Args:
        df: News DataFrame with source and sentiment_score columns
    """
    st.subheader("📊 Sentiment by Source")

    # Calculate average sentiment by source
    source_sentiment = df.groupby("source")["sentiment_score"].agg(["mean", "count"]).reset_index()
    source_sentiment.columns = ["source", "avg_sentiment", "article_count"]
    source_sentiment = source_sentiment.sort_values("avg_sentiment")

    # Create horizontal bar chart
    fig = go.Figure()

    # Color bars based on sentiment
    colors = [get_sentiment_color(score) for score in source_sentiment["avg_sentiment"]]

    fig.add_trace(go.Bar(
        y=source_sentiment["source"],
        x=source_sentiment["avg_sentiment"],
        orientation="h",
        marker=dict(
            color=source_sentiment["avg_sentiment"],
            colorscale=[[0, "#FF6B6B"], [0.5, "#FFD93D"], [1, "#6BCB77"]],
            cmin=0,
            cmax=1
        ),
        text=[f"{score:.2f} ({count} articles)" for score, count in zip(source_sentiment["avg_sentiment"], source_sentiment["article_count"])],
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>Avg Sentiment: %{x:.2f}<extra></extra>"
    ))

    fig.update_layout(
        xaxis_title="Average Sentiment Score",
        yaxis_title="News Source",
        template="plotly_dark",
        height=max(300, len(source_sentiment) * 40),  # Dynamic height
        showlegend=False,
        xaxis=dict(range=[0, 1])
    )

    st.plotly_chart(fig)
