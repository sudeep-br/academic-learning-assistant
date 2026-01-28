from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import PyPDF2
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Store uploaded documents in memory
documents = {}
llm = None

# Initialize LLM on startup with API key from environment
def startup_llm():
    """Initialize LLM with API key from environment variable"""
    global llm
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("WARNING: GEMINI_API_KEY environment variable not set")
        print("Please set it using: set GEMINI_API_KEY=your_api_key")
        return False
    
    try:
        llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model="gemini-2.5-flash",
            temperature=0.7
        )
        print("✓ Gemini API initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize Gemini: {str(e)}")
        return False

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def chunk_text(text, chunk_size=1000, overlap=100):
    """Split text into chunks for better processing"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks = splitter.split_text(text)
    return chunks

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "llm_initialized": llm is not None})

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process PDF document"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        
        # Split into chunks
        chunks = chunk_text(text)
        
        # Store document
        doc_id = file.filename.replace('.pdf', '')
        documents[doc_id] = {
            'filename': file.filename,
            'content': text,
            'chunks': chunks,
            'chunk_count': len(chunks)
        }
        
        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "message": f"Document '{file.filename}' uploaded successfully with {len(chunks)} chunks"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    doc_list = [
        {
            "doc_id": doc_id,
            "filename": doc['filename'],
            "chunks": doc['chunk_count']
        }
        for doc_id, doc in documents.items()
    ]
    return jsonify({"documents": doc_list})

@app.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about uploaded documents"""
    try:
        if llm is None:
            return jsonify({"error": "API not initialized. Please set GEMINI_API_KEY environment variable."}), 400
        
        data = request.json
        question = data.get('question')
        doc_id = data.get('doc_id')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        if doc_id and doc_id not in documents:
            return jsonify({"error": f"Document '{doc_id}' not found"}), 404
        
        # Get relevant content
        if doc_id:
            content = documents[doc_id]['content'][:5000]  # Limit to first 5000 chars
        else:
            # Use all documents
            content = "\n\n".join([doc['content'][:2000] for doc in documents.values()])
        
        # Create prompt for topic explanation
        prompt_template = PromptTemplate(
            input_variables=["content", "question"],
            template="""Based on the following academic content:

{content}

Answer this question comprehensively:
{question}

Provide a clear, educational explanation suitable for students."""
        )
        
        chain = prompt_template | llm
        response = chain.invoke({"content": content, "question": question})
        answer_text = response.content if hasattr(response, 'content') else str(response)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer_text,
            "doc_id": doc_id
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/topic-explanation', methods=['POST'])
def topic_explanation():
    """Get comprehensive explanation on a topic"""
    try:
        if llm is None:
            return jsonify({"error": "API not initialized. Please set GEMINI_API_KEY environment variable."}), 400
        
        data = request.json
        topic = data.get('topic')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Gather content from all documents
        all_content = "\n\n".join([doc['content'][:3000] for doc in documents.values()])
        
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
        
        chain = prompt_template | llm
        response = chain.invoke({"content": all_content, "topic": topic})
        explanation_text = response.content if hasattr(response, 'content') else str(response)
        
        return jsonify({
            "success": True,
            "topic": topic,
            "explanation": explanation_text
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Initialize LLM on startup
    startup_llm()
    app.run(debug=True, port=5000)
