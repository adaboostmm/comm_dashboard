"""
Caching utilities for optimizing performance and token usage.
"""

import streamlit as st
from functools import wraps
from datetime import datetime, timedelta
from typing import Any, Callable, Optional


def cache_with_ttl(ttl_seconds: int):
    """
    Decorator to cache function results with a time-to-live.

    Args:
        ttl_seconds: Time to live in seconds

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache_key = f"cache_{func.__name__}"
        timestamp_key = f"cache_timestamp_{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if cached result exists and is still valid
            if cache_key in st.session_state and timestamp_key in st.session_state:
                cache_age = datetime.now() - st.session_state[timestamp_key]
                if cache_age.total_seconds() < ttl_seconds:
                    return st.session_state[cache_key]

            # Call function and cache result
            result = func(*args, **kwargs)
            st.session_state[cache_key] = result
            st.session_state[timestamp_key] = datetime.now()
            return result

        return wrapper
    return decorator


def clear_cache(func_name: Optional[str] = None):
    """
    Clear cached results.

    Args:
        func_name: Optional function name to clear specific cache.
                  If None, clears all caches.
    """
    if func_name:
        cache_key = f"cache_{func_name}"
        timestamp_key = f"cache_timestamp_{func_name}"

        if cache_key in st.session_state:
            del st.session_state[cache_key]
        if timestamp_key in st.session_state:
            del st.session_state[timestamp_key]
    else:
        # Clear all cache keys
        keys_to_delete = [
            key for key in st.session_state.keys()
            if key.startswith("cache_")
        ]
        for key in keys_to_delete:
            del st.session_state[key]


def get_cache_info(func_name: str) -> dict:
    """
    Get information about a cached function.

    Args:
        func_name: Function name

    Returns:
        Dictionary with cache info (exists, age_seconds)
    """
    cache_key = f"cache_{func_name}"
    timestamp_key = f"cache_timestamp_{func_name}"

    if cache_key not in st.session_state or timestamp_key not in st.session_state:
        return {"exists": False, "age_seconds": None}

    cache_age = datetime.now() - st.session_state[timestamp_key]
    return {
        "exists": True,
        "age_seconds": cache_age.total_seconds()
    }


def session_cache(key: str, value: Any = None) -> Any:
    """
    Simple key-value caching in session state.

    Args:
        key: Cache key
        value: Value to cache (if None, retrieves cached value)

    Returns:
        Cached value or None
    """
    if value is not None:
        st.session_state[key] = value
        return value
    else:
        return st.session_state.get(key)


def has_cache(key: str) -> bool:
    """
    Check if a key exists in cache.

    Args:
        key: Cache key

    Returns:
        True if key exists in cache
    """
    return key in st.session_state
