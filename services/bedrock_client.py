"""
AWS Bedrock API client for Claude Sonnet 4.5.
Handles API communication with retry logic and error handling.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import Config


class BedrockClientError(Exception):
    """Custom exception for Bedrock client errors."""
    pass


class BedrockClient:
    """Client for interacting with AWS Bedrock Claude API."""

    def __init__(self):
        self.api_key = Config.API_KEY
        self.api_endpoint = Config.API_ENDPOINT
        self.model_name = Config.MODEL_NAME
        self.total_tokens_used = 0

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, BedrockClientError))
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        cache_system_prompt: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the Bedrock API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            cache_system_prompt: Whether to cache the system prompt

        Returns:
            Dict containing the response and metadata

        Raises:
            BedrockClientError: If the API request fails
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if system:
            payload["system"] = system

        # Add caching hint if requested
        if cache_system_prompt and system:
            payload["system"] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"}
                }
            ]

        try:
            response = requests.post(
                self.api_endpoint,
                headers=self._build_headers(),
                json=payload,
                timeout=30
            )

            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                raise BedrockClientError(error_msg)

            result = response.json()

            # Track token usage
            if "usage" in result:
                tokens = result["usage"].get("total_tokens", 0)
                self.total_tokens_used += tokens

            return result

        except requests.exceptions.Timeout:
            raise BedrockClientError("API request timed out")
        except requests.exceptions.RequestException as e:
            raise BedrockClientError(f"API request failed: {str(e)}")
        except ValueError as e:
            raise BedrockClientError(f"Failed to parse API response: {str(e)}")

    def extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract text content from API response.

        Args:
            response: API response dict

        Returns:
            Extracted text content
        """
        try:
            # Handle different response formats
            if "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                return message.get("content", "")
            elif "content" in response:
                if isinstance(response["content"], list):
                    # Handle content blocks
                    return " ".join([block.get("text", "") for block in response["content"]])
                return response["content"]
            else:
                return str(response)
        except (KeyError, IndexError) as e:
            raise BedrockClientError(f"Unexpected response format: {str(e)}")

    def simple_completion(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        cache_system: bool = False
    ) -> str:
        """
        Simple completion interface for single-turn interactions.

        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            cache_system: Whether to cache system prompt

        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]

        response = self.chat_completion(
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            cache_system_prompt=False
        )

        return self.extract_text_from_response(response)

    def batch_completion(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> List[str]:
        """
        Process multiple prompts efficiently by batching them into a single request.

        Args:
            prompts: List of user prompts
            system: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            List of generated responses
        """
        # Create a combined prompt for batch processing
        batch_prompt = "Process the following requests:\n\n"
        for i, prompt in enumerate(prompts, 1):
            batch_prompt += f"Request {i}:\n{prompt}\n\n"
        batch_prompt += "Respond to each request in order, labeling your responses as 'Response 1:', 'Response 2:', etc."

        response_text = self.simple_completion(
            prompt=batch_prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            cache_system=False
        )

        # Parse batch response
        responses = []
        lines = response_text.split("\n")
        current_response = []

        for line in lines:
            if line.startswith("Response ") and ":" in line:
                if current_response:
                    responses.append("\n".join(current_response).strip())
                    current_response = []
                # Start collecting new response (skip the header line)
                continue
            else:
                current_response.append(line)

        # Add the last response
        if current_response:
            responses.append("\n".join(current_response).strip())

        return responses[:len(prompts)]  # Ensure we return the right number

    def get_token_usage(self) -> int:
        """Get total tokens used by this client instance."""
        return self.total_tokens_used

    def reset_token_counter(self):
        """Reset the token usage counter."""
        self.total_tokens_used = 0
