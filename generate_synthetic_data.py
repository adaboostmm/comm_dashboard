"""
Synthetic Data Generator - 6 months of data
Generates 150 records per category for each 7-day period over 6 months (26 periods)
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


# Configuration
OUTPUT_DIR = Path(__file__).parent / "synthetic_data"

# 6 months of data: Start from June 1, 2024 to Nov 30, 2024 (6 months = 26 weeks)
BASE_START_DATE = datetime(2024, 6, 1)
NUM_WEEKS = 26  # 6 months

# Categories
INQUIRY_CATEGORIES = [
    "monetary_policy", "inflation", "banking_regulation", "interest_rates",
    "employment", "financial_stability", "housing", "consumer_protection",
    "economic_outlook", "quantitative_easing", "federal_funds_rate"
]

INQUIRY_SOURCES = ["media", "public", "stakeholder"]
INQUIRY_PRIORITIES = ["high", "medium", "low"]
INQUIRY_CHANNELS = ["email", "web_form", "phone", "letter"]

NEWS_SOURCES = ["bloomberg", "wall_street_journal", "reuters", "financial_times", "cnbc", "associated_press"]
NEWS_TOPICS = ["monetary_policy", "interest_rates", "inflation", "employment", "banking_regulation",
               "financial_stability", "fed_communications"]

SOCIAL_PLATFORMS = ["twitter", "reddit", "facebook", "linkedin"]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "David", "Barbara", "William", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"]


def generate_inquiries(count: int, start_date: datetime, end_date: datetime, start_id: int) -> List[Dict[str, Any]]:
    """Generate inquiries with variety across all categories."""
    inquiries = []

    for i in range(count):
        category = INQUIRY_CATEGORIES[i % len(INQUIRY_CATEGORIES)]
        source = random.choice(INQUIRY_SOURCES)

        # Random timestamp within period
        total_seconds = int((end_date - start_date).total_seconds())
        random_seconds = random.randint(0, total_seconds)
        timestamp = start_date + timedelta(seconds=random_seconds)

        category_display = category.replace("_", " ").title()

        if source == "media":
            subject = f"Press Inquiry: {category_display} Policy Update"
            body = f"Requesting official statement on {category_display}. Publication deadline approaching. Need spokesperson comments."
            org = random.choice(["Wall Street Journal", "Bloomberg", "Reuters", "Financial Times", "CNBC"])
        elif source == "public":
            subject = f"Question about {category_display}"
            body = f"I'm concerned about how {category_display} affects my family. Need clear information about Fed policy."
            org = "Individual"
        else:
            subject = f"Congressional Request: {category_display} Briefing"
            org = random.choice(["Office of Senator Martinez", "House Financial Services", "State Banking Dept"])
            body = f"Formal request from {org} for briefing on {category_display}. Constituents need answers."

        inquiry = {
            "id": f"INQ-SYN-{start_id + i:05d}",
            "source": source,
            "channel": random.choice(INQUIRY_CHANNELS),
            "subject": subject,
            "body": body,
            "category": category,
            "priority": random.choice(INQUIRY_PRIORITIES),
            "timestamp": timestamp.isoformat(),
            "sender_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "sender_organization": org
        }
        inquiries.append(inquiry)

    return inquiries


def generate_news(count: int, start_date: datetime, end_date: datetime, start_id: int) -> List[Dict[str, Any]]:
    """Generate news articles with variety across all topics."""
    articles = []

    headlines = [
        "Fed Maintains Monetary Policy Stance",
        "Interest Rates Hold Steady Amid Economic Signals",
        "Federal Reserve Addresses Inflation Concerns",
        "Employment Data Shapes Fed Policy Direction",
        "Banking Sector Responds to Regulatory Changes",
        "Financial Stability Review Released",
        "Fed Communications Clarify Policy Path"
    ]

    for i in range(count):
        main_topic = NEWS_TOPICS[i % len(NEWS_TOPICS)]
        topics = [main_topic] + random.sample([t for t in NEWS_TOPICS if t != main_topic], k=min(2, len(NEWS_TOPICS)-1))

        total_seconds = int((end_date - start_date).total_seconds())
        random_seconds = random.randint(0, total_seconds)
        timestamp = start_date + timedelta(seconds=random_seconds)

        headline = headlines[i % len(headlines)]
        snippet = f"Federal Reserve officials discussed {main_topic.replace('_', ' ')} amid ongoing economic monitoring."
        full_text = f"{snippet}\n\nFederal Reserve Bank of San Francisco President Mary Daly provided insights on the central bank's approach. Officials continue monitoring inflation, employment, and financial conditions closely.\n\nMarket analysts offered varied perspectives on the Fed's strategy and its implications for the broader economy."

        sentiment_score = round(random.uniform(-0.7, 0.7), 2)
        risk_flag = random.random() < 0.20

        severity = None
        risk_desc = None
        if risk_flag:
            severity = random.choice(["low", "medium", "high"])
            risk_desc = f"{severity.title()} risk communication concern"

        article = {
            "id": f"NEWS-SYN-{start_id + i:05d}",
            "source": random.choice(NEWS_SOURCES),
            "headline": headline,
            "snippet": snippet,
            "full_text": full_text,
            "author": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "sentiment": "negative" if sentiment_score < -0.2 else "positive" if sentiment_score > 0.2 else "neutral",
            "sentiment_score": sentiment_score,
            "topics": topics,
            "entities_mentioned": ["Federal Reserve", "Mary Daly", "FRBSF", "FOMC"],
            "risk_flag": risk_flag,
            "risk_description": risk_desc,
            "severity": severity,
            "published_date": timestamp.isoformat(),
            "word_count": random.randint(250, 500)
        }
        articles.append(article)

    return articles


def generate_social_media(count: int, start_date: datetime, end_date: datetime, start_id: int) -> List[Dict[str, Any]]:
    """Generate social media posts."""
    posts = []

    templates = [
        "Fed's {} policy affecting {}. #Fed #Economy",
        "Question: How does {} impact everyday Americans? #AskTheFed",
        "Latest {} news from Federal Reserve #MonetaryPolicy",
        "Concerned about {} and my {} #Economy",
        "Fed discusses {}. Key point: {} matters #FederalReserve"
    ]

    for i in range(count):
        platform = random.choice(SOCIAL_PLATFORMS)

        total_seconds = int((end_date - start_date).total_seconds())
        random_seconds = random.randint(0, total_seconds)
        timestamp = start_date + timedelta(seconds=random_seconds)

        topic = random.choice(INQUIRY_CATEGORIES).replace("_", " ")
        impact = random.choice(["savings", "mortgage", "jobs", "retirement", "investments"])

        template = random.choice(templates)
        content = template.format(topic, impact)

        sentiment_score = round(random.uniform(-0.8, 0.8), 2)

        if platform == "twitter":
            likes = random.randint(10, 3000)
            engagement = {"likes": likes, "retweets": random.randint(0, likes // 3), "replies": random.randint(0, likes // 4)}
        elif platform == "reddit":
            upvotes = random.randint(20, 1500)
            engagement = {"upvotes": upvotes, "downvotes": random.randint(0, upvotes // 10), "comments": random.randint(0, upvotes // 3)}
        else:
            reactions = random.randint(15, 2000)
            engagement = {"reactions": reactions, "shares": random.randint(0, reactions // 4), "comments": random.randint(0, reactions // 3)}

        post = {
            "id": f"SM-SYN-{start_id + i:05d}",
            "platform": platform,
            "author": f"@{random.choice(['econ', 'finance', 'market', 'fed'])}{random.randint(100, 9999)}",
            "content": content,
            "sentiment_score": sentiment_score,
            "timestamp": timestamp.isoformat(),
            "engagement": engagement,
            "verified": random.random() < 0.05
        }
        posts.append(post)

    return posts


def main():
    """Generate 6 months of synthetic data (26 weeks, 7-day periods)."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("="*80)
    print("SYNTHETIC DATA GENERATOR - 6 MONTHS")
    print("="*80)
    print(f"Generating {NUM_WEEKS} weeks of data (7-day periods)")
    print(f"150 records per category per week = 450 records/week")
    print(f"Total: {NUM_WEEKS * 450} records")
    print(f"Output: {OUTPUT_DIR}/")
    print("="*80)
    print()

    total_inquiries = 0
    total_news = 0
    total_social = 0

    for week_num in range(NUM_WEEKS):
        # Calculate 7-day period
        period_start = BASE_START_DATE + timedelta(weeks=week_num)
        period_end = period_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        print(f"Week {week_num + 1}/{NUM_WEEKS}: {period_start.date()} to {period_end.date()}")

        # Generate data with unique IDs
        inquiries = generate_inquiries(150, period_start, period_end, week_num * 150)
        news = generate_news(150, period_start, period_end, week_num * 150)
        social_media = generate_social_media(150, period_start, period_end, week_num * 150)

        # Save files
        period_label = period_start.strftime("%Y%m%d")

        inq_file = OUTPUT_DIR / f"inquiries_synthetic_{period_label}.json"
        with open(inq_file, 'w') as f:
            json.dump(inquiries, f, indent=2)

        news_file = OUTPUT_DIR / f"news_articles_synthetic_{period_label}.json"
        with open(news_file, 'w') as f:
            json.dump(news, f, indent=2)

        social_file = OUTPUT_DIR / f"social_media_synthetic_{period_label}.json"
        with open(social_file, 'w') as f:
            json.dump(social_media, f, indent=2)

        total_inquiries += len(inquiries)
        total_news += len(news)
        total_social += len(social_media)

        print(f"  ✅ Generated: 150 inquiries, 150 news, 150 social = 450 records")

    print("\n" + "="*80)
    print("✨ GENERATION COMPLETE!")
    print("="*80)
    print(f"Total Generated:")
    print(f"  • {total_inquiries:,} inquiries")
    print(f"  • {total_news:,} news articles")
    print(f"  • {total_social:,} social media posts")
    print(f"  • {total_inquiries + total_news + total_social:,} TOTAL records")
    print(f"\nDate Range: {BASE_START_DATE.date()} to {(BASE_START_DATE + timedelta(weeks=NUM_WEEKS)).date()}")
    print(f"Files saved to: {OUTPUT_DIR}/")
    print("="*80)


if __name__ == "__main__":
    main()
