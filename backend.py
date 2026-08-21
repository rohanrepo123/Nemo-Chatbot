from typing import TypedDict, Annotated
import sqlite3
import os
import requests
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
)
from langchain_core.tools import tool

from langchain_community.tools import DuckDuckGoSearchRun

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END, add_messages


load_dotenv()


# ============================================================
# LLM
# ============================================================

# llm = ChatOllama(
#     model="nemotron-3-super:cloud"
# )

# llm2 = ChatOllama(
#     model="nemotron-3-super:cloud",
#     temperature=1
# )
llm = ChatOpenRouter(
    model="nemotron-nano-9b-v2:free",
    api_key=os.environ['OPENROUTER_API_KEY']
)

llm2 = ChatOpenAI(
    model="gpt-5-nano",
    temperature=1,
)


# ============================================================
# DATABASE / MEMORY
# ============================================================

connection = sqlite3.connect(
    database="Chatbot.db",
    check_same_thread=False
)

memory = SqliteSaver(conn=connection)


# ============================================================
# STATE
# ============================================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary: str | None


# ============================================================
# TOOLS
# ============================================================

search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def get_weather_data(city: str) -> str:
    """
    Fetches the current weather of a city.
    """

    url = (
        f"https://api.weatherstack.com/current"
        f"?access_key={os.environ['WEATHER_API']}"
        f"&query={city}"
    )

    response = requests.get(url)

    return response.text


@tool
def calculator(
    first_num: float,
    second_num: float,
    operation: str
) -> dict:
    """
    Perform basic arithmetic operations.

    Supported operations:
    add, sub, mul, div
    """

    try:

        if operation == "add":
            result = first_num + second_num

        elif operation == "sub":
            result = first_num - second_num

        elif operation == "mul":
            result = first_num * second_num

        elif operation == "div":

            if second_num == 0:
                return {
                    "error": "Division by zero is not allowed"
                }

            result = first_num / second_num

        else:
            return {
                "error": f"Unsupported operation '{operation}'"
            }

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price of a company.
    """

    url = (
        "https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY"
        f"&symbol={symbol}"
        f"&apikey={os.environ['STOCK_API']}"
    )

    response = requests.get(url)

    return response.json()


# ============================================================
# TOOL LIST
# ============================================================

tools = [
    get_stock_price,
    search_tool,
    calculator,
    get_weather_data
]


llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)


# ============================================================
# RESPONSE NODE
# ============================================================

def response(state: ChatState):

    messages = state["messages"]

    response_message = llm_with_tools.invoke(messages)

    return {
        "messages": response_message
    }


# ============================================================
# SUMMARY NODE
# ============================================================

def generate_summary(state: ChatState):

    messages = state["messages"]

    for message in messages:

        if isinstance(message, HumanMessage):

            prompt = (
                "Create a short title for this conversation "
                "based on the user's message. "
                "Return ONLY the title, nothing else.\n\n"
                f"User message: {message.content}"
            )

            result = llm2.invoke(prompt)

            return {
                "summary": result.content.strip()
            }

    return {
        "summary": "New Chat"
    }


# ============================================================
# SUMMARY CONDITION
# ============================================================

def condition_for_summary(state: ChatState):

    if state.get("summary"):
        return "response"

    return "summary"

# ============================================================
# GRAPH
# ============================================================

work = StateGraph(ChatState)

work.add_node(
    "response",
    response
)

work.add_node(
    "summary",
    generate_summary
)

work.add_node(
    "tools",
    tool_node
)


# START
work.add_conditional_edges(
    START,
    condition_for_summary,
    {
        "summary": "summary",
        "response": "response"
    }
)


# Summary → Response
work.add_edge(
    "summary",
    "response"
)


# Response → Tool / END
work.add_conditional_edges(
    "response",
    tools_condition,
    {
        "tools": "tools",
        END: END
    }
)


# Tool → Response
work.add_edge(
    "tools",
    "response"
)


workflow = work.compile(
    checkpointer=memory
)


# ============================================================
# RETRIEVE ALL THREADS
# ============================================================

def retrieve_allThreads():

    threads = set()

    for checkpoint in memory.list(None):

        thread_id = (
            checkpoint.config
            .get("configurable", {})
            .get("thread_id")
        )

        if thread_id:
            threads.add(thread_id)

    return list(threads)
