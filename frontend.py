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
st.write("Hey Pal You can talk to me My creator and God is Rohan")

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
        st.markdown(message['content'])
        # st.text(message['content']) use markdown for prettier format

ques = st.chat_input("Type it:")

# Just need to add st.write_stream

if ques:
    # Show user's message
    st.session_state["msg_hstry"].append({"role": "user", "content":ques })
    with st.chat_message("user"):
        st.text(ques)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=ques)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["msg_hstry"].append(
        {"role": "assistant", "content": ai_message}
    )
