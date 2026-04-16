# Communication Intelligence Dashboard
## System Architecture

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Streamlit Web Application)                  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Dashboard   │  │Inquiry Queue │  │News Monitor  │  ...    │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION STATE LAYER                          │
│              (Streamlit st.session_state)                       │
│                                                                 │
│  • Cached data (inquiries, news, social_media, templates)      │
│  • Agent instances (singleton pattern)                         │
│  • User session state                                          │
│  • Activity logs                                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MULTI-AGENT AI SYSTEM                       │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │Classifier│ │ Response │ │ Insights │ │   Risk   │  │  │
│  │  │  Agent   │ │Generator │ │Generator │ │ Detector │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │                                                          │  │
│  │  ┌──────────┐                                           │  │
│  │  │ Chatbot  │         All inherit from BaseAgent       │  │
│  │  │  Agent   │                                           │  │
│  │  └──────────┘                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SERVICES LAYER                        │  │
│  │                                                          │  │
│  │  ┌─────────────────┐        ┌──────────────────────┐   │  │
│  │  │ BedrockClient   │        │    DataLoader        │   │  │
│  │  │                 │        │                      │   │  │
│  │  │ • API Wrapper   │        │ • Load JSON files    │   │  │
│  │  │ • Token Tracking│        │ • Pickle caching     │   │  │
│  │  │ • Retry Logic   │        │ • Data normalization │   │  │
│  │  └─────────────────┘        └──────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           AWS Bedrock - Claude Sonnet 4.5                │  │
│  │              (Natural Language Processing)               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ JSON Files   │  │ Pickle Cache │  │  Configuration       │ │
│  │              │  │              │  │                      │ │
│  │ • inquiries  │  │ • inquiries  │  │ • .env file          │ │
│  │ • news       │  │ • news       │  │ • config.py          │ │
│  │ • social     │  │ • social     │  │ • API credentials    │ │
│  │ • templates  │  │ • templates  │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION STARTUP                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ Check Cache? │
      └──────┬───────┘
             │
        Yes  │  No
      ┌──────┴───────┐
      │              │
      ▼              ▼
┌──────────┐   ┌──────────────┐
│Load from │   │Load from JSON│
│Pickle    │   │Files         │
│Cache     │   │              │
│          │   │• Read files  │
│(Fast:    │   │• Normalize   │
│1-2 sec)  │   │• Convert     │
└─────┬────┘   └──────┬───────┘
      │               │
      │               ▼
      │        ┌──────────────┐
      │        │Create Pickle │
      │        │Cache         │
      │        └──────┬───────┘
      │               │
      └───────┬───────┘
              │
              ▼
      ┌───────────────┐
      │Store in       │
      │Session State  │
      └───────┬───────┘
              │
              ▼
      ┌───────────────────┐
      │Initialize Agents  │
      │                   │
      │DEMO_MODE=true?    │
      │• Yes: Mock data   │
      │• No: AI process   │
      └───────┬───────────┘
              │
              ▼
      ┌───────────────────┐
      │Render UI          │
      │                   │
      │User Interactions: │
      │• Filter data      │
      │• Generate response│
      │• Ask questions    │
      │• View charts      │
      └───────────────────┘
```

---

## 🤖 Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          BaseAgent                              │
│                      (Abstract Base Class)                      │
│                                                                 │
│  Properties:                                                    │
│  • name: str                                                    │
│  • bedrock_client: BedrockClient                               │
│                                                                 │
│  Methods:                                                       │
│  • get_system_prompt() → str  [Abstract]                       │
│  • call_llm(prompt, cache_system=False) → str                  │
│  • log_activity(action, details)                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Inherits
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ClassifierAgent   │      │RiskAgent         │
│                  │      │                  │
│Categorizes:      │      │Detects:          │
│• Inquiries       │      │• Risk flags      │
│• News articles   │      │• Severity levels │
│• Social posts    │      │• Risk description│
└──────────────────┘      └──────────────────┘
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ResponseGenerator │      │InsightsGenerator │
│                  │      │                  │
│Generates:        │      │Creates:          │
│• Template match  │      │• Trend analysis  │
│• Custom response │      │• Executive summary│
│• Refinements     │      │• Key insights    │
└──────────────────┘      └──────────────────┘
        │
        ▼
┌──────────────────┐
│ChatbotAgent      │
│                  │
│Provides:         │
│• Q&A interface   │
│• Context memory  │
│• Suggestions     │
└──────────────────┘
```

