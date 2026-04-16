"""
Insights Generator Agent - Generates dashboard summary insights.
Cached for 5 minutes to minimize token usage.
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from agents.base_agent import BaseAgent


class InsightsAgent(BaseAgent):
    """Agent for generating dashboard insights."""

    def __init__(self):
        super().__init__(name="Insights")
        self.cache_duration = timedelta(minutes=5)
        self.last_generation_time = None
        self.cached_insights = None

    def get_system_prompt(self) -> str:
        """Get the system prompt for insights generation."""
        return """You are a data analyst for a Federal Reserve communications team.

Your role is to generate concise, actionable insights from communication data including:
- Inquiries from media, public, and stakeholders
- News articles about Federal Reserve and monetary policy
- Social media posts

Guidelines for insights:
1. Focus on trends, patterns, and anomalies
2. Highlight urgent or high-priority items
3. Be specific with numbers and percentages
4. Identify potential risks or concerns
5. Keep total response to 3-4 bullet points
6. Use clear, executive-level language

Format your response as bullet points, each starting with "•"."""

    def _prepare_data_summary(self, data: Dict[str, Any]) -> str:
        """
        Prepare a text summary of the data for the LLM.

        Args:
            data: Dictionary with inquiries, news, social_media DataFrames

        Returns:
            Formatted text summary
        """
        summary_parts = []

        # Inquiries summary
        inquiries_df = data.get("inquiries", pd.DataFrame())
        if not inquiries_df.empty:
            total_inquiries = len(inquiries_df)

            # Category distribution
            if "category" in inquiries_df.columns:
                category_counts = inquiries_df["category"].value_counts().head(3)
                top_categories = ", ".join([f"{cat} ({count})" for cat, count in category_counts.items()])
            else:
                top_categories = "Not categorized"

            # Priority distribution
            if "priority" in inquiries_df.columns:
                priority_counts = inquiries_df["priority"].value_counts()
                priority_summary = ", ".join([f"{pri} ({count})" for pri, count in priority_counts.items()])
            else:
                priority_summary = "Not available"

            # Source distribution
            if "source" in inquiries_df.columns:
                source_counts = inquiries_df["source"].value_counts()
                source_summary = ", ".join([f"{src} ({count})" for src, count in source_counts.items()])
            else:
                source_summary = "Not available"

            summary_parts.append(f"""INQUIRIES ({total_inquiries} total):
- Top categories: {top_categories}
- By priority: {priority_summary}
- By source: {source_summary}""")

        # News summary
        news_df = data.get("news", pd.DataFrame())
        if not news_df.empty:
            total_news = len(news_df)

            # Sentiment analysis
            if "sentiment_score" in news_df.columns:
                avg_sentiment = news_df["sentiment_score"].mean()
                negative_news = len(news_df[news_df["sentiment_score"] < 0.4])
                positive_news = len(news_df[news_df["sentiment_score"] > 0.6])
                sentiment_summary = f"Avg: {avg_sentiment:.2f}, Negative: {negative_news}, Positive: {positive_news}"
            else:
                sentiment_summary = "Not available"

            # Risk flags
            if "risk_flag" in news_df.columns:
                risk_count = news_df["risk_flag"].sum() if news_df["risk_flag"].dtype == bool else 0
            else:
                risk_count = 0

            summary_parts.append(f"""NEWS ARTICLES ({total_news} total):
- Sentiment: {sentiment_summary}
- Risk flags: {risk_count}""")

        # Social media summary
        social_df = data.get("social_media", pd.DataFrame())
        if not social_df.empty:
            total_posts = len(social_df)

            # Sentiment
            if "sentiment_score" in social_df.columns:
                avg_sentiment = social_df["sentiment_score"].mean()
                sentiment_trend = "Positive" if avg_sentiment > 0.6 else "Negative" if avg_sentiment < 0.4 else "Neutral"
            else:
                sentiment_trend = "Not available"

            # Platform distribution
            if "platform" in social_df.columns:
                platform_counts = social_df["platform"].value_counts()
                platform_summary = ", ".join([f"{plat} ({count})" for plat, count in platform_counts.items()])
            else:
                platform_summary = "Not available"

            summary_parts.append(f"""SOCIAL MEDIA ({total_posts} total):
- Sentiment trend: {sentiment_trend}
- By platform: {platform_summary}""")

        return "\n\n".join(summary_parts)

    def generate_insights(self, data: Dict[str, Any], force_refresh: bool = False) -> str:
        """
        Generate dashboard insights from data.

        Args:
            data: Dictionary with inquiries, news, social_media DataFrames
            force_refresh: If True, bypass cache and generate new insights

        Returns:
            Generated insights as formatted text
        """
        # Check cache
        if not force_refresh and self.cached_insights and self.last_generation_time:
            time_since_generation = datetime.now() - self.last_generation_time
            if time_since_generation < self.cache_duration:
                self.log_activity("Returning cached insights")
                return self.cached_insights

        # Generate new insights
        data_summary = self._prepare_data_summary(data)

        prompt = f"""Analyze this communications data and provide 3-4 key insights:

{data_summary}

Focus on:
1. Emerging trends or patterns
2. High-priority or urgent items
3. Potential risks or concerns
4. Notable changes or anomalies

Provide concise, actionable insights as bullet points."""

        try:
            with st.spinner("Generating insights..."):
                insights = self.call_llm(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=400,
                    cache_system=False
                )

            # Cache the results
            self.cached_insights = insights
            self.last_generation_time = datetime.now()

            self.log_activity("Generated new dashboard insights")
            return insights

        except Exception as e:
            self.handle_error(e, "generating insights")
            return "• Unable to generate insights at this time. Please try again."

    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get information about cache status.

        Returns:
            Dictionary with cache status information
        """
        if not self.last_generation_time:
            return {
                "cached": False,
                "age_seconds": None,
                "expires_in_seconds": None
            }

        age = datetime.now() - self.last_generation_time
        age_seconds = age.total_seconds()
        expires_in = self.cache_duration.total_seconds() - age_seconds

        return {
            "cached": expires_in > 0,
            "age_seconds": age_seconds,
            "expires_in_seconds": max(0, expires_in)
        }

    def clear_cache(self):
        """Clear the insights cache."""
        self.cached_insights = None
        self.last_generation_time = None
        self.log_activity("Insights cache cleared")
