# Import Streamlit for web interface and other required modules
import streamlit as st
import os
import uuid
import shutil
import sys

# Add the parent directory to Python path so we can import our agents
# This allows us to import from main/, agents/, etc. folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.coordinator import Coordinator

# Create necessary directories for file storage
UPLOAD_DIR = "uploaded_docs"    # Where user uploads are stored
EXTRACT_DIR = "extracted_data"  # Where processed text/images are stored
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# Configure Streamlit page settings
st.set_page_config(page_title="Agentic RAG Chatbot", layout="wide")

# Initialize the coordinator (our main orchestrator)
coordinator = Coordinator()

# Initialize session state variables to persist data across page reloads
# Session state keeps data alive while user interacts with the app
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = None    # Track current file
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []       # Store Q&A history
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0     # Count total questions

# Create sidebar for system status and statistics
with st.sidebar:
    st.markdown("### 📊 System Status")
    
    # Current Document Section
    st.markdown("#### 📄 Current document:")
    if st.session_state.file_uploaded:
        # Show current document with a nice background
        st.success(f"📋 {st.session_state.file_uploaded}")
    else:
        st.info("No document uploaded")
    
    st.markdown("---")  # Separator line
    
    # Statistics Section
    st.markdown("#### 📈 Statistics")
    
    # Questions Asked Counter
    st.markdown("**Questions Asked**")
    st.markdown(f"### {st.session_state.questions_asked}")  
    # Clear Chat History Button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.questions_asked = 0
        st.success("Chat history cleared!")
        st.rerun()  # Refresh the page to update display
    # Show memory usage info
    st.markdown("---")
    st.markdown("#### 💾 Memory Info")
    if st.session_state.chat_history:
        total_chars = sum(len(msg["question"]) + len(msg["answer"]) for msg in st.session_state.chat_history)
        st.metric("Characters in Memory", f"{total_chars:,}")
    else:
        st.info("No data in memory")

# Main content area
st.title("🤖RAG Chatbot - Multi-Format Document QA")

# File uploader widget - allows users to upload various document types
uploaded_file = st.file_uploader(
    "📂 Upload your document", 
    type=["pdf", "docx", "pptx", "csv", "xlsx", "txt", "jpg", "png", "jpeg"]
)

# Handle file upload
if uploaded_file:
    # Save uploaded file to disk so our agents can process it
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Write file bytes to disk

    # Extract file extension for processing (remove the dot)
    ext = os.path.splitext(file_path)[-1].lower().replace(".", "")
    
    # Generate unique trace ID for this session
    trace_id = str(uuid.uuid4())

    # Clean up old extracted data to avoid confusion
    for f in os.listdir(EXTRACT_DIR):
        os.remove(os.path.join(EXTRACT_DIR, f))

    # Reset chat history if user uploads a new file
    if st.session_state.file_uploaded != uploaded_file.name:
        st.session_state.file_uploaded = uploaded_file.name
        st.session_state.chat_history = []   # Clear old conversations
        st.session_state.questions_asked = 0  # Reset question counter
        st.success(f"✅ Uploaded `{uploaded_file.name}` successfully!")

    # Chat input box for user questions
    question = st.chat_input("❓ Ask a question about the uploaded document")

    # Process user question when submitted
    if question:
        # Show loading spinner while processing
        with st.spinner("🔍 Thinking..."):
            # Send question through the entire RAG pipeline
            result = coordinator.handle_user_query(file_path, ext, question, trace_id)
            
            # Update statistics
            st.session_state.questions_asked += 1

            # Add Q&A to session history for display
            st.session_state.chat_history.append({
                "question": question,
                "answer": result.payload["answer"],
                "sources": result.payload["sources"]  # Context chunks used
            })

# Display chat history in a conversational format
if st.session_state.chat_history:
    st.markdown("### 💬 Chat History")
    
    for idx, msg in enumerate(st.session_state.chat_history):
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"**You:** {msg['question']}")
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(f"**Answer:** {msg['answer']}")
            
            # Show expandable section with source context
            with st.expander("📚 Context Used"):
                # Display each context chunk that was used to generate the answer
                for i, chunk in enumerate(msg["sources"], 1):
                    st.markdown(f"**Chunk {i}:** {chunk}")
else:
    # Show welcome message when no chat history
    st.info("👋 Upload a document and start asking questions to see the conversation here!")

# Add personal branding in top-left corner
st.markdown(
    """
    <style>
    .top-right-box {
        position: fixed;        /* Stay in same position when scrolling */
        top: 10px;             /* 10px from top */
        right: 15px;            /* 15px from left */
        z-index: 100;          /* Appear above other elements */
        padding: 6px 12px;     /* Internal spacing */
        border-radius: 6px;    /* Rounded corners */
        font-size: 13px;       /* Small text size */
    }
    </style>
    <div class="top-left-box">
        <strong>Dhowfeek Hasan</strong><br>
        🔗<a href="https://www.linkedin.com/in/dhowfeek-hasan/" target="_blank">LinkedIn Profile</a>
    </div>
    """,
    unsafe_allow_html=True  # Allow custom HTML/CSS
)
