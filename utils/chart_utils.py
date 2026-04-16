"""
Chart utilities for creating Plotly visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any
from config import Config

# Global font configuration for all charts - matching Quick Stats style
CHART_FONT = dict(
    family="Arial, sans-serif",
    size=16,
    color="#1a202c"
)

CHART_TITLE_FONT = dict(
    family="Arial, sans-serif",
    size=20,
    color="#1a202c",
    weight=700
)

AXIS_TITLE_FONT = dict(
    family="Arial, sans-serif",
    size=18,
    color="#1a202c"
)

LEGEND_FONT = dict(
    family="Arial, sans-serif",
    size=15,
    color="#1a202c"
)


def create_sentiment_trend_chart(
    inquiries_df: pd.DataFrame,
    news_df: pd.DataFrame,
    social_df: pd.DataFrame
) -> go.Figure:
    """
    Create a 7-day sentiment trend line chart.

    Args:
        inquiries_df: Inquiries DataFrame with date_received and sentiment_score
        news_df: News DataFrame with published_date and sentiment_score
        social_df: Social media DataFrame with timestamp and sentiment_score

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Add inquiries trend line
    if not inquiries_df.empty and "date_received" in inquiries_df.columns and "sentiment_score" in inquiries_df.columns:
        # Convert to datetime if not already
        inquiries_df_copy = inquiries_df.copy()
        inquiries_df_copy["date_received"] = pd.to_datetime(inquiries_df_copy["date_received"], errors='coerce', utc=True)

        # Remove rows with NaT dates
        inquiries_df_copy = inquiries_df_copy.dropna(subset=["date_received"])

        if not inquiries_df_copy.empty:
            inquiries_trend = inquiries_df_copy.groupby(
                inquiries_df_copy["date_received"].dt.date
            )["sentiment_score"].mean().reset_index()
            inquiries_trend.columns = ["date", "sentiment"]

            fig.add_trace(go.Scatter(
                x=inquiries_trend["date"],
                y=inquiries_trend["sentiment"],
                mode="lines+markers",
                name="Inquiries",
                line=dict(color="#FF8C00", width=2),
                marker=dict(size=6)
            ))

    # Add news trend line
    if not news_df.empty and "published_date" in news_df.columns and "sentiment_score" in news_df.columns:
        # Convert to datetime if not already
        news_df_copy = news_df.copy()
        news_df_copy["published_date"] = pd.to_datetime(news_df_copy["published_date"], errors='coerce', utc=True)

        # Remove rows with NaT dates
        news_df_copy = news_df_copy.dropna(subset=["published_date"])

        if not news_df_copy.empty:
            news_trend = news_df_copy.groupby(
                news_df_copy["published_date"].dt.date
            )["sentiment_score"].mean().reset_index()
            news_trend.columns = ["date", "sentiment"]

            fig.add_trace(go.Scatter(
                x=news_trend["date"],
                y=news_trend["sentiment"],
                mode="lines+markers",
                name="News",
                line=dict(color="#4169E1", width=2),
                marker=dict(size=6)
            ))

    # Add social media trend line
    if not social_df.empty and "timestamp" in social_df.columns and "sentiment_score" in social_df.columns:
        # Convert to datetime if not already
        social_df_copy = social_df.copy()
        social_df_copy["timestamp"] = pd.to_datetime(social_df_copy["timestamp"], errors='coerce', utc=True)

        # Remove rows with NaT dates
        social_df_copy = social_df_copy.dropna(subset=["timestamp"])

        if not social_df_copy.empty:
            social_trend = social_df_copy.groupby(
                social_df_copy["timestamp"].dt.date
            )["sentiment_score"].mean().reset_index()
            social_trend.columns = ["date", "sentiment"]

            fig.add_trace(go.Scatter(
                x=social_trend["date"],
                y=social_trend["sentiment"],
                mode="lines+markers",
                name="Social Media",
                line=dict(color="#32CD32", width=2),
                marker=dict(size=6)
            ))

    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Sentiment Score",
        template="plotly_white",
        hovermode="x unified",
        height=Config.CHART_HEIGHT,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=LEGEND_FONT),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=20, b=40, l=40, r=20),
        font=CHART_FONT,
        xaxis=dict(titlefont=AXIS_TITLE_FONT, tickfont=CHART_FONT),
        yaxis=dict(titlefont=AXIS_TITLE_FONT, tickfont=CHART_FONT)
    )

    return fig


