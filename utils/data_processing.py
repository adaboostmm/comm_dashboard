"""
Data processing utilities for filtering, searching, and transforming data.
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


def filter_dataframe(
    df: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply multiple filters to a DataFrame.

    Args:
        df: DataFrame to filter
        filters: Dictionary of column:value pairs to filter on

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    filtered_df = df.copy()

    for column, value in filters.items():
        if column in filtered_df.columns and value is not None:
            if isinstance(value, list):
                # Multiple values (OR filter)
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                # Single value
                filtered_df = filtered_df[filtered_df[column] == value]

    return filtered_df


def search_dataframe(
    df: pd.DataFrame,
    search_term: str,
    search_columns: List[str]
) -> pd.DataFrame:
    """
    Search for a term across multiple columns.

    Args:
        df: DataFrame to search
        search_term: Search term
        search_columns: List of column names to search in

    Returns:
        Filtered DataFrame with matching rows
    """
    if df.empty or not search_term:
        return df

    # Convert search term to lowercase for case-insensitive search
    search_term = search_term.lower()

    # Create a mask for rows that match in any column
    mask = pd.Series([False] * len(df))

    for column in search_columns:
        if column in df.columns:
            # Convert column to string and search
            mask |= df[column].astype(str).str.lower().str.contains(search_term, na=False)

    return df[mask]


def paginate_dataframe(
    df: pd.DataFrame,
    page: int,
    page_size: int
) -> pd.DataFrame:
    """
    Paginate a DataFrame.

    Args:
        df: DataFrame to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated DataFrame
    """
    if df.empty:
        return df

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return df.iloc[start_idx:end_idx]


def sort_dataframe(
    df: pd.DataFrame,
    sort_column: str,
    ascending: bool = True
) -> pd.DataFrame:
    """
    Sort a DataFrame by a column.

    Args:
        df: DataFrame to sort
        sort_column: Column name to sort by
        ascending: Sort order

    Returns:
        Sorted DataFrame
    """
    if df.empty or sort_column not in df.columns:
        return df

    return df.sort_values(by=sort_column, ascending=ascending)


def get_sentiment_label(sentiment_score: float) -> str:
    """
    Convert sentiment score to label.

    Args:
        sentiment_score: Sentiment score (0-1)

    Returns:
        Sentiment label (Positive/Neutral/Negative)
    """
    if pd.isna(sentiment_score):
        return "Unknown"
    elif sentiment_score >= 0.6:
        return "Positive"
    elif sentiment_score >= 0.4:
        return "Neutral"
    else:
        return "Negative"


def get_sentiment_color(sentiment_score: float) -> str:
    """
    Get color for sentiment score.

    Args:
        sentiment_score: Sentiment score (0-1)

    Returns:
        Color name or hex code
    """
    if pd.isna(sentiment_score):
        return "gray"
    elif sentiment_score >= 0.6:
        return "green"
    elif sentiment_score >= 0.4:
        return "orange"
    else:
        return "red"


def get_priority_color(priority: str) -> str:
    """
    Get color for priority level.

    Args:
        priority: Priority level (high/medium/low)

    Returns:
        Color name or hex code
    """
    priority_map = {
        "high": "red",
        "medium": "orange",
        "low": "green"
    }
    return priority_map.get(str(priority).lower(), "gray")


def get_severity_color(severity: str) -> str:
    """
    Get color for risk severity.

    Args:
        severity: Severity level (high/medium/low)

    Returns:
        Color name or hex code
    """
    severity_map = {
        "high": "#FF6B6B",
        "medium": "#FFD93D",
        "low": "#6BCB77"
    }
    return severity_map.get(str(severity).lower(), "#888888")


def format_date(date) -> str:
    """
    Format date for display.

    Args:
        date: Date object or string

    Returns:
        Formatted date string
    """
    if pd.isna(date):
        return "Unknown"

    try:
        if isinstance(date, str):
            date = pd.to_datetime(date)
        return date.strftime("%Y-%m-%d %H:%M")
    except:
        return str(date)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or pd.isna(text):
        return ""

    text = str(text)
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def filter_by_date_range(data: Dict[str, pd.DataFrame], start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
    """
    Filter all data sources by date range.

    Args:
        data: Dictionary with DataFrames (inquiries, news, social_media)
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        Filtered data dictionary
    """
    filtered_data = {}

    # Convert datetime objects to timezone-aware if needed
    # Make end_date inclusive of the full day (23:59:59)
    if start_date.tzinfo is None:
        start_date = pd.Timestamp(start_date).tz_localize('UTC')
    else:
        start_date = pd.Timestamp(start_date).tz_convert('UTC')

    if end_date.tzinfo is None:
        # Add 1 day minus 1 second to make it inclusive of the end date
        end_date = pd.Timestamp(end_date + timedelta(days=1) - timedelta(seconds=1)).tz_localize('UTC')
    else:
        end_date = pd.Timestamp(end_date + timedelta(days=1) - timedelta(seconds=1)).tz_convert('UTC')

    # Filter inquiries
    inquiries_df = data.get("inquiries", pd.DataFrame())
    if not inquiries_df.empty and "date_received" in inquiries_df.columns:
        inquiries_df = inquiries_df.copy()
        inquiries_df["date_received"] = pd.to_datetime(inquiries_df["date_received"], errors='coerce', utc=True)
        # Drop rows with invalid dates
        inquiries_df = inquiries_df[inquiries_df["date_received"].notna()]
        mask = (inquiries_df["date_received"] >= start_date) & (inquiries_df["date_received"] <= end_date)
        filtered_data["inquiries"] = inquiries_df[mask]
    else:
        filtered_data["inquiries"] = inquiries_df

    # Filter news
    news_df = data.get("news", pd.DataFrame())
    if not news_df.empty and "published_date" in news_df.columns:
        news_df = news_df.copy()
        news_df["published_date"] = pd.to_datetime(news_df["published_date"], errors='coerce', utc=True)
        news_df = news_df[news_df["published_date"].notna()]
        mask = (news_df["published_date"] >= start_date) & (news_df["published_date"] <= end_date)
        filtered_data["news"] = news_df[mask]
    else:
        filtered_data["news"] = news_df

    # Filter social media
    social_df = data.get("social_media", pd.DataFrame())
    if not social_df.empty and "timestamp" in social_df.columns:
        social_df = social_df.copy()
        social_df["timestamp"] = pd.to_datetime(social_df["timestamp"], errors='coerce', utc=True)
        social_df = social_df[social_df["timestamp"].notna()]
        mask = (social_df["timestamp"] >= start_date) & (social_df["timestamp"] <= end_date)
        filtered_data["social_media"] = social_df[mask]
    else:
        filtered_data["social_media"] = social_df

    # Pass through templates unchanged
    filtered_data["templates"] = data.get("templates", [])

    return filtered_data


def get_date_ranges(data: Dict[str, pd.DataFrame] = None) -> List[Dict[str, Any]]:
    """
    Generate list of 7-day date ranges in descending order.
    Only returns ranges for the 6-month synthetic data period (June-Nov 2024).

    Args:
        data: Dictionary with DataFrames to determine date range from actual data

    Returns:
        List of date range dictionaries with label, start_date, end_date
    """
    ranges = []

    # Use fixed 6-month period: June 1 - Nov 30, 2024 (26 weeks)
    base_start = datetime(2024, 6, 1)
    num_weeks = 26

    # Generate 26 seven-day periods
    for week_num in range(num_weeks):
        period_start = base_start + timedelta(weeks=week_num)
        period_end = period_start + timedelta(days=6)

        label = f"{period_start.strftime('%b %d')} - {period_end.strftime('%b %d, %Y')}"

        ranges.append({
            "label": label,
            "start_date": period_start,
            "end_date": period_end
        })

    # Reverse to show most recent first
    ranges.reverse()

    return ranges


def calculate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics for a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {
            "total_count": 0,
            "avg_sentiment": None,
            "risk_count": 0,
            "high_priority_count": 0
        }

    stats = {
        "total_count": len(df)
    }

    # Average sentiment
    if "sentiment_score" in df.columns:
        stats["avg_sentiment"] = df["sentiment_score"].mean()

    # Risk count
    if "risk_flag" in df.columns:
        stats["risk_count"] = df["risk_flag"].sum() if df["risk_flag"].dtype == bool else 0

    # High priority count
    if "priority" in df.columns:
        stats["high_priority_count"] = len(df[df["priority"].str.lower() == "high"])

    return stats
