# Python RAG Backend Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed from https://ollama.ai
3. **Models pulled**:
   ```bash
   ollama pull llama3.2
   ollama pull mxbai-embed-large
   ```

## Installation

### 1. Install Python Dependencies

Open a terminal in the `backend` directory and run:

```bash
cd backend
pip install -r requirements.txt
```

Or if you're using a virtual environment (recommended):

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Verify Ollama is Running

Make sure Ollama is running and your models are available:

```bash
ollama list
```

You should see both `llama3.2` and `mxbai-embed-large` in the list.

## Running the Backend

### Start the FastAPI Server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Or simply:

```bash
cd backend
python main.py
```

The backend will be available at: **http://localhost:8000**

### Test the Backend

Open a browser and visit:
- Health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/docs

## Running the Full Application

You need **two terminals**:

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## API Endpoints

### Health Check
```
GET /api/health
```
Returns backend status and model information.

### Chat
```
POST /api/chat
Body: {
  "message": "Your question",
  "use_context": true,
  "stream": false,
  "conversation_history": []
}
```

### Upload Document
```
POST /api/upload
Body: FormData with file
```
Supported formats: PDF, TXT, MD

### List Documents
```
GET /api/documents
```

### Delete Document
```
DELETE /api/documents/{source_name}
```

### Reset All Documents
```
POST /api/documents/reset
```

## Directory Structure

```
backend/
├── main.py                # FastAPI server
├── rag_service.py         # RAG logic
├── vector_store.py        # ChromaDB vector store
├── document_processor.py  # Document processing
├── requirements.txt       # Python dependencies
├── documents/             # Uploaded documents (auto-created)
└── chromadb_data/         # ChromaDB storage (auto-created)
```

## Adding Documents to Knowledge Base

### Option 1: Upload via API

Use the frontend or send a POST request:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@your_document.pdf"
```

### Option 2: Add to Documents Folder

1. Place your files (PDF, TXT, MD) in the `backend/documents/` folder
2. Process them manually:

```python
from document_processor import DocumentProcessor
from vector_store import VectorStore

processor = DocumentProcessor()
vector_store = VectorStore()

# Process a single file
chunks = processor.process_document("documents/your_file.pdf")
texts = [chunk['text'] for chunk in chunks]
metadatas = [chunk['metadata'] for chunk in chunks]
vector_store.add_documents(texts=texts, metadatas=metadatas)

# Or process entire directory
chunks = processor.process_directory("documents")
texts = [chunk['text'] for chunk in chunks]
metadatas = [chunk['metadata'] for chunk in chunks]
vector_store.add_documents(texts=texts, metadatas=metadatas)
```

## Configuration

### Model Configuration

Edit `backend/main.py` to change models:

```python
rag_service = RAGService(
    llm_model="llama3.2",           # Change LLM model
    embedding_model="mxbai-embed-large"  # Change embedding model
)
```

### Chunking Configuration

Edit `backend/main.py`:

```python
doc_processor = DocumentProcessor(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200     # Overlapping characters
)
```

### Vector Store Configuration

Edit `backend/vector_store.py`:

```python
vector_store = VectorStore(
    collection_name="hmo_documents",
    persist_directory="./chromadb_data"
)
```

## Troubleshooting

### Ollama Not Available

**Error:** `ollama_available: false`

**Solution:**
1. Make sure Ollama is installed and running
2. Verify models are pulled: `ollama list`
3. Test Ollama: `ollama run llama3.2 "Hello"`

### CORS Errors

**Error:** CORS policy blocking requests

**Solution:**
Add your frontend URL to CORS origins in `backend/main.py`:

```python
allow_origins=[
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://your-custom-url"
]
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
Change the port in `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

Or kill the process using port 8000.

## Testing the RAG System

1. **Upload a test document:**
   ```bash
   # Create a test file
   echo "HMO stands for Health Maintenance Organization." > test.txt
   
   # Upload it
   curl -X POST "http://localhost:8000/api/upload" -F "file=@test.txt"
   ```

2. **Query with RAG:**
   ```bash
   curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is HMO?", "use_context": true}'
   ```

3. **Verify the response uses your document as context**

## Production Deployment

For production, consider:

1. **Use environment variables** for configuration
2. **Add authentication** to API endpoints
3. **Use a production ASGI server** like Gunicorn with Uvicorn workers
4. **Set up proper logging**
5. **Configure rate limiting**
6. **Use a proper vector database** (if scaling beyond local use)

## Next Steps

- Update your React chat interface to use the new API
- Add a document upload UI component
- Display sources in chat responses
- Add conversation persistence
- Implement user authentication

For more information, see the API documentation at http://localhost:8000/docs
