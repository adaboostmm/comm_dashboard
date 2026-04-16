A comprehensive Streamlit dashboard for analyzing external communications using multi-agent AI system.

## Features

### 📊 Main Dashboard
- **7-Day Sentiment Trend**: Multi-line chart tracking sentiment across inquiries, news, and social media
- **Category Distribution**: Interactive pie chart of inquiry categories
- **Source Breakdown**: Bar chart showing inquiry sources
- **Risk Distribution**: Visual breakdown of detected risks by severity
- **AI-Generated Insights**: Real-time analysis with 5-minute caching

### 📬 Inquiry Queue
- **Smart Filtering**: Filter by source, priority, status, and category
- **Advanced Search**: Full-text search across inquiries
- **Risk Flagging**: Automatic identification of high-risk communications
- **Response Generation**: 
  - Template matching for efficiency
  - AI-powered response generation
  - Response refinement capabilities
- **Pagination**: Easy navigation through large datasets

### 📰 News Monitor
- **Card Layout**: Clean, scannable view of news articles
- **Sentiment Analysis**: Color-coded sentiment indicators
- **Risk Detection**: Automatic flagging with severity levels
- **Source Analytics**: Sentiment breakdown by news source
- **Full Article View**: Expandable detailed view with entity mentions

### 💬 AI Assistant
- **Context-Aware Chat**: Ask questions about your communication data
- **Conversation Memory**: Maintains context across interactions
- **Suggested Questions**: Quick-start prompts for common queries
- **Token Optimization**: Automatic conversation summarization

## Multi-Agent System

The dashboard uses 5 specialized AI agents:

1. **Classifier Agent**: Categorizes communications into topics (monetary policy, banking regulation, etc.)
2. **Response Generator Agent**: Matches templates or generates custom responses
3. **Insights Generator Agent**: Creates executive-level dashboard summaries
4. **Risk Detector Agent**: Identifies communication risks and assigns severity levels
5. **Chatbot Agent**: Interactive Q&A with context awareness

All agents share token tracking and caching for optimal efficiency.

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd <> 
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify environment variables**:
   update config with the following appropriately. 
   ```
   API_KEY=your_api_key
   API_ENDPOINT=your_end_point
   MODEL_NAME=anthropic.claude-sonnet-4-5-20250929-v1:0
   ```

## Usage

1. **Start the dashboard**:
   ```bash
   streamlit run app.py
   ```

2. **Access the dashboard**:
   Open your browser to `http://localhost:8501`

3. **Navigate between views**:
   Use the tabs at the top to switch between Dashboard, Inquiry Queue, News Monitor, and AI Assistant

## Project Structure

```
comm_project/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── agents/                     # Multi-agent system
│   ├── base_agent.py          # Abstract base class
│   ├── classifier_agent.py    # Communication categorization
│   ├── response_generator.py  # Response generation
│   ├── insights_agent.py      # Dashboard insights
│   └── risk_agent.py          # Risk detection
├── services/                   # Core services
│   ├── bedrock_client.py      # AWS Bedrock API client
│   └── data_loader.py         # Data loading and caching
├── components/                 # UI components
│   ├── dashboard.py           # Main dashboard
│   ├── inquiry_queue.py       # Inquiry management
│   ├── news_monitor.py        # News monitoring
│   └── chatbot.py             # AI assistant
├── utils/                      # Utility functions
│   ├── chart_utils.py         # Plotly charts
│   ├── data_processing.py     # Data manipulation
│   └── cache_utils.py         # Caching utilities
├── assets/
│   └── styles.css             # Dark theme CSS
└── sample_data/               # JSON data files
```

## Token Optimization

The system implements several strategies to minimize API token usage:

1. **Prompt Caching**: System prompts are cached for 5 minutes
2. **Batch Processing**: Multiple items processed in single API calls
3. **Conditional LLM Calls**: Only call AI when necessary
4. **Template Matching**: Responses use templates when possible
5. **Conversation Summarization**: Chat history automatically compressed
6. **Data Reuse**: Leverages existing sentiment/category data when available

Expected token usage: **10,000-15,000 tokens per demo session**

## Performance Targets

- Initial page load: < 3 seconds
- Chart interaction: < 1 second
- LLM response (chatbot): < 5 seconds
- Dashboard insights: < 3 seconds (cached)

## Data Format

The dashboard expects JSON files in the `sample_data/` directory:

- `inquiries_*.json`: Communication inquiries
- `news_articles_*.json`: News articles
- `social_media_*.json`: Social media posts
- `response_templates_*.json`: Response templates

## Troubleshooting

### Data Not Loading
- Verify `sample_data/` directory exists and contains JSON files
- Check file permissions
- Review console for error messages

- Reset token counter in sidebar
- Avoid frequent insights regeneration

### Performance Issues
- Reduce page size in inquiry queue
- Clear browser cache
- Check data file sizes

## Development

To extend the dashboard:

1. **Add New Agent**: Create class inheriting from `BaseAgent` in `agents/`
2. **Add New Component**: Create module in `components/` and import in `app.py`
3. **Add New Chart**: Add function to `utils/chart_utils.py`
4. **Modify Styling**: Edit `assets/styles.css`

## License

Uses Public data

## Support

For issues or questions, contact the development team.
