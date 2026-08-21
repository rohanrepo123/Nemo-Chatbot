# 🤖 Omni-NemoBot

> Agentic AI chatbot built with LangGraph, LangChain, OpenAI GPT-5.4 Nano, Streamlit, persistent SQLite memory, web search, and real-world API tools.

## 🌐 Live Demo

**https://omni-nemobot.streamlit.app/**

## ✨ Features

- 💬 Multi-turn conversations with persistent memory
- ⚡ Real-time response streaming
- 🧠 SQLite checkpoint-based conversation memory
- 🔄 Multiple chat threads with automatic titles
- 🤖 LangGraph agent with intelligent tool calling
- 🔍 Tavily web search
- 🌦️ Live weather information
- 📈 Stock market information
- 💱 Currency conversion
- 🧮 Calculator
- 🎬 Movie search, trending/popular movies, recommendations, and genre-based discovery
- 👤 Celebrity information
- 👨‍⚖️ Human-in-the-Loop tool execution
- 🔧 Live tool execution status in the UI

## 🏗️ Architecture

```text
                    User
                     │
                     ▼
              Streamlit Frontend
                     │
                     ▼
              LangGraph Agent
                     │
                     ▼
             OpenAI GPT-5.4 Nano
                     │
             ┌───────┴────────┐
             │                │
          No Tool          Tool Required
             │                │
             ▼                ▼
          Response          ToolNode
                              │
       ┌──────────┬───────────┼──────────┐
       ▼          ▼           ▼          ▼
    Tavily      TMDB      Finance     Utility APIs
    Search     Movies      APIs       Weather/etc.
       │          │           │          │
       └──────────┴───────────┴──────────┘
                              │
                              ▼
                         Tool Result
                              │
                              ▼
                              LLM
                              │
                              ▼
                        Final Response
                              │
                              ▼
                       SQLite Memory
```

## 🔄 LangGraph Workflow

```text
START
  │
  ▼
Response Node
  │
  ├── No tool ───────────────► END
  │
  └── Tool required
          │
          ▼
       ToolNode
          │
          ▼
      Tool Result
          │
          ▼
      Response Node
          │
          └──────────────► END
```

## 🛠️ Tools

| Tool | Purpose |
|---|---|
| Tavily Search | Current web information |
| WeatherStack | Current weather |
| Alpha Vantage | Stock information |
| ExchangeRate API | Currency exchange rates |
| Calculator | Basic arithmetic |
| TMDB Movie Details | Movie information |
| TMDB Trending | Trending movies by day/week |
| TMDB Popular | Popular movies |
| TMDB Recommendations | Similar movie recommendations |
| TMDB Genre Discovery | Genre-based movie recommendations |
| TMDB Person Search | Celebrity information |
| Stock Purchase | Human-approved simulated stock purchase |

## 🧠 Memory & Conversations

Each conversation receives a unique `thread_id`. LangGraph's `SqliteSaver` stores checkpoints in `Chatbot.db`, allowing conversations to persist across application sessions.

The sidebar provides:

- New chat creation
- Previous conversation selection
- Automatic conversation titles

## ⚡ Streaming & Tool Status

Responses are streamed to the interface as they are generated.

During tool execution, the UI displays statuses such as:

```text
🔧 Using `tavily_search`...
🔧 Using `trending_movies`...
🔧 Using `calculator`...
✅ Tool finished
```

## 🧩 Tech Stack

- **Python**
- **Streamlit**
- **LangChain**
- **LangGraph**
- **OpenAI GPT-5.4 Nano**
- **SQLite**
- **Tavily**
- **TMDB**
- **Alpha Vantage**
- **WeatherStack**
- **ExchangeRate API**
- **Requests**
- **python-dotenv**

## 📂 Project Structure

```text
Nemo-Chatbot/
├── backend.py
├── frontend.py
├── Chatbot.db
├── requirements.txt
├── README.md
├── .gitignore
└── assets/
    └── chat.png
```

## ⚙️ Installation

### 1. Clone

```bash
git clone https://github.com/rohanrepo123/Nemo-Chatbot.git
cd Nemo-Chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv311
```

Windows:

```bash
venv311\Scripts\activate
```

Linux/macOS:

```bash
source venv311/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
TMDB_API_KEY=your_tmdb_api_key
STOCK_API=your_alpha_vantage_api_key
WEATHER_API=your_weatherstack_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Omni-NemoBot
```

### 5. Run

```bash
streamlit run frontend.py
```

Open:

```text
http://localhost:8501
```

## 💬 Example Queries

```text
What are the latest AI developments?
```

```text
What movies are trending today?
```

```text
Tell me about Interstellar.
```

```text
Recommend movies similar to Inception.
```

```text
What's the weather in Mumbai?
```

```text
What is the stock price of AAPL?
```

```text
Convert 100 USD to INR.
```

```text
Calculate 125 * 42.
```

## ☁️ Deployment

The application is deployed on Streamlit Community Cloud:

**https://omni-nemobot.streamlit.app/**

For deployment, store API keys in Streamlit Secrets rather than committing `.env` to the repository.

## 🔒 Security

Never commit API keys or secrets.

Recommended `.gitignore`:

```gitignore
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
venv/
venv311/
```

## 🚀 Future Improvements

- RAG and document Q&A
- PDF/file analysis
- Voice input and output
- Multilingual support
- User authentication
- Cloud database
- Long-term user memory
- Agent evaluation and observability
- Vision/image understanding
- Multi-agent workflows

## 👨‍💻 Author

**Rohan**  
B.Tech CSE (AI & ML), Indian Institute of Information Technology Nagpur

## ⭐ Support

If you find the project useful, consider giving the repository a ⭐.

**GitHub:** https://github.com/rohanrepo123/Nemo-Chatbot
