import streamlit as st
from utils.assistant import Assistant
import uuid
from datetime import datetime
import os

st.set_page_config(page_title="Private Assistant", page_icon="💬", layout="wide")

if "assistant" not in st.session_state:
    st.session_state.assistant = Assistant()

if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    session_id = str(uuid.uuid4())
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {
        "title": "New Chat",
        "messages": []
    }

with st.sidebar:
    # Header
    st.markdown("### Chats")
    
    # New chat button
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("New Chat", use_container_width=True, type="primary", key="new_chat_btn"):
            session_id = str(uuid.uuid4())
            st.session_state.current_session_id = session_id
            st.session_state.sessions[session_id] = {
                "title": "New Chat",
                "messages": []
            }
            st.rerun()
    
    with col2:
        if st.button("Clear Cache", use_container_width=True, type="secondary", help="Clear vector store", key="clear_cache_btn"):
            import shutil
            vector_db_path = st.session_state.assistant.vector_db_path
            if os.path.exists(vector_db_path):
                shutil.rmtree(vector_db_path)
                st.success("Vector store cache cleared!")
                st.rerun()
            else:
                st.info("No cache to clear")
    
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
            # Delete button
            if st.button("✕", key=f"delete_{session_id}", help="Delete chat"):
                if len(st.session_state.sessions) > 1:
                    del st.session_state.sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("Made by [mausneg](https://github.com/mausneg)")

# Main chat area
st.title("Private Assistant")

current_session = st.session_state.sessions[st.session_state.current_session_id]

# Chat messages container
for message in current_session["messages"]:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Fixed input area at the bottom using columns
col1, col2 = st.columns([1, 20])

with col1:
    # Button to trigger file upload
    if st.button("📎", key="add_file_btn", help="Attach files"):
        st.session_state.show_uploader = not st.session_state.get("show_uploader", False)
        st.rerun()

# Show file uploader if button is clicked
if st.session_state.get("show_uploader", False):
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "md", "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls"],
        key=f"uploader_{st.session_state.current_session_id}",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with st.spinner("Uploading file..."):
            st.session_state.assistant.vectorize_document(uploaded_file)
        st.success(f"Document has been uploaded: {uploaded_file.name}")
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
        with st.spinner("Thinking..."):
            response = st.write_stream(st.session_state.assistant.chat(st.session_state.current_session_id, question))
    
    current_session["messages"].append({
        "role": "assistant",
        "content": response
    })
    
    st.rerun()