**Shared Resources:**
- All agents share a single `BedrockClient` instance
- Token usage tracked globally and per-agent
- Activity logs centralized in session state

---

## 🔄 Request Flow - Generate Response

```
User clicks "Generate Response" on an inquiry
                │
                ▼
        ┌───────────────┐
        │UI Component   │
        │(inquiry_queue)│
        └───────┬───────┘
                │
                ▼
        ┌───────────────────┐
        │ResponseGenerator  │
        │Agent              │
        └───────┬───────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌──────────────┐  ┌─────────────────┐
│Check         │  │If no match:     │
│Templates     │  │Call LLM via     │
│              │  │BedrockClient    │
└──────┬───────┘  └────────┬────────┘
       │                   │
       │ Match found       │ Custom response
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
        ┌────────────────┐
        │Log Activity    │
        │(track tokens)  │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │Return response │
        │to UI           │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │Display in      │
        │Streamlit       │
        └────────────────┘
```

---

## 🗂️ Folder Structure

```
comm_project/
│
├── 📄 app.py                          # Main application entry point
├── 📄 config.py                       # Configuration & environment variables
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env                            # Environment variables (not in git)
│
├── 📁 agents/                         # Multi-agent AI system
│   ├── 📄 __init__.py
│   ├── 📄 base_agent.py              # Abstract base class
│   ├── 📄 classifier_agent.py        # Categorization logic
│   ├── 📄 response_generator_agent.py # Response generation
│   ├── 📄 insights_generator_agent.py # Dashboard insights
│   ├── 📄 risk_agent.py              # Risk detection
│   └── 📄 chatbot_agent.py           # Conversational AI
│
├── 📁 services/                       # Core services
│   ├── 📄 __init__.py
│   ├── 📄 bedrock_client.py          # AWS Bedrock API wrapper
│   └── 📄 data_loader.py             # Data loading & caching
│
├── 📁 components/                     # UI components (Streamlit)
│   ├── 📄 __init__.py
│   ├── 📄 dashboard.py               # Main dashboard view
│   ├── 📄 inquiry_queue.py           # Inquiry management
│   ├── 📄 news_monitor.py            # News monitoring
│   └── 📄 chatbot.py                 # AI assistant interface
│
├── 📁 utils/                          # Utility functions
│   ├── 📄 __init__.py
│   ├── 📄 chart_utils.py             # Plotly chart creation
│   └── 📄 data_processing.py         # Data filtering & processing
│
├── 📁 assets/                         # Static assets
│   └── 📄 styles.css                 # Custom CSS styling
│
├── 📁 synthetic_data/                 # Generated data files
│   ├── 📄 inquiries_week_1.json      # Week 1 inquiries
│   ├── 📄 inquiries_week_2.json      # Week 2 inquiries
│   ├── ...                           # (26 weeks total)
│   ├── 📄 news_articles_week_1.json  # Week 1 news
│   ├── ...                           # (26 weeks total)
│   ├── 📄 social_media_week_1.json   # Week 1 social
│   └── ...                           # (26 weeks total)
│
├── 📁 .cache/                         # Pickle cache (generated)
│   ├── 📄 inquiries.pkl              # Cached inquiries
│   ├── 📄 news.pkl                   # Cached news
│   ├── 📄 social.pkl                 # Cached social media
│   └── 📄 templates.pkl              # Cached templates
│
├── 📄 generate_synthetic_data.py      # Script to generate data
├── 📄 preload_data.py                 # Script to create cache
├── 📄 test_setup.py                   # Environment test script
│
├── 📄 CLAUDE.md                       # AI assistant guidance
├── 📄 DEVELOPER_PRESENTATION.md       # This presentation
└── 📄 ARCHITECTURE.md                 # Architecture documentation
```

---

