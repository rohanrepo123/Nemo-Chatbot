from langchain_openai import ChatOpenAI
from typing import TypedDict,Literal,Annotated
from langchain_ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv
import sqlite3
load_dotenv()
# llm = ChatOpenAI()
llm = ChatOllama(model ='nemotron-3-super:cloud')

# memory = InMemorySaver()
connection = sqlite3.connect(database='Chatbot.db',check_same_thread=False)

memory = SqliteSaver(conn=connection)

class chat(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def response(state: chat):
    print('calling response.......')
    messages = state['messages']
    response = content=llm.invoke(messages)
    return {'messages': response}

work = StateGraph(chat)

work.add_node('response',response)

work.add_edge(START,'response')
work.add_edge('response',END)

workflow = work.compile(checkpointer=memory)

# config = {'configurable':{'thread_id':"2"}}   

# for message_chunk, metadata in workflow.stream({'messages':"Give me a short lyrics of a song"},config=config,stream_mode='messages'):
#     if message_chunk.content:
#         print(message_chunk.content,end='',flush = True)
# resp = workflow.invoke({'messages':"Who is the oldest man alive. Answer byu acknowledge by my name"},config=config)
# print(resp)
def retrieve_allThreads():
    x = set()   
    for i in memory.list(None):
        # print(i.config['configurable']['thread_id'])
        x.add(i.config['configurable']['thread_id'])
    return list(x)