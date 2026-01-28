# Academic Learning Assistant

A simple, multi-document learning assistant following Track A specifications. Upload PDFs, ask questions, and get AI-powered explanations using OpenAI's GPT-3.5.

## Architecture

- **Backend**: Python Flask REST API with PDF processing and LangChain integration
- **Frontend**: Static HTML + Vanilla JavaScript with modern UI
- **LLM**: OpenAI GPT-3.5-turbo

## Features

- 📄 **Multi-document upload** - Upload PDF files for processing
- ❓ **Ask questions** - Get answers based on uploaded documents
- 💡 **Topic explanations** - Comprehensive explanations on any topic
- 🔍 **Content extraction** - Automatic PDF text extraction and chunking
- 🎯 **Document listing** - View all uploaded documents

## Prerequisites

- Python 3.8+
- OpenAI API key (get from https://platform.openai.com/api-keys)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
cd backend
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Open Frontend

Open `frontend/index.html` in a web browser (double-click the file or drag to browser)

## Usage

1. **Initialize API**
   - Paste your OpenAI API key in the "Setup API" section
   - Click "Initialize API"

2. **Upload Documents**
   - Click "Select PDF File"
   - Choose a PDF document
   - Click "Upload PDF"

3. **Ask Questions**
   - Type your question in the "Ask Questions" tab
   - Optionally select a specific document
   - Click "Get Answer"

4. **Get Topic Explanations**
   - Click the "Topic Explanation" tab
   - Enter a topic name
   - Click "Get Explanation"

## API Endpoints

- `GET /health` - Health check
- `POST /init-api` - Initialize OpenAI API key
- `POST /upload` - Upload PDF document
- `GET /documents` - List all uploaded documents
- `POST /ask` - Ask a question
- `POST /topic-explanation` - Get topic explanation

## Project Structure

```
academic-assistant/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Single-page frontend
└── README.md               # This file
```

## Technologies Used

- **Backend Framework**: Flask
- **PDF Processing**: PyPDF2
- **LLM Framework**: LangChain
- **LLM Provider**: OpenAI GPT-3.5-turbo
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **CORS**: Flask-CORS

## Limitations

- PDF text extraction quality depends on document format
- Maximum document content stored in memory
- Responses limited to first 5000 characters of document
- Requires active internet connection for LLM API calls

## Future Enhancements

- Add DOCX and PPTX support
- Implement persistent storage (database)
- Add vector search with FAISS/ChromaDB
- Support for multiple LLM providers
- Export functionality (study guides, summaries)
- User authentication and document management

## Troubleshooting

**API not initializing?**
- Check if OpenAI API key is valid
- Ensure internet connection is active

**PDF upload fails?**
- Ensure file is a valid PDF
- Check if PDF text is extractable (not scanned image)

**No response from questions?**
- Upload a document first
- Check if API is initialized
- Verify internet connection

## License

MIT
