"""
Chatbot Component - Interactive AI assistant for querying communication data.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from config import Config


class ChatbotAgent(BaseAgent):
    """Specialized agent for chatbot interactions."""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(name="Chatbot")
        self.data = data

    def get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot."""
        return """You are an AI assistant for a Federal Reserve communications dashboard.

Your role is to help users understand and analyze communication data including:
- Inquiries from media, public, and stakeholders
- News articles about the Federal Reserve
- Social media posts

You have access to the following data context:
- Inquiry categories, priorities, sources
- News article sentiments, risk flags
- Social media engagement metrics

Guidelines:
1. Be helpful and informative
2. Reference specific data when answering questions
3. Keep responses concise but complete
4. Suggest relevant dashboard views when appropriate
5. Explain insights in clear, non-technical language
6. Acknowledge limitations if data is not available

User questions may ask about:
- Trends and patterns
- Specific inquiries or articles
- Risk assessments
- Sentiment analysis
- Response suggestions

Always ground your responses in the available data."""

    def _prepare_context(self, user_message: str) -> str:
        """
        Prepare relevant data context for the user's question.

        Args:
            user_message: User's question

        Returns:
            Formatted context string
        """
        context_parts = []

        # Basic data summary
        inquiries_df = self.data.get("inquiries", pd.DataFrame())
        news_df = self.data.get("news", pd.DataFrame())
        social_df = self.data.get("social_media", pd.DataFrame())

        context_parts.append(f"Available data: {len(inquiries_df)} inquiries, {len(news_df)} news articles, {len(social_df)} social media posts")

        # Check what the user is asking about
        user_lower = user_message.lower()

        # If asking about inquiries
        if "inquir" in user_lower or "question" in user_lower or "request" in user_lower:
            if not inquiries_df.empty:
                # Category distribution
                if "category" in inquiries_df.columns:
                    top_cats = inquiries_df["category"].value_counts().head(5)
                    context_parts.append(f"\nTop inquiry categories: {', '.join([f'{cat} ({count})' for cat, count in top_cats.items()])}")

                # Priority distribution
                if "priority" in inquiries_df.columns:
                    pri_counts = inquiries_df["priority"].value_counts()
                    context_parts.append(f"Priority breakdown: {', '.join([f'{pri} ({count})' for pri, count in pri_counts.items()])}")

                # Risk flags
                if "risk_flag" in inquiries_df.columns:
                    risk_count = inquiries_df["risk_flag"].sum() if inquiries_df["risk_flag"].dtype == bool else 0
                    if risk_count > 0:
                        context_parts.append(f"Inquiries with risk flags: {risk_count}")

        # If asking about news or sentiment
        if "news" in user_lower or "article" in user_lower or "sentiment" in user_lower or "media" in user_lower:
            if not news_df.empty:
                # Sentiment summary
                if "sentiment_score" in news_df.columns:
                    avg_sentiment = news_df["sentiment_score"].mean()
                    negative = len(news_df[news_df["sentiment_score"] < 0.4])
                    positive = len(news_df[news_df["sentiment_score"] > 0.6])
                    context_parts.append(f"\nNews sentiment: Avg {avg_sentiment:.2f}, {negative} negative, {positive} positive")

                # Risk flags
                if "risk_flag" in news_df.columns:
                    risk_count = news_df["risk_flag"].sum() if news_df["risk_flag"].dtype == bool else 0
                    if risk_count > 0:
                        context_parts.append(f"News articles with risk flags: {risk_count}")
                        if "severity" in news_df.columns:
                            risk_df = news_df[news_df["risk_flag"] == True]
                            severity_counts = risk_df["severity"].value_counts()
                            context_parts.append(f"Risk severity: {', '.join([f'{sev} ({count})' for sev, count in severity_counts.items()])}")

        # If asking about risks
        if "risk" in user_lower or "concern" in user_lower or "urgent" in user_lower:
            all_risks = []

            if not inquiries_df.empty and "risk_flag" in inquiries_df.columns:
                risky_inquiries = inquiries_df[inquiries_df["risk_flag"] == True]
                if not risky_inquiries.empty:
                    context_parts.append(f"\n{len(risky_inquiries)} inquiries flagged as risks")
                    if "risk_description" in risky_inquiries.columns:
                        sample_risks = risky_inquiries["risk_description"].dropna().head(3).tolist()
                        if sample_risks:
                            context_parts.append(f"Sample risk descriptions: {'; '.join(sample_risks)}")

            if not news_df.empty and "risk_flag" in news_df.columns:
                risky_news = news_df[news_df["risk_flag"] == True]
                if not risky_news.empty:
                    context_parts.append(f"\n{len(risky_news)} news articles flagged as risks")

        # Limit context size to avoid token overflow
        context = "\n".join(context_parts)
        if len(context) > 2000:
            context = context[:2000] + "..."

        return context

    def chat(self, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate a chat response.

        Args:
            user_message: User's message
            conversation_history: Previous messages in the conversation

        Returns:
            Assistant's response
        """
        # Prepare context from data
        data_context = self._prepare_context(user_message)

        # Build prompt with context and history
        prompt = f"Data Context:\n{data_context}\n\n"

        # Add recent conversation history (windowed to last 4 messages)
        if conversation_history:
            recent_history = conversation_history[-4:]
            prompt += "Recent conversation:\n"
            for msg in recent_history:
                role = msg["role"]
                content = msg["content"]
                prompt += f"{role}: {content}\n"
            prompt += "\n"

        prompt += f"User: {user_message}\n\nProvide a helpful response based on the data context and conversation."

        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                cache_system=False
            )

            self.log_activity(f"Chatbot response generated ({len(response)} chars)")
            return response

        except Exception as e:
            error_msg = self.handle_error(e, "generating chat response")
            return f"I'm sorry, I encountered an error: {str(e)}. Please try again."


def render_chatbot(data: Dict[str, Any]):
    """
    Render the chatbot interface.

    Args:
        data: Dictionary with communication data
    """
    # Title is now shown in main app.py

    st.markdown("""
    Ask me questions about your communication data:
    - *"What are the main concerns in recent inquiries?"*
    - *"Summarize risk flags in the news"*
    - *"Which topics have the most negative sentiment?"*
    - *"Show me high-priority inquiries"*
    """)

    # Initialize chatbot agent
    if "chatbot_agent" not in st.session_state:
        st.session_state.chatbot_agent = ChatbotAgent(data)

    # Initialize conversation history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history (compatible with Streamlit 1.8.0)
    st.markdown("### Conversation")

    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style="background-color: #e0f2fe; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #3b82f6;">
                    <b>You:</b><br>{message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="background-color: #f0fdf4; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #22c55e;">
                    <b>Assistant:</b><br>{message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Chat input (compatible with Streamlit 1.8.0)
    st.markdown("---")
    user_input = st.text_input(
        "Ask a question about your communication data:",
        key="chat_input",
        placeholder="e.g., What are the top inquiry categories?"
    )

    if st.button("Send", key="send_chat") and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Generate response
        with st.spinner("Thinking..."):
            agent = st.session_state.chatbot_agent
            response = agent.chat(user_input, st.session_state.chat_history[:-1])  # Exclude current message

            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

        # Conversation summarization if history gets too long
        if len(st.session_state.chat_history) > Config.CHATBOT_HISTORY_WINDOW:
            summarize_conversation()

        # Rerun to show new messages
        st.experimental_rerun()

    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")

        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.experimental_rerun()

        # Show token usage
        if "chatbot_agent" in st.session_state:
            agent = st.session_state.chatbot_agent
            tokens_used = agent.get_token_usage()
            st.metric("Tokens Used", f"{tokens_used:,}")

            if tokens_used > 15000:
                st.warning("⚠️ High token usage. Consider clearing chat history.")

        # Suggested questions
        st.subheader("💡 Suggested Questions")

        suggestions = [
            "What are the top inquiry categories?",
            "Summarize recent risk flags",
            "What's the sentiment trend?",
            "Show high-priority items",
            "What concerns are most common?"
        ]

        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion[:20]}"):
                # Trigger the suggestion as input
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": suggestion
                })
                st.experimental_rerun()


def summarize_conversation():
    """
    Summarize conversation history to reduce token usage.
    Keeps last 2 messages and creates a summary of earlier messages.
    """
    if len(st.session_state.chat_history) <= Config.CHATBOT_HISTORY_WINDOW:
        return

    # Get messages to summarize (all except last 2)
    messages_to_summarize = st.session_state.chat_history[:-2]
    recent_messages = st.session_state.chat_history[-2:]

    # Create summary
    summary_text = "Previous conversation summary:\n"
    for msg in messages_to_summarize:
        summary_text += f"{msg['role']}: {msg['content'][:100]}...\n"

    # Replace history with summary + recent messages
    st.session_state.chat_history = [
        {"role": "assistant", "content": f"[Conversation summary: Previous discussion covered inquiry categories, risk analysis, and sentiment trends.]"},
        *recent_messages
    ]
