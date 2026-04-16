"""
Base agent class for all AI agents.
Provides shared functionality for LLM calls, token tracking, and error handling.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import streamlit as st
from services.bedrock_client import BedrockClient, BedrockClientError


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str):
        """
        Initialize the agent.

        Args:
            name: Agent name for identification and logging
        """
        self.name = name
        self.client = self._get_or_create_client()
        self.tokens_used = 0

    @staticmethod
    def _get_or_create_client() -> BedrockClient:
        """Get or create a shared Bedrock client from session state."""
        if "bedrock_client" not in st.session_state:
            st.session_state.bedrock_client = BedrockClient()
        return st.session_state.bedrock_client

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.

        Returns:
            System prompt string
        """
        pass

    def call_llm(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        cache_system: bool = False
    ) -> str:
        """
        Call the LLM with the agent's system prompt.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            cache_system: Whether to cache system prompt

        Returns:
            Generated response text

        Raises:
            BedrockClientError: If LLM call fails
        """
        try:
            system_prompt = self.get_system_prompt()

            # Track tokens before call
            tokens_before = self.client.get_token_usage()

            # Make the LLM call
            response = self.client.simple_completion(
                prompt=prompt,
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                cache_system=cache_system
            )

            # Track tokens used by this call
            tokens_after = self.client.get_token_usage()
            self.tokens_used += (tokens_after - tokens_before)

            return response

        except BedrockClientError as e:
            error_msg = f"{self.name} agent error: {str(e)}"
            st.error(error_msg)
            raise

    def get_token_usage(self) -> int:
        """Get total tokens used by this agent instance."""
        return self.tokens_used

    def reset_token_counter(self):
        """Reset the token usage counter for this agent."""
        self.tokens_used = 0

    @staticmethod
    def handle_error(error: Exception, context: str = "") -> str:
        """
        Handle errors gracefully with user-friendly messages.

        Args:
            error: The exception that occurred
            context: Additional context about what was being attempted

        Returns:
            User-friendly error message
        """
        error_msg = f"An error occurred"
        if context:
            error_msg += f" while {context}"
        error_msg += f": {str(error)}"

        st.error(error_msg)
        return error_msg

    def log_activity(self, message: str):
        """
        Log agent activity.

        Args:
            message: Activity message to log
        """
        if "agent_logs" not in st.session_state:
            st.session_state.agent_logs = []

        log_entry = f"[{self.name}] {message}"
        st.session_state.agent_logs.append(log_entry)

        # Keep only last 100 log entries
        if len(st.session_state.agent_logs) > 100:
            st.session_state.agent_logs = st.session_state.agent_logs[-100:]
