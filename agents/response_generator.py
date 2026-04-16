"""
Response Generator Agent - Generates or matches response templates.
Prioritizes template matching for efficiency, falls back to full generation.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from difflib import SequenceMatcher
import streamlit as st
from agents.base_agent import BaseAgent


class ResponseGenerator(BaseAgent):
    """Agent for generating responses to inquiries."""

    def __init__(self, templates: List[Dict[str, Any]]):
        """
        Initialize response generator with templates.

        Args:
            templates: List of response template dictionaries
        """
        super().__init__(name="ResponseGenerator")
        self.templates = templates

    def get_system_prompt(self) -> str:
        """Get the system prompt for response generation."""
        return """You are a professional communications specialist for a Federal Reserve entity.

Your role is to draft responses to inquiries from media, public, and stakeholders about monetary policy, banking, and economic topics.

Guidelines:
1. Be professional, clear, and concise
2. Use neutral, objective language
3. Avoid speculation or commitments
4. Reference official Fed statements when appropriate
5. Be respectful and helpful
6. Keep responses under 300 words unless more detail is needed

Tone should match the inquiry source:
- Media: Professional, quotable, official
- Public: Accessible, educational, friendly
- Stakeholders: Detailed, technical when appropriate

Draft a complete response that can be sent with minimal editing."""

    def find_best_template(self, inquiry: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Find the best matching template for an inquiry.

        Args:
            inquiry: Inquiry dictionary with subject, body, category

        Returns:
            Tuple of (best_template, similarity_score) or (None, 0.0)
        """
        if not self.templates:
            return None, 0.0

        inquiry_text = f"{inquiry.get('subject', '')} {inquiry.get('body', '')}".lower()
        inquiry_category = inquiry.get('category', '').lower()

        best_template = None
        best_score = 0.0

        for template in self.templates:
            # Check category match first
            template_category = template.get('category', '').lower()
            if template_category and inquiry_category:
                if template_category != inquiry_category:
                    continue  # Skip templates from different categories

            # Calculate text similarity
            template_text = f"{template.get('subject', '')} {template.get('description', '')}".lower()
            similarity = SequenceMatcher(None, inquiry_text[:500], template_text[:500]).ratio()

            # Boost score if keywords match
            template_keywords = set(template.get('keywords', []))
            inquiry_keywords = set(inquiry_text.split())
            keyword_overlap = len(template_keywords & inquiry_keywords) / max(len(template_keywords), 1)
            similarity += keyword_overlap * 0.2  # Boost by keyword matches

            if similarity > best_score:
                best_score = similarity
                best_template = template

        # Only return template if similarity is above threshold
        if best_score >= 0.3:  # 30% similarity threshold
            return best_template, best_score
        return None, 0.0

    def fill_template(self, template: Dict[str, Any], inquiry: Dict[str, Any]) -> str:
        """
        Fill template placeholders with inquiry-specific information.

        Args:
            template: Template dictionary
            inquiry: Inquiry dictionary

        Returns:
            Filled response text
        """
        response_text = template.get('response_body', '')

        # Define placeholder mappings
        placeholders = {
            '{{sender_name}}': inquiry.get('sender_name', '[Name]'),
            '{{sender_organization}}': inquiry.get('sender_organization', '[Organization]'),
            '{{subject}}': inquiry.get('subject', '[Subject]'),
            '{{date}}': inquiry.get('date_received', '[Date]'),
            '{{inquiry_id}}': inquiry.get('inquiry_id', '[ID]')
        }

        # Replace all placeholders
        for placeholder, value in placeholders.items():
            if placeholder in response_text:
                response_text = response_text.replace(placeholder, str(value))

        return response_text

    def generate_full_response(self, inquiry: Dict[str, Any]) -> str:
        """
        Generate a completely new response using LLM.

        Args:
            inquiry: Inquiry dictionary

        Returns:
            Generated response text
        """
        prompt = f"""Generate a response to this inquiry:

From: {inquiry.get('sender_name', 'Unknown')} ({inquiry.get('sender_organization', 'Unknown')})
Source: {inquiry.get('source', 'Unknown')}
Category: {inquiry.get('category', 'Unknown')}

Subject: {inquiry.get('subject', 'No subject')}

Body:
{inquiry.get('body', 'No body provided')}

Generate an appropriate response following the guidelines."""

        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                cache_system=False
            )

            self.log_activity(f"Generated full response for inquiry {inquiry.get('inquiry_id', 'unknown')}")
            return response

        except Exception as e:
            self.handle_error(e, "generating response")
            return "Error generating response. Please try again."

    def generate_response(
        self,
        inquiry: Dict[str, Any],
        force_generate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response to an inquiry, using template matching first.

        Args:
            inquiry: Inquiry dictionary
            force_generate: If True, skip template matching and generate new

        Returns:
            Dictionary with 'response', 'method', 'template_match_score'
        """
        result = {
            'response': '',
            'method': 'generated',
            'template_match_score': 0.0
        }

        # Try template matching first (unless forced to generate)
        if not force_generate:
            template, score = self.find_best_template(inquiry)

            if template:
                # Use template
                response = self.fill_template(template, inquiry)
                result['response'] = response
                result['method'] = 'template'
                result['template_match_score'] = score
                self.log_activity(f"Matched template for inquiry {inquiry.get('inquiry_id', 'unknown')} (score: {score:.2f})")
                return result

        # Fallback to full generation
        response = self.generate_full_response(inquiry)
        result['response'] = response
        result['method'] = 'generated'

        return result

    def refine_response(self, original_response: str, feedback: str) -> str:
        """
        Refine a response based on user feedback.

        Args:
            original_response: Original response text
            feedback: User feedback for refinement

        Returns:
            Refined response text
        """
        prompt = f"""Refine this response based on the feedback provided.

Original Response:
{original_response}

Feedback:
{feedback}

Provide the refined response that incorporates the feedback."""

        try:
            refined = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                cache_system=False
            )

            self.log_activity("Refined response based on feedback")
            return refined

        except Exception as e:
            self.handle_error(e, "refining response")
            return original_response  # Return original if refinement fails