## 🔌 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py (Main)                           │
│                                                                 │
│  1. Load configuration (config.py)                             │
│  2. Initialize session state                                   │
│  3. Load data via DataLoader                                   │
│  4. Initialize agents                                          │
│  5. Render sidebar navigation                                  │
│  6. Route to selected component                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─────────────────┬──────────────────┬──────────────┐
             │                 │                  │              │
             ▼                 ▼                  ▼              ▼
    ┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐
    │   dashboard    │ │inquiry_queue │ │news_monitor  │ │ chatbot  │
    │   component    │ │  component   │ │  component   │ │component │
    └────────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────┬─────┘
             │                │                 │               │
             │                │                 │               │
             │  Uses Charts   │  Uses Agents    │  Uses Agents  │
             │                │                 │               │
             ▼                ▼                 ▼               ▼
    ┌────────────────┐ ┌─────────────────────────────────────────────┐
    │  chart_utils   │ │         Multi-Agent System                  │
    │                │ │                                             │
    │ • Sentiment    │ │  ClassifierAgent  ResponseGeneratorAgent   │
    │   trends       │ │  InsightsGeneratorAgent  RiskAgent         │
    │ • Category pie │ │  ChatbotAgent                              │
    │ • Source bars  │ │                                             │
    │ • Risk dist.   │ │  All agents use ──────────────┐            │
    └────────────────┘ └────────────────────────────────┼────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │ BedrockClient    │
                                              │                  │
                                              │ • API calls      │
                                              │ • Token tracking │
                                              │ • Retry logic    │
                                              └──────────┬───────┘
                                                         │
                                                         ▼
                                              ┌──────────────────┐
                                              │ AWS Bedrock API  │
                                              │ Claude Sonnet 4.5│
                                              └──────────────────┘
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                             │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Configuration Security
┌─────────────────────────────────────────────────────────────────┐
│  .env file (not in version control)                             │
│  ├── API_KEY=xxxxx                                              │
│  ├── API_ENDPOINT=xxxxx                                         │
│  └── MODEL_NAME=xxxxx                                           │
│                                                                 │
│  .gitignore ensures .env never committed                        │
│  config.py loads via python-dotenv                              │
└─────────────────────────────────────────────────────────────────┘

Layer 2: Data Security
┌─────────────────────────────────────────────────────────────────┐
│  • All demo data is synthetic (no real PII)                     │
│  • Session state isolated per user                              │
│  • No data persistence beyond session                           │
└─────────────────────────────────────────────────────────────────┘

Layer 3: API Security
┌─────────────────────────────────────────────────────────────────┐
│  BedrockClient:                                                 │
│  • Credentials from environment only                            │
│  • HTTPS communication                                          │
│  • Timeout protection (30 seconds)                              │
│  • Retry with exponential backoff                               │
│  • Token usage monitoring                                       │
└─────────────────────────────────────────────────────────────────┘

Layer 4: Error Handling
┌─────────────────────────────────────────────────────────────────┐
│  • Try-catch blocks around all API calls                        │
│  • Graceful degradation on failures                             │
│  • User-friendly error messages (no stack traces to users)      │
│  • Activity logging for debugging                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERFORMANCE OPTIMIZATION                      │
└─────────────────────────────────────────────────────────────────┘

1. Data Loading Optimization
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  JSON Files (78 files)          Pickle Cache (.cache/)         │
│  ├── inquiries_*.json      →    ├── inquiries.pkl             │
│  ├── news_*.json           →    ├── news.pkl                  │
│  └── social_*.json         →    └── social.pkl                │
│                                                                 │
│  First Load: 30+ seconds        Subsequent: 1-2 seconds        │
│                                                                 │
│  preload_data.py generates pickle cache once                   │
└─────────────────────────────────────────────────────────────────┘

2. Session State Caching
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  st.session_state.data                                         │
│  • Loaded once per session                                     │
│  • Persists across page interactions                           │
│  • No re-processing on navigation                              │
│                                                                 │
│  st.session_state.data_processed                               │
│  • Flag prevents duplicate AI processing                       │
│  • Agents run once, results cached                             │
└─────────────────────────────────────────────────────────────────┘

