"""
Inquiry Queue Component - Manage and respond to inquiries.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from utils.data_processing import (
    filter_dataframe,
    search_dataframe,
    paginate_dataframe,
    sort_dataframe,
    get_priority_color,
    get_sentiment_color,
    format_date,
    truncate_text
)
from agents.response_generator import ResponseGenerator
from config import Config


def render_inquiry_queue(data: Dict[str, Any]):
    """
    Render the inquiry queue page.

    Args:
        data: Dictionary with inquiries DataFrame and templates
    """
    # Title is now shown in main app.py

    inquiries_df = data.get("inquiries", pd.DataFrame())
    templates = data.get("templates", [])

    if inquiries_df.empty:
        st.warning("No inquiries available")
        return

    # Initialize response generator
    if "response_generator" not in st.session_state:
        st.session_state.response_generator = ResponseGenerator(templates)

    # Filters and search
    filters = render_filters(inquiries_df)

    # Apply filters
    filtered_df = apply_filters(inquiries_df, filters)

    # Display summary
    st.write(f"Showing {len(filtered_df)} of {len(inquiries_df)} inquiries")

    # Pagination
    page_size = Config.PAGE_SIZE
    total_pages = max(1, (len(filtered_df) + page_size - 1) // page_size)

    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=1,
            key="inquiry_page"
        )
    with col2:
        st.write(f"Page {page} of {total_pages}")

    # Get paginated data
    paginated_df = paginate_dataframe(filtered_df, page, page_size)

    # Display inquiries
    for idx, row in paginated_df.iterrows():
        render_inquiry_card(row, data, page, idx)


def render_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Render filter controls.

    Args:
        df: Inquiries DataFrame

    Returns:
        Dictionary with filter values
    """
    st.subheader("Filters & Search")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Source filter
        sources = ["All"] + sorted(df["source"].dropna().unique().tolist())
        source_filter = st.selectbox("Source", sources, key="source_filter")

    with col2:
        # Priority filter
        priorities = ["All"] + sorted(df["priority"].dropna().unique().tolist())
        priority_filter = st.selectbox("Priority", priorities, key="priority_filter")

    with col3:
        # Status filter
        if "status" in df.columns:
            statuses = ["All"] + sorted(df["status"].dropna().unique().tolist())
            status_filter = st.selectbox("Status", statuses, key="status_filter")
        else:
            status_filter = "All"

    with col4:
        # Category filter
        if "category" in df.columns:
            categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
            category_filter = st.selectbox("Category", categories, key="category_filter")
        else:
            category_filter = "All"

    # Search box
    search_term = st.text_input(
        "🔍 Search inquiries",
        placeholder="Search by sender, subject, or content...",
        key="inquiry_search"
    )

    return {
        "source": None if source_filter == "All" else source_filter,
        "priority": None if priority_filter == "All" else priority_filter,
        "status": None if status_filter == "All" else status_filter,
        "category": None if category_filter == "All" else category_filter,
        "search": search_term
    }


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to DataFrame.

    Args:
        df: Inquiries DataFrame
        filters: Filter dictionary

    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()

    # Apply column filters
    filter_dict = {
        "source": filters.get("source"),
        "priority": filters.get("priority"),
        "status": filters.get("status"),
        "category": filters.get("category")
    }

    filtered_df = filter_dataframe(filtered_df, filter_dict)

    # Apply search
    search_term = filters.get("search", "")
    if search_term:
        search_columns = ["sender_name", "sender_organization", "subject", "body"]
        filtered_df = search_dataframe(filtered_df, search_term, search_columns)

    # Sort by date (most recent first) and priority
    if "date_received" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("date_received", ascending=False)

    return filtered_df


