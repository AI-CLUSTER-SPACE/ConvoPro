import streamlit as st

from db.conversation import get_all_conversations, get_conversation, create_new_conversation, add_message
from services.chat_utilities import get_answer
from services.get_model_lists import get_ollama_model_lists
from services.get_title import get_chat_title

st.set_page_config(
    page_title="ConvoPRO",
    page_icon="🤖",
    layout="centered"
)
st.title("🦸‍ SpeedY ConvoPRO GPT")


# -----MODELS -----
if "OLLAMA_MODELS" not in st.session_state:
    st.session_state.OLLAMA_MODELS = get_ollama_model_lists()

selected_model = st.selectbox("Select Model",st.session_state.OLLAMA_MODELS)

#------Session State------------
st.session_state.setdefault("conversation_id",None)
st.session_state.setdefault("conversation_title",None)
st.session_state.setdefault("chat_history",[])  #{role , content}


#------ SideBar: Conversation ------
with st.sidebar:
    st.button("💬 Chat History")
    conversations = get_all_conversations()    #{ conversation_id : title }

    if st.button("➕ New Chat"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = None
        st.session_state.chat_history = []

    for cid,title in conversations.items():
        is_current = cid == st.session_state.conversation_id
        label = f"🟣 {title}" if is_current else title
        if st.button(label,key=f"conv_{cid}"):
            doc = get_conversation(cid) or {}
            st.session_state.conversation_id = cid
            st.session_state.conversation_title = doc.get("title", "untitled")
            st.session_state.chat_history = [
                {"role": m['role'],"content":m['content']} for m in doc.get("messages",[])
            ]


#----show chats soo far---------
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])


#------chat Input -------------
user_query = st.chat_input("Ask SpeedY ConvoPRO GPT.......")
if user_query:
    # 1. show + store user message in UI
    st.chat_message("user").markdown(user_query)
    st.session_state.chat_history.append({"role":"user","content":user_query})

    #2. Persist DB (create convo on first message else append
    if st.session_state.conversation_id is None:
        try:
            title = get_chat_title(selected_model,user_query) or "NewChat"
        except Exception:
            title = "NewChat"
        conv_id = create_new_conversation(title=title,role="user",content=user_query)
        st.session_state.conversation_id = conv_id
        st.session_state.conversation_title = title
    else:
        add_message(st.session_state.conversation_id,"user",user_query)


    # 3. Get assistant response (direct service)
    try:
        assistant_text = get_answer(selected_model,st.session_state.chat_history)
    except Exception as e:
        assistant_text = f"Error getting response: {e}"

    # 4. Show + store assistant message
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
    st.session_state.chat_history.append({"role":"assistant","content":assistant_text})

    #5. Persist assistant message to DB
    if st.session_state.conversation_id:
        add_message(st.session_state.conversation_id,"assistant",assistant_text)