3. AI Optimization (Token Management)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Batch Processing:                                             │
│  • Multiple items in single API call                           │
│  • Reduces API overhead                                        │
│                                                                 │
│  Conditional Calls:                                            │
│  • Only call LLM when user action requires it                  │
│  • Use existing data when available                            │
│                                                                 │
│  Template Matching:                                            │
│  • Try templates before calling LLM                            │
│  • Instant response for common inquiries                       │
│                                                                 │
│  Insights Caching:                                             │
│  • Dashboard insights cached for 5 minutes                     │
│  • Avoid regenerating same insights                            │
│                                                                 │
│  Demo Mode:                                                    │
│  • DEMO_MODE=true skips LLM on startup                         │
│  • Uses mock data for instant load                             │
└─────────────────────────────────────────────────────────────────┘

4. UI Rendering Optimization
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Pagination:                                                   │
│  • Show 20 items per page (configurable)                       │
│  • Reduces rendering overhead                                  │
│                                                                 │
│  Lazy Loading:                                                 │
│  • Charts render only when visible                             │
│  • Expandable sections load on demand                          │
│                                                                 │
│  Filtered Data:                                                │
│  • Filter before rendering (not after)                         │
│  • Only process visible date range                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 State Management

```
┌─────────────────────────────────────────────────────────────────┐
│              Streamlit Session State Structure                 │
└─────────────────────────────────────────────────────────────────┘

st.session_state
├── initialized: bool
│   └── Tracks if app has been initialized
│
├── data: Dict
│   ├── inquiries: pd.DataFrame
│   ├── news: pd.DataFrame
│   ├── social_media: pd.DataFrame
│   └── templates: pd.DataFrame
│
├── data_processed: bool
│   └── Flag to prevent duplicate AI processing
│
├── bedrock_client: BedrockClient
│   └── Shared API client (singleton)
│
├── classifier_agent: ClassifierAgent
│   └── Instance cached for session
│
├── risk_agent: RiskAgent
│   └── Instance cached for session
│
├── response_generator_agent: ResponseGeneratorAgent
│   └── Instance cached for session
│
├── insights_generator_agent: InsightsGeneratorAgent
│   └── Instance cached for session
│
├── chatbot_agent: ChatbotAgent
│   └── Instance cached for session
│
├── agent_logs: List[Dict]
│   └── Activity log (last 100 entries)
│
├── data_summary: Dict
│   └── Count statistics for sidebar
│
├── selected_date_range_idx: int
│   └── Currently selected date range
│
└── chat_history: List[Dict]
    └── Conversation history for chatbot

**Key Principles:**
• Initialize once per session
• Cache expensive operations
• Persist across page interactions
• Reset only on app restart
```

---

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                           │
└─────────────────────────────────────────────────────────────────┘

Option 1: Local Development
┌─────────────────────────────────────────────────────────────────┐
│  Developer Machine                                              │
│  ├── Python 3.8+                                                │
│  ├── Install requirements.txt                                  │
│  ├── Configure .env                                             │
│  ├── Generate data (generate_synthetic_data.py)                │
│  ├── Create cache (preload_data.py)                            │
│  └── Run: streamlit run app.py                                 │
│                                                                 │
│  Access: http://localhost:8501                                  │
└─────────────────────────────────────────────────────────────────┘

Option 2: Server Deployment
┌─────────────────────────────────────────────────────────────────┐
│  Production Server (Linux/Windows)                              │
│  ├── Python 3.8+ installed                                      │
│  ├── Clone repository                                           │
│  ├── Setup virtual environment                                  │
│  ├── Install dependencies                                       │
│  ├── Configure .env with production credentials                 │
│  ├── Generate data and cache                                    │
│  ├── Run with systemd/PM2/Windows Service                       │
│  └── Configure reverse proxy (nginx/Apache)                     │
│                                                                 │
│  Access: https://your-domain.com                                │
└─────────────────────────────────────────────────────────────────┘

