import streamlit as st
from dotenv import load_dotenv
from utils.model import chat_with_llm, get_session_history
from utils.document_loader import convert_document
import uuid
from datetime import datetime

load_dotenv(".env")

st.set_page_config(page_title="Private Chatbot", page_icon="💬", layout="wide")

if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    session_id = str(uuid.uuid4())
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {
        "title": "New Chat",
        "messages": [],
        "context": ""
    }

with st.sidebar:
    # Header
    st.markdown("### Chats")
    
    # New chat button
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        session_id = str(uuid.uuid4())
        st.session_state.current_session_id = session_id
        st.session_state.sessions[session_id] = {
            "title": "New Chat",
            "messages": [],
            "context": ""
        }
        st.rerun()
    
    st.markdown("---")
    
    # Display session history (ChatGPT style - clean list without extra columns)
    for session_id in reversed(list(st.session_state.sessions.keys())):
        session = st.session_state.sessions[session_id]
        
        # Create a container for hover effect
        col1, col2 = st.columns([6, 1])
        
        with col1:
            # Session button - clean text only
            if st.button(
                session['title'][:35],
                key=f"session_{session_id}",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.current_session_id = session_id
                st.rerun()
        
        with col2:
            # Delete button - only show on hover (simulated with smaller button)
            if st.button("×", key=f"delete_{session_id}", help="Delete"):
                if len(st.session_state.sessions) > 1:
                    del st.session_state.sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("Made by [mausneg](https://github.com/mausneg)")

# Main chat area
st.title("Private Chatbot")

current_session = st.session_state.sessions[st.session_state.current_session_id]

# Chat messages container
for message in current_session["messages"]:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Fixed input area at the bottom using columns
col1, col2 = st.columns([1, 20])

with col1:
    # Button to trigger file upload - positioned above chat input
    if st.button("➕", help="Add photos & files", key="add_file_btn"):
        st.session_state.show_uploader = not st.session_state.get("show_uploader", False)

# Show file uploader if button is clicked
if st.session_state.get("show_uploader", False):
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "md", "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls"],
        key=f"uploader_{st.session_state.current_session_id}",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with st.spinner("Processing file..."):
            st.session_state.sessions[st.session_state.current_session_id]["context"] = convert_document(uploaded_file)
        st.success(f"✓ {uploaded_file.name}")
        st.session_state.show_uploader = False

# Chat input - always at the bottom
question = st.chat_input("Ask anything...")

if question:
    if not current_session["messages"]:
        current_session["title"] = question[:50]
    
    current_session["messages"].append({
        "role": "user",
        "content": question
    })
    
    with st.chat_message("user"):
        st.markdown(question)
    
    with st.chat_message("assistant"):
        context = current_session.get("context", "")
        response = st.write_stream(chat_with_llm(st.session_state.current_session_id, context, question))
    
    current_session["messages"].append({
        "role": "assistant",
        "content": response
    })