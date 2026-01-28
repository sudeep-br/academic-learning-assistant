import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../backend/.env")

# Page config
st.set_page_config(
    page_title="Academic Learning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .stTabs [role="tab"] {
        font-size: 18px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

API_BASE = "http://localhost:5000"

# Initialize session state
if "documents" not in st.session_state:
    st.session_state.documents = []
if "response" not in st.session_state:
    st.session_state.response = None

# Header
st.markdown("# 📚 Academic Learning Assistant")
st.markdown("Upload documents, ask questions, and get AI-powered explanations using Google Gemini")

# Check API status
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY not found in environment")
    st.info("Please set the GEMINI_API_KEY in the backend/.env file")
    st.stop()

# Create tabs
tab1, tab2, tab3 = st.tabs(["📄 Upload", "❓ Ask Questions", "💡 Topic Explanation"])

# ============ TAB 1: UPLOAD ============
with tab1:
    st.subheader("Upload PDF Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Select a PDF file", type="pdf")
    
    with col2:
        if uploaded_file is not None:
            if st.button("📤 Upload PDF", use_container_width=True):
                with st.spinner("Uploading..."):
                    try:
                        files = {"file": uploaded_file}
                        response = requests.post(f"{API_BASE}/upload", files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                st.success(f"✓ {data.get('message')}")
                                # Refresh documents list
                                st.rerun()
                            else:
                                st.error(f"Error: {data.get('error')}")
                        else:
                            st.error(f"Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # List uploaded documents
    st.subheader("Uploaded Documents")
    try:
        response = requests.get(f"{API_BASE}/documents")
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            
            if documents:
                for doc in documents:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.text(f"📄 {doc['filename']}")
                        with col2:
                            st.caption(f"{doc['chunks']} chunks")
            else:
                st.info("No documents uploaded yet")
    except Exception as e:
        st.warning(f"Could not load documents: {str(e)}")

# ============ TAB 2: ASK QUESTIONS ============
with tab2:
    st.subheader("Ask Questions About Your Documents")
    
    # Get documents for dropdown
    try:
        response = requests.get(f"{API_BASE}/documents")
        documents = response.json().get("documents", []) if response.status_code == 200 else []
        doc_options = ["All Documents"] + [doc["filename"] for doc in documents]
        doc_ids = [""] + [doc["doc_id"] for doc in documents]
    except:
        doc_options = ["All Documents"]
        doc_ids = [""]
    
    # Question input
    question = st.text_area(
        "Your Question",
        placeholder="e.g., What is photosynthesis? Explain the main concepts...",
        height=120
    )
    
    # Document selector
    selected_doc = st.selectbox(
        "Select Document (optional)",
        options=doc_options,
        index=0
    )
    
    doc_id = doc_ids[doc_options.index(selected_doc)] if selected_doc in doc_options else ""
    
    if st.button("🔍 Get Answer", use_container_width=True):
        if not question:
            st.error("Please enter a question")
        else:
            with st.spinner("Generating answer..."):
                try:
                    payload = {
                        "question": question,
                        "doc_id": doc_id if doc_id else None
                    }
                    response = requests.post(f"{API_BASE}/ask", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            st.session_state.response = data.get("answer")
                            st.success("✓ Answer generated!")
                        else:
                            st.error(f"Error: {data.get('error')}")
                    else:
                        st.error(f"Request failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display response
    if st.session_state.response:
        st.divider()
        st.subheader("Response")
        st.markdown(st.session_state.response)

# ============ TAB 3: TOPIC EXPLANATION ============
with tab3:
    st.subheader("Get Topic Explanation")
    
    topic = st.text_area(
        "Topic Name",
        placeholder="e.g., Photosynthesis, Quantum Computing, Machine Learning...",
        height=100
    )
    
    if st.button("📖 Get Explanation", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
        else:
            with st.spinner("Generating explanation..."):
                try:
                    payload = {"topic": topic}
                    response = requests.post(f"{API_BASE}/topic-explanation", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            st.session_state.response = data.get("explanation")
                            st.success("✓ Explanation generated!")
                        else:
                            st.error(f"Error: {data.get('error')}")
                    else:
                        st.error(f"Request failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display response
    if st.session_state.response:
        st.divider()
        st.subheader("Explanation")
        st.markdown(st.session_state.response)

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px; margin-top: 2rem;">
    Academic Learning Assistant v1.0 | Powered by Google Gemini AI<br>
    <a href="https://aistudio.google.com" target="_blank">Google AI Studio</a> | 
    <a href="https://streamlit.io" target="_blank">Streamlit</a>
    </div>
    """,
    unsafe_allow_html=True
)