Option 3: Cloud Deployment (AWS/Azure/GCP)
┌─────────────────────────────────────────────────────────────────┐
│  Cloud Instance                                                 │
│  ├── EC2/VM/App Service                                         │
│  ├── Load balancer (optional)                                   │
│  ├── SSL certificate                                            │
│  ├── Environment variables in cloud config                      │
│  ├── Auto-scaling (optional)                                    │
│  └── Monitoring & logging                                       │
└─────────────────────────────────────────────────────────────────┘

Resource Requirements:
┌─────────────────────────────────────────────────────────────────┐
│  Minimum:           Recommended:                                │
│  • 2 CPU cores      • 4+ CPU cores                              │
│  • 4 GB RAM         • 8+ GB RAM                                 │
│  • 2 GB disk        • 5+ GB disk                                │
│  • Python 3.8+      • Python 3.10+                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────┐
│                  MONITORING ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

Built-in Monitoring (Sidebar)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Token Usage Tracking                                          │
│  ├── Total tokens used                                         │
│  ├── Per-agent breakdown                                       │
│  ├── Warning thresholds (10K, 15K)                             │
│  └── Reset capability                                          │
│                                                                 │
│  Activity Logs                                                 │
│  ├── Last 100 agent actions                                    │
│  ├── Timestamps                                                │
│  ├── Success/failure status                                    │
│  └── Details of operations                                     │
│                                                                 │
│  System Status                                                 │
│  ├── Demo mode indicator                                       │
│  ├── Data summary counts                                       │
│  └── Active risk count                                         │
└─────────────────────────────────────────────────────────────────┘

External Monitoring (Optional)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Application Logs                                              │
│  • stdout/stderr capture                                       │
│  • Log aggregation (ELK, Splunk, CloudWatch)                  │
│                                                                 │
│  Performance Metrics                                           │
│  • Response times                                              │
│  • API call latency                                            │
│  • Error rates                                                 │
│                                                                 │
│  Health Checks                                                 │
│  • Endpoint monitoring                                         │
│  • Uptime tracking                                             │
│  • Alert notifications                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Extension Points