def create_category_pie_chart(df: pd.DataFrame, category_column: str = "category") -> go.Figure:
    """
    Create a pie chart for category distribution.

    Args:
        df: DataFrame with category column
        category_column: Name of the category column

    Returns:
        Plotly figure
    """
    if df.empty or category_column not in df.columns:
        # Return empty chart
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=Config.CHART_HEIGHT,
            margin=dict(t=20, b=20, l=20, r=20),
            font=CHART_FONT
        )
        return fig

    category_counts = df[category_column].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=category_counts.index,
        values=category_counts.values,
        hole=0.3,  # Donut chart
        marker=dict(
            colors=px.colors.qualitative.Set3
        ),
        textfont=dict(size=18, color="#1a202c", family="Arial, sans-serif"),
        textposition="inside"
    )])

    fig.update_layout(
        template="plotly_white",
        height=Config.CHART_HEIGHT,
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        font=CHART_FONT
    )

    return fig


def create_source_bar_chart(df: pd.DataFrame, source_column: str = "source") -> go.Figure:
    """
    Create a horizontal bar chart for source distribution.

    Args:
        df: DataFrame with source column
        source_column: Name of the source column

    Returns:
        Plotly figure
    """
    if df.empty or source_column not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=Config.CHART_HEIGHT,
            margin=dict(t=20, b=40, l=40, r=20),
            font=CHART_FONT
        )
        return fig

    source_counts = df[source_column].value_counts()

    fig = go.Figure(data=[go.Bar(
        x=source_counts.values,
        y=source_counts.index,
        orientation="h",
        marker=dict(
            color=source_counts.values,
            colorscale="Viridis"
        )
    )])

    fig.update_layout(
        xaxis_title="Count",
        yaxis_title="Source",
        template="plotly_white",
        height=Config.CHART_HEIGHT,
        showlegend=False,
        margin=dict(t=20, b=40, l=100, r=20),
        font=CHART_FONT,
        xaxis=dict(titlefont=AXIS_TITLE_FONT, tickfont=CHART_FONT),
        yaxis=dict(titlefont=AXIS_TITLE_FONT, tickfont=CHART_FONT)
    )

    return fig


def create_sentiment_gauge(average_sentiment: float) -> go.Figure:
    """
    Create a gauge chart for overall sentiment.

    Args:
        average_sentiment: Average sentiment score (0-1)

    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=average_sentiment,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Sentiment"},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.4], 'color': "#FF6B6B"},
                {'range': [0.4, 0.6], 'color': "#FFD93D"},
                {'range': [0.6, 1], 'color': "#6BCB77"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': average_sentiment
            }
        }
    ))

    fig.update_layout(
        template="plotly_white",
        height=300
    )

    return fig


def create_risk_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart for risk severity distribution.

    Args:
        df: DataFrame with severity column

    Returns:
        Plotly figure
    """
    if df.empty or "severity" not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        return fig

    # Filter to only items with risks
    risk_df = df[df["severity"].notna()]

    if risk_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No risks detected",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color='#64748b')
        )
        fig.update_layout(
            template="plotly_white",
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        return fig

    severity_counts = risk_df["severity"].value_counts()

    # Ensure all severity levels are represented (even if count is 0)
    all_severities = ["low", "medium", "high"]
    for severity in all_severities:
        if severity not in severity_counts:
            severity_counts[severity] = 0

    # Sort by severity level (low, medium, high)
    severity_order = ["low", "medium", "high"]
    severity_counts = severity_counts.reindex(severity_order, fill_value=0)

    # Define color mapping
    color_map = {
        "low": "#10b981",
        "medium": "#f59e0b",
        "high": "#ef4444"
    }

    colors = [color_map.get(sev, "#888888") for sev in severity_counts.index]

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[s.capitalize() for s in severity_counts.index],
        values=severity_counts.values,
        marker=dict(colors=colors),
        hole=0.3,  # Donut chart
        textinfo='label+percent+value',
        textfont=dict(size=14, color='#1e293b')
    )])

    fig.update_layout(
        template="plotly_white",
        height=300,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        margin=dict(t=20, b=20, l=20, r=100)
    )

    return fig