def render_inquiry_card(row: pd.Series, data: Dict[str, Any], page: int = 1, idx: int = 0):
    """
    Render a single inquiry card.

    Args:
        row: Inquiry row from DataFrame
        data: Full data dictionary
        page: Current page number for unique keys
        idx: Row index for additional uniqueness
    """
    inquiry_id = row["inquiry_id"]
    # Create unique key prefix with page number and index
    unique_prefix = f"p{page}_idx{idx}_{inquiry_id}"

    # Create expander for inquiry
    priority_emoji = "🔴" if row.get("priority", "").lower() == "high" else "🟡" if row.get("priority", "").lower() == "medium" else "🟢"
    risk_emoji = "⚠️ " if row.get("risk_flag", False) else ""

    header = f"{risk_emoji}{priority_emoji} {row.get('sender_name', 'Unknown')} - {truncate_text(row.get('subject', 'No subject'), 60)}"

    with st.expander(header, expanded=False):
        # Inquiry details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**From:** {row.get('sender_name', 'Unknown')} ({row.get('sender_organization', 'Unknown')})")
            st.markdown(f"**Subject:** {row.get('subject', 'No subject')}")
            st.markdown(f"**Date:** {format_date(row.get('date_received'))}")

        with col2:
            # Badges
            priority = row.get('priority', 'unknown')
            st.markdown(f"**Priority:** :{get_priority_color(priority)}[{priority.upper()}]")

            if "category" in row and pd.notna(row["category"]):
                st.markdown(f"**Category:** {row['category'].replace('_', ' ').title()}")

            if "status" in row and pd.notna(row["status"]):
                st.markdown(f"**Status:** {row['status']}")

        # Risk warning
        if row.get("risk_flag", False):
            st.warning(f"⚠️ **Risk Detected:** {row.get('risk_description', 'Potential communication risk identified')}")
            if "severity" in row and pd.notna(row["severity"]):
                st.markdown(f"**Severity:** {row['severity'].upper()}")

        st.markdown("---")

        # Inquiry body
        st.markdown("**Inquiry Content:**")
        st.text_area(
            "",
            value=row.get('body', 'No content available'),
            height=150,
            disabled=True,
            key=f"body_{unique_prefix}"
        )

        st.markdown("---")

        # Response generation section
        st.markdown("**Response:**")

        # Check if response already generated
        response_key = f"response_{unique_prefix}"
        if response_key not in st.session_state:
            st.session_state[response_key] = None

        col_gen, col_edit = st.columns([1, 3])

        with col_gen:
            if st.button("✍️ Generate Response", key=f"gen_{unique_prefix}"):
                generate_response(row, response_key)

        # Show generated response
        if st.session_state[response_key]:
            response_data = st.session_state[response_key]

            # Show method used
            method = response_data.get("method", "unknown")
            if method == "template":
                score = response_data.get("template_match_score", 0)
                st.info(f"📋 Response generated using template (match score: {score:.2%})")
            else:
                st.info("🤖 Response generated using AI")

            # Editable response
            edited_response = st.text_area(
                "Response text (editable)",
                value=response_data.get("response", ""),
                height=200,
                key=f"edit_{unique_prefix}"
            )

            # Action buttons
            col_copy, col_refine, col_clear = st.columns(3)

            with col_copy:
                if st.button("📋 Copy", key=f"copy_{unique_prefix}"):
                    st.success("Response copied to clipboard!")

            with col_refine:
                if st.button("✨ Refine", key=f"refine_{unique_prefix}"):
                    refine_response(inquiry_id, edited_response)

            with col_clear:
                if st.button("🗑️ Clear", key=f"clear_{unique_prefix}"):
                    st.session_state[response_key] = None
                    st.experimental_rerun()


def generate_response(inquiry_row: pd.Series, response_key: str):
    """
    Generate a response for an inquiry.

    Args:
        inquiry_row: Inquiry data
        response_key: Session state key for storing response
    """
    # Convert row to dict
    inquiry_dict = inquiry_row.to_dict()

    # Get response generator
    generator = st.session_state.response_generator

    with st.spinner("Generating response..."):
        try:
            result = generator.generate_response(inquiry_dict)
            st.session_state[response_key] = result
            st.success("Response generated!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to generate response: {str(e)}")


def refine_response(inquiry_id: str, current_response: str):
    """
    Refine a response based on user feedback.

    Args:
        inquiry_id: Inquiry ID
        current_response: Current response text
    """
    # Get feedback from user
    feedback = st.text_input(
        "Enter refinement instructions:",
        key=f"feedback_{inquiry_id}",
        placeholder="E.g., 'Make it more formal' or 'Add technical details'"
    )

    if feedback:
        generator = st.session_state.response_generator
        with st.spinner("Refining response..."):
            try:
                refined = generator.refine_response(current_response, feedback)
                response_key = f"response_{inquiry_id}"
                if response_key in st.session_state:
                    st.session_state[response_key]["response"] = refined
                    st.success("Response refined!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to refine response: {str(e)}")