```
┌─────────────────────────────────────────────────────────────────┐
│                HOW TO EXTEND THE SYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

Add New Agent
┌─────────────────────────────────────────────────────────────────┐
│  1. Create new file: agents/my_agent.py                         │
│  2. Inherit from BaseAgent                                      │
│  3. Implement get_system_prompt()                               │
│  4. Add business logic methods                                  │
│  5. Initialize in app.py                                        │
│  6. Call from UI components                                     │
└─────────────────────────────────────────────────────────────────┘

Add New UI Component
┌─────────────────────────────────────────────────────────────────┐
│  1. Create new file: components/my_component.py                 │
│  2. Define render function: render_my_component(data)           │
│  3. Use Streamlit widgets                                       │
│  4. Import in app.py                                            │
│  5. Add navigation option in sidebar                            │
│  6. Route to component in main()                                │
└─────────────────────────────────────────────────────────────────┘

Add New Data Source
┌─────────────────────────────────────────────────────────────────┐
│  1. Update config.py with file patterns                         │
│  2. Add loader method in data_loader.py                         │
│  3. Update load_all_data() to include new source                │
│  4. Add to session state structure                              │
│  5. Create UI component to display                              │
└─────────────────────────────────────────────────────────────────┘

Add New Chart Type
┌─────────────────────────────────────────────────────────────────┐
│  1. Add function to utils/chart_utils.py                        │
│  2. Use Plotly (go.Figure or px.*)                              │
│  3. Apply consistent fonts (CHART_FONT, AXIS_TITLE_FONT)        │
│  4. Return go.Figure object                                     │
│  5. Call from UI component with st.plotly_chart()               │
└─────────────────────────────────────────────────────────────────┘

Integrate New AI Model
┌─────────────────────────────────────────────────────────────────┐
│  1. Create new client: services/my_model_client.py              │
│  2. Implement same interface as BedrockClient                   │
│  3. Update config.py with new credentials                       │
│  4. Update BaseAgent to use new client                          │
│  5. Test with all existing agents                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Technology Stack Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY LAYERS                            │
└─────────────────────────────────────────────────────────────────┘

Frontend Layer
┌─────────────────────────────────────────────────────────────────┐
│  Streamlit 1.31.0                                               │
│  ├── Web framework                                              │
│  ├── Built-in widgets                                           │
│  ├── Session state management                                   │
│  └── Hot reloading                                              │
│                                                                 │
│  Custom CSS (assets/styles.css)                                 │
│  ├── Purple gradient theme                                      │
│  ├── Glass morphism effects                                     │
│  ├── Animated backgrounds                                       │
│  └── Responsive design                                          │
└─────────────────────────────────────────────────────────────────┘

Visualization Layer
┌─────────────────────────────────────────────────────────────────┐
│  Plotly 5.18.0                                                  │
│  ├── Interactive charts                                         │
│  ├── Line charts (sentiment trends)                             │
│  ├── Pie charts (category distribution)                         │
│  ├── Bar charts (source breakdown)                              │
│  └── Gauge charts (overall sentiment)                           │
└─────────────────────────────────────────────────────────────────┘

Data Processing Layer
┌─────────────────────────────────────────────────────────────────┐
│  Pandas 2.1.4                                                   │
│  ├── DataFrame operations                                       │
│  ├── Filtering & aggregation                                    │
│  ├── Date range processing                                      │
│  └── Pickle serialization                                       │
└─────────────────────────────────────────────────────────────────┘

AI/ML Layer
┌─────────────────────────────────────────────────────────────────┐
│  AWS Bedrock - Claude Sonnet 4.5                                │
│  ├── Natural language understanding                             │
│  ├── Text classification                                        │
│  ├── Sentiment analysis                                         │
│  ├── Response generation                                        │
│  └── Conversational AI                                          │
│                                                                 │
│  Accessed via:                                                  │
│  • OpenAI-compatible API format                                 │
│  • Custom BedrockClient wrapper                                 │
│  • Retry logic with tenacity 8.2.3                              │
└─────────────────────────────────────────────────────────────────┘

Configuration Layer
┌─────────────────────────────────────────────────────────────────┐
│  python-dotenv 1.0.0                                            │
│  ├── .env file loading                                          │
│  ├── Environment variables                                      │
│  └── Secure credential management                               │
└─────────────────────────────────────────────────────────────────┘

HTTP Layer
┌─────────────────────────────────────────────────────────────────┐
│  Requests 2.31.0                                                │
│  ├── HTTP client for API calls                                  │
│  ├── Timeout handling                                           │
│  ├── Error handling                                             │
│  └── JSON encoding/decoding                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Design Principles

```
┌─────────────────────────────────────────────────────────────────┐
│              ARCHITECTURAL DESIGN PRINCIPLES                    │
└─────────────────────────────────────────────────────────────────┘

1. Separation of Concerns
   ├── UI components separate from business logic
   ├── Agents separate from data access
   ├── Services separate from presentation
   └── Configuration separate from code

2. Single Responsibility
   ├── Each agent has one job
   ├── Each component renders one view
   ├── Each service handles one concern
   └── Each utility focuses on one task

3. DRY (Don't Repeat Yourself)
   ├── BaseAgent for common functionality
   ├── Shared BedrockClient instance
   ├── Reusable chart functions
   └── Central configuration

4. Modularity
   ├── Easy to add new agents
   ├── Easy to add new components
   ├── Easy to swap data sources
   └── Easy to change AI models

5. Performance First
   ├── Cache everything possible
   ├── Lazy load when practical
   ├── Batch operations
   └── Minimize API calls

6. Security by Default
   ├── Credentials in environment
   ├── No secrets in code
   ├── Secure API communication
   └── Input validation

7. User Experience
   ├── Fast response times
   ├── Clear feedback
   ├── Intuitive navigation
   └── Beautiful design
```

---

## 📋 Summary

This architecture provides:

✅ **Scalable** - Handle thousands of records effortlessly

✅ **Maintainable** - Clean separation of concerns

✅ **Extensible** - Easy to add new features

✅ **Performant** - Sub-2-second load times

✅ **Secure** - Best practices implemented

✅ **User-Friendly** - Intuitive interface

**Built for the long term with modern best practices**

---

**Version 1.0** | **Last Updated: 2026-04-16**
