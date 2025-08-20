import streamlit as st
import os
import uuid
import shutil
import sys

# Add root directory to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.coordinator import Coordinator

# Setup folders
UPLOAD_DIR = "uploaded_docs"
EXTRACT_DIR = "extracted_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# Title
st.set_page_config(page_title="Agentic RAG Chatbot", layout="wide")
st.title("🤖 RAG Chatbot - Multi-Format Document QA")

# Initialize Coordinator
coordinator = Coordinator()

# Clear chat session state on file upload
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File uploader
uploaded_file = st.file_uploader("📂 Upload your document", type=["pdf", "docx", "pptx", "csv", "xlsx", "txt", "jpg", "png", "jpeg"])

if uploaded_file:
    # Save file
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    ext = os.path.splitext(file_path)[-1].lower().replace(".", "")
    trace_id = str(uuid.uuid4())

    # Clear previous extracted text
    for f in os.listdir(EXTRACT_DIR):
        os.remove(os.path.join(EXTRACT_DIR, f))

    # Reset chat if new file uploaded
    if st.session_state.file_uploaded != uploaded_file.name:
        st.session_state.file_uploaded = uploaded_file.name
        st.session_state.chat_history = []
        st.success(f"✅ Uploaded `{uploaded_file.name}` successfully!")

    # Input box for question
    question = st.chat_input("❓ Ask a question about the uploaded document")

    if question:
        with st.spinner("🔍 Thinking..."):
            result = coordinator.handle_user_query(file_path, ext, question, trace_id)

            # Save Q&A to history
            st.session_state.chat_history.append({
                "question": question,
                "answer": result.payload["answer"],
                "sources": result.payload["sources"]
            })

# Display chat history
for idx, msg in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(f"**You:** {msg['question']}")
    with st.chat_message("assistant"):
        st.markdown(f"**Answer:** {msg['answer']}")
        with st.expander("📚 Context Used"):
            for i, chunk in enumerate(msg["sources"], 1):
                st.markdown(f"**Chunk {i}:** {chunk}")


import streamlit as st

# 💼 Personal Info (top-left above title)
st.markdown(
    """
    <style>
    .top-left-box {
        position: fixed;
        top: 10px;
        left: 15px;
        z-index: 100;
        
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        
    }
    </style>
    <div class="top-left-box">
        <strong>Dhowfeek Hasan</strong><br>
        🔗<a href="https://www.linkedin.com/in/dhowfeek-hasan/" target="_blank">LinkedIn Profile</a>
    </div>
    """,
    unsafe_allow_html=True
)
