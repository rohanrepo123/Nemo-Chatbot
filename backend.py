from typing import TypedDict, Annotated
import sqlite3
import os
import requests
from langchain_openrouter import ChatOpenRouter
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

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
from langgraph.types import interrupt


load_dotenv()


# ============================================================
# LLM
# ============================================================

llm = ChatOpenRouter(
    model="nemotron-nano-9b-v2:free",
    api_key=os.environ['OPENROUTER_API_KEY']
)
# llm = ChatOllama(
#     model="nemotron-3-super:cloud",
# )

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
# TMDB
# ============================================================

TMDB_API_KEY = os.environ["TMDB_API_KEY"]


# TMDB genre IDs
genre_id = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "fantasy": 14,
    "history": 36,
    "horror": 27,
    "music": 10402,
    "mystery": 9648,
    "romance": 10749,
    "science fiction": 878,
    "scifi": 878,
    "tv movie": 10770,
    "thriller": 53,
    "war": 10752,
    "western": 37
}


# ============================================================
# DUCKDUCKGO SEARCH
# ============================================================

search_tool = TavilySearch(
    max_results=5,
    topic="general"
)


# ============================================================
# CALCULATOR
# ============================================================

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


# ============================================================
# CURRENCY CONVERSION
# ============================================================

@tool
def currency_conversion(
    from_currency: str,
    to_currency: str
) -> float:
    """
    Get the current currency conversion rate between two currencies.

    Example:
    USD to INR
    EUR to USD
    """

    url = (
        "https://v6.exchangerate-api.com/v6/"f"{os.environ['EXCHANGE_RATE_API']}/pair/"f"{from_currency.upper()}/"f"{to_currency.upper()}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data.get("result") != "success":
        return {
            "error": data
        }

    return data["conversion_rate"]


# ============================================================
# CURRENCY AMOUNT CONVERSION
# ============================================================

@tool
def conversion_amount(
    base_currency_value: float,
    conversion_rate: float
) -> float:
    """
    Convert an amount using a currency conversion rate.

    Always use this tool after obtaining a conversion rate.
    """

    return (
        base_currency_value *
        conversion_rate
    )


# ============================================================
# STOCK PRICE
# ============================================================

@tool
def get_stock_price(
    symbol: str
) -> dict:
    """
    Fetch the latest available daily stock information
    for a company using its stock symbol.
    """

    url = (
        "https://www.alphavantage.co/query"
        "?function=TIME_SERIES_DAILY"
        f"&symbol={symbol.upper()}"
        f"&apikey={os.environ['STOCK_API']}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MOVIE DETAILS
# ============================================================

@tool
def movie_details(
    movie: str
) -> dict:
    """
    Retrieve detailed information about a movie.

    Use this when the user asks about a specific movie,
    including release date, overview, genres, rating,
    popularity, runtime, language, poster, etc.
    """

    url = (
        "https://api.themoviedb.org/3/search/movie"
    )

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# CELEBRITY DETAILS
# ============================================================

@tool
def celebrities_details(
    celebrity: str
) -> dict:
    """
    Retrieve information about a celebrity, actor,
    actress, director, or other film-industry personality.
    """

    url = (
        "https://api.themoviedb.org/3/search/person"
    )

    params = {
        "api_key": TMDB_API_KEY,
        "query": celebrity
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MOVIE RECOMMENDATIONS
# ============================================================

@tool
def movies_recommendation(
    movie_id: int
) -> dict:
    """
    Get movies recommended by TMDB based on a movie ID.

    Use this for similar-movie recommendations.
    """

    url = (
        f"https://api.themoviedb.org/3/movie/"
        f"{movie_id}/recommendations"
    )

    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# POPULAR MOVIES
# ============================================================

@tool
def popular_movies() -> dict:
    """
    Retrieve currently popular movies from TMDB.
    """

    url = (
        "https://api.themoviedb.org/3/movie/popular"
    )

    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# TRENDING MOVIES
# ============================================================

@tool
def trending_movies(time_window: str = "day") -> dict:
    """
    Retrieve the current trending movies from TMDB.

    Use this tool when the user asks for trending movies, movies that are
    currently popular, or the hottest films right now.

    Args:
        time_window (str): The trending period. Accepted values are:
            - "day": Trending today (default)
            - "week": Trending this week

    Returns:
        dict: A TMDB response containing a list of trending movies with
        details such as title, overview, release date, ratings, popularity,
        and poster paths.
    """
    url = f"https://api.themoviedb.org/3/trending/movie/{time_window}"

    params = {
        "api_key": os.environ['TMDB_API_KEY']
    }

    return requests.get(url, params=params).json()


# ============================================================
# GENRE-BASED MOVIES
# ============================================================

@tool
def genre_based_movies_recommendation(
    genre: str
) -> dict:
    """
    Retrieve popular movies belonging to a specified genre.

    Supported genres include:
    action, adventure, animation, comedy, crime,
    documentary, drama, family, fantasy, history,
    horror, music, mystery, romance, science fiction,
    thriller, war and western.
    """

    genre_name = genre.lower().strip()

    genre_id_temp = genre_id.get(
        genre_name
    )

    if genre_id_temp is None:

        return {
            "error":
                f"Unsupported genre '{genre}'.",

            "supported_genres":
                list(genre_id.keys())
        }

    url = (
        "https://api.themoviedb.org/3/discover/movie"
    )

    params = {
        "api_key": TMDB_API_KEY,

        "with_genres":
            genre_id_temp,

        "sort_by":
            "popularity.desc"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# WEATHER
# ============================================================

@tool
def get_weather_data(
    city: str
) -> str:
    """
    Fetch the current weather of a city.
    """

    url = (
        "https://api.weatherstack.com/current"
        f"?access_key={os.environ['WEATHER_API']}"
        f"&query={city}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.text


# ============================================================
# PURCHASE STOCK
# ============================================================
#
#This tool is not used in this bot
@tool
def purchase_stock(
    symbol: str,
    quantity: int
) -> dict:
    """
    Simulate purchasing a quantity of a stock.

    This tool requires human approval before confirming
    the purchase.
    """

    if quantity <= 0:

        return {
            "status": "error",
            "message":
                "Quantity must be greater than zero."
        }

    decision = interrupt(
        f"Approve buying {quantity} shares "
        f"of {symbol.upper()}? (yes/no)"
    )

    if (
        isinstance(decision, str)
        and
        decision.lower().strip() == "yes"
    ):

        return {

            "status": "success",

            "message":
                f"Purchase order placed for "
                f"{quantity} shares of "
                f"{symbol.upper()}.",

            "symbol":
                symbol.upper(),

            "quantity":
                quantity
        }

    return {

        "status": "cancelled",

        "message":
            f"Purchase of {quantity} shares "
            f"of {symbol.upper()} was declined "
            f"by human.",

        "symbol":
            symbol.upper(),

        "quantity":
            quantity
    }


# ============================================================
# TOOL LIST
# ============================================================
#
# purchase_stock is deliberately excluded — see note above.
# ============================================================

tools = [
    get_stock_price,
    search_tool,
    calculator,
    get_weather_data,
    currency_conversion,
    conversion_amount,
    movie_details,
    celebrities_details,
    movies_recommendation,
    popular_movies,
    trending_movies,
    genre_based_movies_recommendation,
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
