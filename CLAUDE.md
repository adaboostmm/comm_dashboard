# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Communication Intelligence Dashboard - A Streamlit application for analyzing Federal Reserve communications using a multi-agent AI system powered by Claude Sonnet 4.5 via AWS Bedrock. The dashboard processes inquiries, news articles, and social media posts to provide sentiment analysis, risk detection, category classification, and automated response generation.

## Development Commands

### Running the Application

```bash
# Start the dashboard (primary method)
streamlit run app.py

# Alternative method
python run_dashboard.py

# Using the shell script
./run_dashboard.sh
```

The dashboard will be available at `http://localhost:8501`

### Testing

```bash
# Verify environment setup
python test_setup.py

# This tests:
# - Package imports
# - Configuration validity
# - Data file presence
# - Data loading functionality
# - API client initialization
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and set:
# - API_KEY
# - API_ENDPOINT
# - MODEL_NAME
```

## Architecture

### Multi-Agent System

The application uses 5 specialized agents that inherit from `BaseAgent`:

1. **ClassifierAgent** - Categorizes communications into topics (monetary policy, banking regulation, inflation, employment, etc.)
2. **ResponseGeneratorAgent** - Matches templates or generates custom responses to inquiries
3. **InsightsGeneratorAgent** - Creates executive-level dashboard summaries (cached for 5 minutes)
4. **RiskDetectorAgent** - Identifies communication risks and assigns severity levels (low/medium/high)
5. **ChatbotAgent** - Interactive Q&A with context awareness and conversation memory

All agents:
- Share a single `BedrockClient` instance stored in Streamlit session state
- Track token usage individually and globally
- Implement retry logic via the `tenacity` library (3 retries with exponential backoff)
- System prompt caching is disabled as the API endpoint does not support it

### Core Services

**BedrockClient** (`services/bedrock_client.py`):
- Wraps the AWS Bedrock API endpoint for Claude Sonnet 4.5
- Uses OpenAI-compatible chat completions format
- Implements exponential backoff retry (3 attempts, 2-10 second waits)
- Tracks total token usage across all API calls
- System prompt caching is disabled (API endpoint does not support the format)

**DataLoader** (`services/data_loader.py`):
- Loads JSON files from `sample_data/` directory
- Converts to pandas DataFrames with field name normalization
- Caches data in Streamlit session state for 1 hour
- Handles both list and dict JSON formats
- Normalizes sentiment scores from -1 to 1 range into 0 to 1 range

### UI Components

All components are separate modules in `components/`:

- **dashboard.py** - Main dashboard with sentiment trends, category distribution, source breakdown, and AI-generated insights
- **inquiry_queue.py** - Paginated inquiry management with filtering, search, and response generation
- **news_monitor.py** - Card-based news article view with sentiment indicators and risk flagging
- **chatbot.py** - Conversational AI assistant with suggested questions and conversation summarization

### State Management

Streamlit session state is used extensively:
- `st.session_state.data` - All loaded data (inquiries, news, social_media, templates)
- `st.session_state.bedrock_client` - Shared API client instance
- `st.session_state.classifier_agent` / `risk_agent` - Agent instances
- `st.session_state.agent_logs` - Activity log (last 100 entries)
- `st.session_state.data_processed` - Flag to prevent re-processing on page refresh

### Token Optimization Strategy

**CRITICAL**: Token usage is constrained by API limitations. The system implements:

1. **Batch Processing** - Multiple items processed in single API calls
2. **Conditional LLM Calls** - Only invoke AI when necessary (user clicks "Generate Response")
3. **Template Matching First** - Response generation tries templates before full LLM generation
4. **Data Reuse** - Leverages existing sentiment/category fields from JSON data
5. **Conversation Summarization** - Chat history compressed after 10 messages

**Note**: Prompt caching is disabled (`cache_system=False` everywhere) as the API endpoint does not support the caching format.

Target: **10,000-15,000 tokens per demo session**

## Data Format

Sample data files in `sample_data/`:
- `inquiries_*.json` - Communication inquiries with fields: inquiry_id, sender_name, sender_organization, subject, body, source, priority, date_received
- `news_articles_*.json` - News articles with fields: article_id, headline, source, content, sentiment_score, published_date, entities
- `social_media_*.json` - Social media posts with fields: post_id, platform, author, content, sentiment_score, timestamp, engagement
- `response_templates_*.json` - Response templates for matching

DataLoader normalizes field names (e.g., `id` → `inquiry_id`, `full_text` → `content`) and handles missing columns by adding defaults.

## Configuration

**Config class** (`config.py`) provides centralized settings:
- API credentials loaded from `.env` via `python-dotenv`
- File paths: `BASE_DIR`, `SAMPLE_DATA_DIR`, `ASSETS_DIR`
- Token optimization: `CACHE_TTL_SECONDS=300`, `MAX_BATCH_SIZE=10`, `CHATBOT_HISTORY_WINDOW=10`
- UI settings: `PAGE_SIZE=20`, `CHART_HEIGHT=400`, `CHART_WIDTH=600`
- Sentiment thresholds and risk levels

## Agent Development Pattern

When creating or modifying agents:

1. Inherit from `BaseAgent` and implement `get_system_prompt()`
2. Use `self.call_llm()` for all LLM interactions (handles token tracking)
3. Keep `cache_system=False` (caching is disabled project-wide)
4. Log activities with `self.log_activity()` for debugging
5. Store agent instances in `st.session_state` (singleton pattern)
6. Batch operations when processing multiple items

Example:
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent")
    
    def get_system_prompt(self) -> str:
        return "You are a specialized assistant..."
    
    def process_item(self, item):
        prompt = f"Analyze this: {item}"
        return self.call_llm(prompt, cache_system=False)
```

## Common Patterns

**Adding New Chart Types**: Add functions to `utils/chart_utils.py` that return Plotly figure objects

**Modifying Dark Theme**: Edit `assets/styles.css` - CSS is loaded in `app.py` via `load_custom_css()`

**Adding New Data Sources**: 
1. Add glob pattern to `Config.get_sample_data_files()`
2. Create loader method in `DataLoader`
3. Update `load_all_data()` to include new data type

**Processing Data on Startup**:
- Data processing happens once when `st.session_state.data_processed` is False
- Add new processing logic to `initialize_agents()` in `app.py`
- Only process if data doesn't already have the required fields

## Performance Targets

- Initial page load: < 3 seconds
- Chart interaction: < 1 second
- LLM response (chatbot): < 5 seconds
- Dashboard insights: < 3 seconds (cached)

## Important Notes

- **Caching disabled**: System prompt caching is disabled project-wide as the API endpoint times out with caching format
- **Batch where possible**: Process multiple items in single API calls to reduce token overhead
- **Check existing fields**: Don't re-compute sentiment/category if already present in data
- **Session state persistence**: Streamlit reruns on every interaction - use session state to preserve expensive computations
- **API endpoint format**: Uses OpenAI-compatible format (`messages`, `system`, `temperature`, `max_tokens`) but hosted on AWS Bedrock
- **Error handling**: All agents catch `BedrockClientError` and display user-friendly messages via Streamlit
- **Timeout setting**: API requests timeout after 30 seconds with 3 retry attempts
