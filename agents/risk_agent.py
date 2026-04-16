"""
Risk Detector Agent - Identifies communication risks in news and inquiries.
Outputs risk flags, descriptions, and severity levels.
"""

import json
from typing import Dict, List, Any
import pandas as pd
import streamlit as st
from agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Agent for detecting communication risks."""

    SEVERITY_LEVELS = ["low", "medium", "high"]

    def __init__(self):
        super().__init__(name="RiskDetector")

    def get_system_prompt(self) -> str:
        """Get the system prompt for risk detection."""
        return """You are a risk analyst for Federal Reserve communications.

Your role is to identify potential communication risks in news articles, social media posts, and inquiries.

Risk Types to Identify:
1. Misinformation or factual errors about Fed policy
2. Crisis situations (bank failures, market crashes)
3. Controversial or politically sensitive topics
4. Criticism of Fed actions or officials
5. Urgent media requests requiring immediate response
6. Legal or regulatory concerns
7. Reputational risks to the Federal Reserve
8. Security or confidentiality issues

For each item, assess:
- risk_flag: true/false (is there a risk?)
- risk_description: Brief description of the risk
- severity: low/medium/high

Severity Guidelines:
- HIGH: Urgent response needed, major reputational risk, crisis situation
- MEDIUM: Important to address, moderate concern, potential for escalation
- LOW: Minor concern, routine monitoring, low urgency

Respond with JSON format."""

    def detect_risk_single(self, text: str, item_id: str) -> Dict[str, Any]:
        """
        Detect risk in a single text.

        Args:
            text: Text to analyze
            item_id: Identifier for the item

        Returns:
            Dictionary with risk_flag, risk_description, severity
        """
        prompt = f"""Analyze this communication for risks:

ID: {item_id}
Text: {text[:800]}

Respond with JSON:
{{
    "risk_flag": true/false,
    "risk_description": "description or null",
    "severity": "low/medium/high or null"
}}"""

        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.3,
                max_tokens=200,
                cache_system=False
            )

            # Parse JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            result = json.loads(json_str)

            # Validate severity
            if result.get("severity") not in self.SEVERITY_LEVELS:
                result["severity"] = None

            return result

        except Exception as e:
            self.handle_error(e, f"detecting risk for item {item_id}")
            return {
                "risk_flag": False,
                "risk_description": None,
                "severity": None
            }

    def detect_risks_batch(
        self,
        texts: List[str],
        item_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Detect risks in multiple texts efficiently.

        Args:
            texts: List of texts to analyze
            item_ids: List of IDs for each text

        Returns:
            Dictionary mapping item_id to risk assessment
        """
        if not texts:
            return {}

        # Process in batches of 10
        batch_size = 10
        all_results = {}

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_ids = item_ids[i:i + batch_size]

            # Build batch prompt
            batch_prompt = "Analyze each communication for risks. Respond with JSON object mapping ID to risk assessment.\n\n"

            for item_id, text in zip(batch_ids, batch_texts):
                truncated = text[:500]
                batch_prompt += f"ID: {item_id}\nText: {truncated}\n\n"

            batch_prompt += """\nRespond with JSON:
{
    "item_id": {
        "risk_flag": true/false,
        "risk_description": "description or null",
        "severity": "low/medium/high or null"
    },
    ...
}"""

            try:
                response = self.call_llm(
                    prompt=batch_prompt,
                    temperature=0.3,
                    max_tokens=1000,
                    cache_system=False
                )

                # Parse JSON
                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()

                batch_results = json.loads(json_str)

                # Validate and merge results
                for item_id, risk_data in batch_results.items():
                    if risk_data.get("severity") not in self.SEVERITY_LEVELS and risk_data.get("risk_flag"):
                        risk_data["severity"] = "medium"  # Default severity
                    all_results[item_id] = risk_data

            except Exception as e:
                # Fallback: process individually
                self.log_activity(f"Batch risk detection failed, falling back to individual processing")
                for item_id, text in zip(batch_ids, batch_texts):
                    all_results[item_id] = self.detect_risk_single(text, item_id)

        self.log_activity(f"Analyzed {len(all_results)} items for risks")
        return all_results

    def analyze_news_risks(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add risk assessments to news articles DataFrame.

        Args:
            news_df: DataFrame with news article data

        Returns:
            DataFrame with added risk columns
        """
        if news_df.empty:
            return news_df

        # Check if already analyzed
        if all(col in news_df.columns for col in ["risk_flag", "risk_description", "severity"]):
            # Check if values exist
            if news_df["risk_flag"].notna().all():
                self.log_activity("News articles already risk-analyzed, skipping")
                return news_df

        # Prepare texts (headline + content preview)
        texts = []
        for _, row in news_df.iterrows():
            headline = str(row.get("headline", ""))
            content = str(row.get("content", ""))[:400]
            texts.append(f"{headline}\n{content}")

        item_ids = news_df["article_id"].astype(str).tolist()

        # Detect risks
        with st.spinner("Analyzing news articles for risks..."):
            risks = self.detect_risks_batch(texts, item_ids)

        # Add to DataFrame
        news_df = news_df.copy()

        news_df["risk_flag"] = news_df["article_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("risk_flag", False)
        )
        news_df["risk_description"] = news_df["article_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("risk_description")
        )
        news_df["severity"] = news_df["article_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("severity")
        )

        risk_count = news_df["risk_flag"].sum()
        self.log_activity(f"Identified {risk_count} risks in {len(news_df)} news articles")

        return news_df

    def analyze_inquiry_risks(self, inquiries_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add risk assessments to inquiries DataFrame.

        Args:
            inquiries_df: DataFrame with inquiry data

        Returns:
            DataFrame with added risk columns
        """
        if inquiries_df.empty:
            return inquiries_df

        # Check if already analyzed
        if all(col in inquiries_df.columns for col in ["risk_flag", "risk_description", "severity"]):
            if inquiries_df["risk_flag"].notna().all():
                self.log_activity("Inquiries already risk-analyzed, skipping")
                return inquiries_df

        # Prepare texts (subject + body preview)
        texts = []
        for _, row in inquiries_df.iterrows():
            subject = str(row.get("subject", ""))
            body = str(row.get("body", ""))[:400]
            texts.append(f"{subject}\n{body}")

        item_ids = inquiries_df["inquiry_id"].astype(str).tolist()

        # Detect risks
        with st.spinner("Analyzing inquiries for risks..."):
            risks = self.detect_risks_batch(texts, item_ids)

        # Add to DataFrame
        inquiries_df = inquiries_df.copy()

        inquiries_df["risk_flag"] = inquiries_df["inquiry_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("risk_flag", False)
        )
        inquiries_df["risk_description"] = inquiries_df["inquiry_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("risk_description")
        )
        inquiries_df["severity"] = inquiries_df["inquiry_id"].astype(str).map(
            lambda x: risks.get(x, {}).get("severity")
        )

        risk_count = inquiries_df["risk_flag"].sum()
        self.log_activity(f"Identified {risk_count} risks in {len(inquiries_df)} inquiries")

        return inquiries_df
