from langchain_openai import ChatOpenAI
from typing import TypedDict,Literal,Annotated 
# from langchain_ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
import requests
from langchain_core.messages import ToolMessage
from langchain_community.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv
import sqlite3
import os 
load_dotenv()
# llm = ChatOpenAI()
llm = ChatOllama(model ='nemotron-3-super:cloud')
llm2 = ChatOllama(model ='nemotron-3-super:cloud',temperature=1)
# llm = ChatOpenAI(model ='gpt-5.4-nano',temperature=.4)
# llm2 = ChatOpenAI(model ='gpt-5.4-nano',temperature=1)

# memory = InMemorySaver()
connection = sqlite3.connect(database='Chatbot.db',check_same_thread=False)

memory = SqliteSaver(conn=connection)

class chat(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary : str | None


search_tool = DuckDuckGoSearchRun(region='us-en')
@tool
def get_weather_data(city: str) -> str:
    """
    Fetches the current weather of a city.
    """
    url = (
        f"https://api.weatherstack.com/current"
        f"?access_key={os.environ['WEATHER_API']}&query={city}"
    )

    response = requests.get(url)

    return response.text
@tool
def calculator(first_num:float,second_num:float,operation:str)-> dict:
    """
    Perform basic arithematic operations like addition, subtraction, multiplication, division.
    Supported operation: add, sub, mul, div
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
                return {"error": "Division by zero is not allowed"}

            result = first_num / second_num

        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result
        }
    except Exception as e:
        return {'error':str(e)}
@tool 
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price of companies 
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={os.environ['STOCK_API']}"
    x = requests.get(url)
    return x.json()

tools = [get_stock_price, search_tool, calculator,get_weather_data]

llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)
def response(state: chat):
    # print('calling response.......')
    messages = state['messages']
    response =llm_with_tools.invoke(messages)
    # print(response.content)
    return {'messages': response}

def generate_summary(state:chat):
    # print('First Execution.....')
    messages = state['messages']
    prompt = "You are a helpful AI bot.Here the user starting a chat you have to create a small title for for new chat thread.her is the user input.\n" \
        f"{messages}"
    summ = llm2.invoke(prompt)
    return {'summary':summ}

def condition_forSum(state):
    if state.get('summary') is not None:
        return END
    return "summary"

work= StateGraph(chat)
work.add_node('response',response)
work.add_node('summary',generate_summary)
work.add_node('tools',tool_node)
work.add_edge(START,'response')
work.add_conditional_edges(
    "response",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

work.add_edge("tools", "response")
work.add_conditional_edges(START,condition_forSum,{'summary':'summary',END:END})
work.add_edge('summary',END)
work.add_edge('response',END)

workflow = work.compile(checkpointer=memory)

def retrieve_allThreads():
    x = set()   
    for i in memory.list(None):
        # print(i.config['configurable']['thread_id'])
        x.add(i.config['configurable']['thread_id'])
    return list(x)
# x = retrieve_allThreads()
# for i in x:
#     print(workflow.get_state(config={'configurable':{'thread_id':i}}))
