import uuid
from langchain_core.messages import HumanMessage,SystemMessage
import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage
)

from backend import (
    workflow,
    retrieve_allThreads
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ChatGPT",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# AVATARS
# ============================================================

BOT_AVATAR = (
    "https://api.dicebear.com/10.x/"
    "bottts/svg?seed=AI"
)

USER_AVATAR = (
    "https://api.dicebear.com/9.x/"
    "fun-emoji/svg?seed=User"
)


# ============================================================
# THREAD FUNCTIONS
# ============================================================

def generate_thread():
    return str(uuid.uuid4())


def add_thread(thread_id):

    if thread_id not in st.session_state["chat_thread"]:

        st.session_state["chat_thread"].append(
            thread_id
        )


def reset_chat():

    # Create a new temporary thread
    thread_id = generate_thread()

    st.session_state["thread_id"] = thread_id

    # Empty chat
    st.session_state["msg_hstry"] = []


# ============================================================
# LOAD CHAT
# ============================================================

def load_chat(thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = workflow.get_state(config)

    return state.values.get(
        "messages",
        []
    )


# ============================================================
# FIND TITLE
# ============================================================

def find_title(thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = workflow.get_state(config)

    values = state.values

    # --------------------------------------------------------
    # Stored summary
    # --------------------------------------------------------

    summary = values.get("summary")

    if summary:

        return str(summary).strip()


    # --------------------------------------------------------
    # Fallback for old conversations
    # --------------------------------------------------------

    messages = values.get(
        "messages",
        []
    )

    for message in messages:

        if isinstance(
            message,
            HumanMessage
        ):

            text = message.content.strip()

            if len(text) > 30:

                text = text[:30] + "..."

            return text

    return "New Chat"


# ============================================================
# CONVERT DATABASE MESSAGES
# ============================================================

def convert_messages_to_history(
    messages,
    summary=None
):

    temp_message = []

    summary_text = (
        str(summary).strip()
        if summary
        else None
    )

    for message in messages:

        # ====================================================
        # USER MESSAGE
        # ====================================================

        if isinstance(
            message,
            HumanMessage
        ):

            temp_message.append({

                "role": "user",

                "content":
                    message.content

            })


        # ====================================================
        # AI MESSAGE
        # ====================================================

        elif isinstance(
            message,
            AIMessage
        ):

            # Ignore tool-call messages
            if message.tool_calls:

                continue

            # Ignore empty AI messages
            if not message.content:

                continue

            # Ignore old title/summary messages
            if (
                summary_text
                and
                message.content.strip()
                == summary_text
            ):

                continue

            temp_message.append({

                "role": "assistant",

                "content":
                    message.content

            })


        # ====================================================
        # TOOL MESSAGE
        # ====================================================

        elif isinstance(
            message,
            ToolMessage
        ):

            # Don't display raw tool output
            continue


    return temp_message


# ============================================================
# SESSION STATE
# ============================================================

if "msg_hstry" not in st.session_state:

    st.session_state["msg_hstry"] = []


if "thread_id" not in st.session_state:

    st.session_state["thread_id"] = generate_thread()


if "chat_thread" not in st.session_state:

    st.session_state["chat_thread"] = (
        retrieve_allThreads()
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🤖 ChatGPT"
)


# ============================================================
# NEW CHAT
# ============================================================

if st.sidebar.button(
    "➕ New chat",
    use_container_width=True
):

    reset_chat()

    st.rerun()


st.sidebar.header(
    "My Conversations"
)


# ============================================================
# CONVERSATION LIST
# ============================================================

for thread_id in st.session_state["chat_thread"]:

    title = find_title(
        thread_id
    )

    if st.sidebar.button(

        title,

        key=f"thread_{thread_id}",

        use_container_width=True

    ):

        st.session_state["thread_id"] = (
            thread_id
        )

        # -----------------------------------------------
        # Get database state
        # -----------------------------------------------

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        state = workflow.get_state(
            config
        )

        messages = state.values.get(
            "messages",
            []
        )

        summary = state.values.get(
            "summary"
        )

        # -----------------------------------------------
        # Load conversation
        # -----------------------------------------------

        st.session_state[
            "msg_hstry"
        ] = convert_messages_to_history(

            messages,

            summary

        )

        st.rerun()


# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "🤖 My AI Assistant"
)

st.caption(
    "Powered by LangGraph + Nemotron"
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state["msg_hstry"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

ques = st.chat_input(
    "Type your message..."
)


# ============================================================
# PROCESS MESSAGE
# ============================================================

if ques:

    # ========================================================
    # IMPORTANT:
    # ADD THREAD ONLY WHEN USER ACTUALLY SENDS A MESSAGE
    # ========================================================

    current_thread = (
        st.session_state["thread_id"]
    )

    add_thread(
        current_thread
    )


    # ========================================================
    # SAVE USER MESSAGE TO SESSION
    # ========================================================

    st.session_state[
        "msg_hstry"
    ].append({

        "role": "user",

        "content": ques

    })


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message(
        "user"
    ):

        st.markdown(
            ques
        )


    # ========================================================
    # LANGGRAPH CONFIG
    # ========================================================

    CONFIG = {

        "configurable": {

            "thread_id":
                current_thread

        },

        "metadata": {

            "thread_id":
                current_thread

        },

        "run_name":
            "chat_turn"
    }


    # ========================================================
    # ASSISTANT
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        # ----------------------------------------------------
        # Reserve status position BEFORE response
        # ----------------------------------------------------

        status_placeholder = st.empty()

        status_holder = {
            "box": None
        }


        # ====================================================
        # STREAM GENERATOR
        # ====================================================

        def ai_only_stream():

            for message_chunk, metadata in workflow.stream(

                {
                    "messages": [
                        SystemMessage(content="You are a helpful AI assitant powered by some tools use the tools when you thing required." \
                        "Also there is a web search tool 'search_tool' use it when you have no knowledge or not updated with that knowledge" \
                        "It is Aug 2026 when user is using you if there is something between your laswt training date and current date use web search of it" \
                        "like who won fifa 2026, ICC cup 2024,etc"),
                        HumanMessage(content=ques)
                    ]
                },

                config=CONFIG,

                stream_mode="messages"
            ):

                # ====================================================
                # TOOL
                # ====================================================

                if isinstance(
                    message_chunk,
                    ToolMessage
                ):

                    tool_name = getattr(
                        message_chunk,
                        "name",
                        "tool"
                    )

                    if status_holder["box"] is None:

                        with status_placeholder.container():

                            status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}`...",
                                expanded=True
                            )

                    else:

                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}`...",
                            state="running",
                            expanded=True
                        )


                # ====================================================
                # AI
                # ====================================================

                if isinstance(
                    message_chunk,
                    AIMessage
                ):

                    # Ignore tool calls
                    if message_chunk.tool_calls:
                        continue

                    # Ignore empty messages
                    if not message_chunk.content:
                        continue

                    # -----------------------------------------------
                    # IMPORTANT
                    # -----------------------------------------------
                    # Don't display summary/title as chat response
                    # -----------------------------------------------

                    current_title = None

                    try:

                        current_state = workflow.get_state(
                            CONFIG
                        )

                        current_title = (
                            current_state.values.get(
                                "summary"
                            )
                        )

                    except Exception:
                        pass


                    if (
                        current_title
                        and
                        message_chunk.content.strip()
                        == str(current_title).strip()
                    ):

                        continue


                    yield message_chunk.content

        # ====================================================
        # STREAM RESPONSE
        # ====================================================

        ai_message = st.write_stream(
            ai_only_stream()
        )


        # ====================================================
        # COMPLETE TOOL STATUS
        # ====================================================

        if status_holder["box"] is not None:

            status_holder[
                "box"
            ].update(

                label="✅ Tool finished",

                state="complete",

                expanded=False

            )


    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state[
        "msg_hstry"
    ].append({

        "role":
            "assistant",

        "content":
            ai_message

    })
