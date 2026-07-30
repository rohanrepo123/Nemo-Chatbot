import streamlit as st
from backend import * 
import uuid

# msg_hstry =[]
# USER_AVATAR = "https://api.dicebear.com/10.x/adventurer/svg?seed=Rohan"

BOT_AVATAR = "https://api.dicebear.com/10.x/bottts/svg?seed=AI"
USER_AVATAR = "https://api.dicebear.com/9.x/fun-emoji/svg?seed=User"
#******************************** Utility functions**************************************#

def generate_thread():
    thread_id = uuid.uuid4()
    return thread_id
# print(generate_thread())

def reset_chat():
    thread_id = generate_thread()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['msg_hstry'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_chat(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    # try:
    state = workflow.get_state(config)
    # print(thread_id)
    return state.values.get('messages',[])

def find_title(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state = workflow.get_state(config)
    if len(state.values):
        return state[0]['summary'].content
    else:
        return "New Chat"
    # return message

if 'msg_hstry' not in st.session_state:
    st.session_state['msg_hstry'] = [] 

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread()

# if 'chat_thread' not in st.session_state:
#     st.session_state['chat_thread'] = []
# Now we have database
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_allThreads()
    # print(retrieve_allThreads)

add_thread(st.session_state['thread_id'])

st.sidebar.title("ChatGpt")
if st.sidebar.button("New chat"):
    reset_chat()

st.sidebar.header("My Conversations")
st.write("Hey there")

for thread_id in st.session_state['chat_thread']:
    if st.sidebar.button(str(find_title(thread_id))):
        st.session_state['thread_id'] = thread_id
        message = load_chat(thread_id)
        temp_message = []
        for msg in message:
            if isinstance(msg,HumanMessage):
                role='user'
            else:
                role = 'assistant'
            temp_message.append({'role':role,'content':msg.content})
        st.session_state['msg_hstry'] = temp_message
#loading history shown

for message in st.session_state['msg_hstry']:
    with st.chat_message(message['role']):
        st.text(message['content'])

ques = st.chat_input("Type it:")

# Just need to add st.write_stream

if ques:
    # ques = str(input("You: \n"))
    st.session_state['msg_hstry'] .append({'role':'user','content':ques})
    with st.chat_message('user',avatar=USER_AVATAR):
        st.write(ques)
        st.snow()
    config = {'configurable':{'thread_id':st.session_state['thread_id']}}
    with st.status("Thinking...", expanded=True) as status:
        # continue
    # with st.status("Thinking...", expanded=True) as status:
        # st.write("Sending request to LLM...")
        with st.chat_message('assistant'):
            ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata in workflow.stream({'messages': [HumanMessage(content=ques)]}, config=config,stream_mode='messages')
            )  #needs a generator to pass
    st.balloons()
    st.session_state['msg_hstry'] .append({'role':'assistant','content':ai_message})
    st.rerun()         #rerun to show output

