import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Page configuration
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
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = {}
if 'llm' not in st.session_state:
    st.session_state.llm = None

# Initialize LLM
def initialize_llm():
    if st.session_state.llm is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False, "GEMINI_API_KEY not found in environment"
        
        try:
            st.session_state.llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model="gemini-2.5-flash",
                temperature=0.7
            )
            return True, "API initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize: {str(e)}"
    return True, "API already initialized"

# Extract text from PDF
def extract_pdf_text(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"

# Chunk text
def chunk_text(text, chunk_size=1000, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return splitter.split_text(text)

# Ask question
def ask_question(question, doc_id=None):
    if st.session_state.llm is None:
        return None, "API not initialized. Please check GEMINI_API_KEY."
    
    if not question:
        return None, "Please enter a question"
    
    try:
        # Get content
        if doc_id and doc_id in st.session_state.documents:
            content = st.session_state.documents[doc_id]['content'][:5000]
        else:
            content = "\n\n".join([
                doc['content'][:2000] 
                for doc in st.session_state.documents.values()
            ])
        
        if not content:
            return None, "No documents uploaded. Please upload a PDF first."
        
        # Create prompt
        prompt_template = PromptTemplate(
            input_variables=["content", "question"],
            template="""Based on the following academic content:

{content}

Answer this question comprehensively:
{question}

Provide a clear, educational explanation suitable for students."""
        )
        
        chain = prompt_template | st.session_state.llm
        response = chain.invoke({"content": content, "question": question})
        answer = response.content if hasattr(response, 'content') else str(response)
        return answer, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Get topic explanation
def get_topic_explanation(topic):
    if st.session_state.llm is None:
        return None, "API not initialized. Please check GEMINI_API_KEY."
    
    if not topic:
        return None, "Please enter a topic"
    
    try:
        # Gather content from all documents
        all_content = "\n\n".join([
            doc['content'][:3000] 
            for doc in st.session_state.documents.values()
        ])
        
        if not all_content:
            all_content = "General knowledge"
        
        prompt_template = PromptTemplate(
            input_variables=["content", "topic"],
            template="""Based on the following academic materials:

{content}

Provide a comprehensive explanation of: {topic}

Include:
1. Definition and core concepts
2. Key points and examples (from the materials if available)
3. Common misconceptions
4. Practical applications

Format the response clearly with sections."""
        )
        
        chain = prompt_template | st.session_state.llm
        response = chain.invoke({"content": all_content, "topic": topic})
        explanation = response.content if hasattr(response, 'content') else str(response)
        return explanation, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Header
st.markdown("# 📚 Academic Learning Assistant")
st.markdown("Upload documents, ask questions, and get AI-powered explanations")

# Initialize API
success, msg = initialize_llm()
if success:
    st.sidebar.success("✓ API Initialized")
else:
    st.sidebar.error(f"✗ {msg}")

# Sidebar
with st.sidebar:
    st.header("📋 Documents")
    
    if st.session_state.documents:
        st.subheader("Uploaded Documents:")
        for doc_id, doc in st.session_state.documents.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📄 {doc['filename']}")
                st.caption(f"Chunks: {doc['chunk_count']}")
            with col2:
                if st.button("✕", key=f"del_{doc_id}"):
                    del st.session_state.documents[doc_id]
                    st.rerun()
    else:
        st.info("No documents uploaded yet")

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload", "❓ Ask Questions", "💡 Topic Explanation"])

# Tab 1: Upload
with tab1:
    st.subheader("Upload PDF Document")
    uploaded_file = st.file_uploader("Select a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Upload PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                text, error = extract_pdf_text(uploaded_file)
                
                if error:
                    st.error(error)
                else:
                    chunks = chunk_text(text)
                    doc_id = uploaded_file.name.replace('.pdf', '')
                    
                    st.session_state.documents[doc_id] = {
                        'filename': uploaded_file.name,
                        'content': text,
                        'chunks': chunks,
                        'chunk_count': len(chunks)
                    }
                    
                    st.success(f"✓ Document '{uploaded_file.name}' uploaded successfully!")
                    st.info(f"Split into {len(chunks)} chunks")
                    st.rerun()

# Tab 2: Ask Questions
with tab2:
    st.subheader("Ask a Question")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        question = st.text_area(
            "Your Question",
            placeholder="e.g., What is photosynthesis? Explain the key steps.",
            height=100
        )
    with col2:
        st.write("**Select Document**")
        doc_options = list(st.session_state.documents.keys())
        selected_doc = st.selectbox(
            "Document",
            ["All Documents"] + doc_options,
            label_visibility="collapsed"
        )
    
    if st.button("Get Answer", type="primary", use_container_width=True):
        if not st.session_state.documents:
            st.error("Please upload a document first")
        elif not question:
            st.error("Please enter a question")
        else:
            with st.spinner("Generating answer..."):
                doc_id = selected_doc if selected_doc != "All Documents" else None
                answer, error = ask_question(question, doc_id)
                
                if error:
                    st.error(error)
                else:
                    st.markdown("### Answer")
                    st.markdown(answer)
                    
                    # Copy button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.success("✓ Complete")

# Tab 3: Topic Explanation
with tab3:
    st.subheader("Get Topic Explanation")
    
    topic = st.text_area(
        "Topic Name",
        placeholder="e.g., Photosynthesis, Quantum Computing, Newton's Laws",
        height=80
    )
    
    if st.button("Generate Explanation", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
        else:
            with st.spinner("Generating explanation..."):
                explanation, error = get_topic_explanation(topic)
                
                if error:
                    st.error(error)
                else:
                    st.markdown("### Explanation")
                    st.markdown(explanation)
                    
                    st.success("✓ Explanation generated")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px;">
    <p>Academic Learning Assistant v1.0 | Powered by Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)
