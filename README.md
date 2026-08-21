# 🤖 Omni-NemoBot

**Omni-NemoBot** is a full-fledged AI chatbot built using **LangGraph**, **LangChain**, **OpenAI GPT-5.4 Nano**, and **Streamlit**. It supports real-time streaming responses, persistent conversation memory, intelligent tool calling, and automatic conversation title generation.

## 🌐 Live Demo

🚀 **Try it here:** https://omni-nemobot.streamlit.app/

---

## ✨ Features

- 💬 Natural multi-turn conversations
- ⚡ Real-time token streaming
- 🧠 Persistent chat memory using SQLite
- 🏷️ Automatic conversation title generation
- 🔄 Multiple chat threads
- 🔍 Internet search using DuckDuckGo
- 🌦️ Live weather information
- 📈 Live stock price lookup
- 🧮 Built-in calculator
- 🛠️ Tool execution status indicator
- 🎨 Modern Streamlit interface

---

## 🏗️ Architecture

```
                  User
                    │
                    ▼
            Streamlit Frontend
                    │
                    ▼
              LangGraph Agent
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
 DuckDuckGo    Calculator    Weather API
     │
     ▼
 Stock API

                    │
                    ▼
          GPT-5.4 Nano (OpenAI)
                    │
                    ▼
         SQLite Checkpoint Memory
```

---

## 🧠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Streamlit | Web UI |
| LangGraph | Agent Workflow |
| LangChain | LLM Orchestration |
| OpenAI GPT-5.4 Nano | Language Model |
| SQLite | Persistent Memory |
| DuckDuckGo Search | Web Search |
| Alpha Vantage API | Stock Prices |
| WeatherStack API | Weather Information |

---

## 🛠️ Tools

### 🔍 DuckDuckGo Search

Searches the web for current information.

Example:

```
Latest AI news
```

---

### 🌦️ Weather Tool

Returns the latest weather of any city.

Example:

```
Weather in Mumbai
```

---

### 📈 Stock Price Tool

Fetches current stock market data.

Example:

```
Apple stock price
Tesla stock
```

---

### 🧮 Calculator

Performs arithmetic operations.

Supports:

- Addition
- Subtraction
- Multiplication
- Division

Example:

```
Calculate 45 * 27
```

---

## 💡 Conversation Memory

Every chat is stored in **SQLite** using LangGraph Checkpoints.

Features:

- Resume previous chats
- Multiple chat threads
- Persistent history
- Automatic thread titles

---

## ⚡ Streaming Responses

Responses are streamed token-by-token for a ChatGPT-like experience.

Additionally, whenever the assistant invokes a tool, the UI displays a live status such as:

```
🔧 Using DuckDuckGo...

🔧 Using Calculator...

🔧 Using Weather Tool...

✅ Tool Finished
```

---

## 📂 Project Structure

```
.
├── backend.py
├── frontend.py
├── Chatbot.db
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Omni-NemoBot.git
```

Move inside the project

```bash
cd Omni-NemoBot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
OPENAI_API_KEY=your_openai_key

STOCK_API=your_alpha_vantage_key

WEATHER_API=your_weatherstack_key

LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Omni-NemoBot
```

Run the application

```bash
streamlit run frontend.py
```

---

## 📸 Screenshots

### Chat Interface

<img width="900" alt="Omni-NemoBot" src="assets/chat.png">

---

## Future Improvements

- 📄 PDF Question Answering
- 🧠 RAG Support
- 📁 File Upload
- 🎤 Voice Chat
- 🌍 Multi-language Support
- 👥 User Authentication
- ☁️ Cloud Database
- 📊 Conversation Analytics

---

## 👨‍💻 Author

**Rohan**

B.Tech CSE (AI & ML)

Indian Institute of Information Technology Nagpur

---

## ⭐ If you found this project useful

Please consider giving the repository a ⭐ on GitHub.

It helps others discover the project and motivates further development.
