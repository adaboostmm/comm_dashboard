"""
Classifier Agent - Categorizes communications into relevant topics.
Uses few-shot prompting with cached system prompt for efficiency.
"""

import json
from typing import List, Dict, Any
import pandas as pd
import streamlit as st
from agents.base_agent import BaseAgent


class ClassifierAgent(BaseAgent):
    """Agent for classifying communications into categories."""

    # Category definitions
    CATEGORIES = [
        "monetary_policy",
        "banking_regulation",
        "inflation",
        "employment",
        "interest_rates",
        "financial_stability",
        "housing",
        "consumer_protection",
        "payment_systems",
        "other"
    ]

    def __init__(self):
        super().__init__(name="Classifier")

    def get_system_prompt(self) -> str:
        """Get the system prompt for classification."""
        return f"""You are an expert classifier for Federal Reserve communications.

Your task is to categorize communications into one of these categories:
{', '.join(self.CATEGORIES)}

Category Definitions:
- monetary_policy: Federal funds rate, quantitative easing, monetary policy statements
- banking_regulation: Bank supervision, capital requirements, stress tests
- inflation: Price stability, CPI, inflation targets
- employment: Labor market, unemployment, maximum employment mandate
- interest_rates: Rate decisions, rate forecasts, yield curves
- financial_stability: Systemic risk, financial crises, bank failures
- housing: Mortgage rates, housing market, home prices
- consumer_protection: Consumer financial regulations, fair lending
- payment_systems: Payment processing, digital currencies, FedNow
- other: Topics not fitting above categories

Examples:
1. "What is the Fed's plan for raising interest rates?" → interest_rates
2. "How will the SVB failure affect banking regulation?" → financial_stability
3. "What is the current inflation outlook?" → inflation
4. "When will employment return to pre-pandemic levels?" → employment

Respond with ONLY the category name, no explanation."""

    def classify_single(self, text: str) -> str:
        """
        Classify a single text into a category.

        Args:
            text: Text to classify (inquiry subject/body or article headline)

        Returns:
            Category name
        """
        prompt = f"Classify this communication:\n\n{text[:500]}"  # Limit length

        try:
            category = self.call_llm(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for consistent classification
                max_tokens=50,
                cache_system=False
            ).strip().lower()

            # Validate category
            if category not in self.CATEGORIES:
                self.log_activity(f"Invalid category '{category}', defaulting to 'other'")
                return "other"

            return category

        except Exception as e:
            self.handle_error(e, "classifying text")
            return "other"

    def classify_batch(self, texts: List[str], text_ids: List[str] = None) -> Dict[str, str]:
        """
        Classify multiple texts efficiently in a batch.

        Args:
            texts: List of texts to classify
            text_ids: Optional list of IDs for each text

        Returns:
            Dictionary mapping text_id to category
        """
        if not texts:
            return {}

        if text_ids is None:
            text_ids = [f"item_{i}" for i in range(len(texts))]

        # Build batch prompt
        batch_prompt = "Classify each of the following communications. Respond with JSON format: {\"id\": \"category\"}\n\n"

        for text_id, text in zip(text_ids, texts):
            # Truncate long texts
            truncated = text[:300] if len(text) > 300 else text
            batch_prompt += f"ID: {text_id}\nText: {truncated}\n\n"

        batch_prompt += f"\nRespond with ONLY a JSON object mapping each ID to its category from: {', '.join(self.CATEGORIES)}"

        try:
            response = self.call_llm(
                prompt=batch_prompt,
                temperature=0.3,
                max_tokens=1000,
                cache_system=False
            )

            # Parse JSON response
            # Extract JSON from response (handle markdown code blocks)
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            classifications = json.loads(json_str)

            # Validate all categories
            for text_id, category in classifications.items():
                if category not in self.CATEGORIES:
                    classifications[text_id] = "other"

            self.log_activity(f"Classified {len(classifications)} items in batch")
            return classifications

        except json.JSONDecodeError as e:
            self.log_activity(f"Failed to parse batch classification response, falling back to single classification")
            # Fallback: classify one by one
            results = {}
            for text_id, text in zip(text_ids, texts):
                results[text_id] = self.classify_single(text)
            return results
        except Exception as e:
            self.handle_error(e, "batch classifying texts")
            return {text_id: "other" for text_id in text_ids}

    def classify_inquiries(self, inquiries_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add classifications to inquiries DataFrame.

        Args:
            inquiries_df: DataFrame with inquiry data

        Returns:
            DataFrame with added 'category' column
        """
        if inquiries_df.empty:
            return inquiries_df

        # Check if already classified
        if "category" in inquiries_df.columns and inquiries_df["category"].notna().all():
            self.log_activity("Inquiries already classified, skipping")
            return inquiries_df

        # Create classification texts (combine subject and preview of body)
        texts = []
        for _, row in inquiries_df.iterrows():
            subject = str(row.get("subject", ""))
            body = str(row.get("body", ""))[:200]  # First 200 chars
            texts.append(f"{subject}\n{body}")

        # Get IDs
        text_ids = inquiries_df["inquiry_id"].astype(str).tolist()

        # Classify in batch
        with st.spinner("Classifying inquiries..."):
            classifications = self.classify_batch(texts, text_ids)

        # Add to DataFrame
        inquiries_df = inquiries_df.copy()
        inquiries_df["category"] = inquiries_df["inquiry_id"].astype(str).map(classifications)

        # Fill any missing with 'other'
        inquiries_df["category"] = inquiries_df["category"].fillna("other")

        self.log_activity(f"Successfully classified {len(inquiries_df)} inquiries")
        return inquiries_df

    def classify_news(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add classifications to news articles DataFrame.

        Args:
            news_df: DataFrame with news article data

        Returns:
            DataFrame with added 'category' column
        """
        if news_df.empty:
            return news_df

        # Check if already classified
        if "category" in news_df.columns and news_df["category"].notna().all():
            self.log_activity("News articles already classified, skipping")
            return news_df

        # Create classification texts (use headline + first part of content)
        texts = []
        for _, row in news_df.iterrows():
            headline = str(row.get("headline", ""))
            content = str(row.get("content", ""))[:200]
            texts.append(f"{headline}\n{content}")

        # Get IDs
        text_ids = news_df["article_id"].astype(str).tolist()

        # Classify in batch
        with st.spinner("Classifying news articles..."):
            classifications = self.classify_batch(texts, text_ids)

        # Add to DataFrame
        news_df = news_df.copy()
        news_df["category"] = news_df["article_id"].astype(str).map(classifications)

        # Fill any missing with 'other'
        news_df["category"] = news_df["category"].fillna("other")

        self.log_activity(f"Successfully classified {len(news_df)} news articles")
        return news_df
