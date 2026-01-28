# HMO RAG System 🏥

A Retrieval-Augmented Generation (RAG) system for HMO documentation that uses Ollama for local LLM inference and provides intelligent responses based on your organization's documents.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **📚 Document-Based Responses**: Answers queries using your HMO documentation
- **🔍 Smart Retrieval**: Intelligent context retrieval with similarity scoring
- **💬 Conversational AI**: Maintains context across multiple turns
- **🚀 Fast & Local**: Runs locally using Ollama (no API costs)
- **🔧 Easy Setup**: Simple installation with minimal dependencies
- **🎯 Accurate**: Enhanced prompt engineering for better context utilization
- **📊 Debug Tools**: Built-in diagnostics and testing utilities

## 🏗️ Architecture

```
┌─────────────┐
│   FastAPI   │ ← REST API Server
│   Backend   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
┌──────▼──────┐   ┌─────▼─────┐
│  RAG Service │   │  Vector   │
│   (Ollama)   │   │   Store   │
└──────┬──────┘   └─────┬─────┘
       │                 │
       └─────────┬───────┘
                 │
         ┌───────▼────────┐
         │   Documents    │
         │  (HMO Files)   │
         └────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- 4GB+ RAM recommended
- Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hmo-rag-system.git
cd hmo-rag-system
```

### 2. Install Dependencies

**Option A: Simple Installation (No C++ build tools required)**
```bash
pip install -r requirements_simple.txt
```

**Option B: Full Installation (with ChromaDB)**
```bash
pip install -r requirements.txt
```

### 3. Install Ollama Models

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 4. Add Your Documents

Place your HMO documents (`.txt` or `.md` files) in the `backend/documents/` folder:

```
backend/documents/
├── policies.txt
├── faqs.txt
├── contracts.txt
├── sops.txt
├── appointment.txt
└── sample_hmo_info.txt
```

### 5. Setup the System

```bash
cd backend
python setup_rag.py
```

This will:
- Check your project structure
- Load and chunk your documents
- Create embeddings
- Test the system

### 6. Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 7. Test It!

```bash
# Check status
curl http://localhost:8000/status

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the HMO benefits?"}'
```

## 📁 Project Structure

```
hmo-rag-system/
├── backend/
│   ├── main.py                      # FastAPI server
│   ├── improved_rag_service.py      # Enhanced RAG service
│   ├── vector_store.py              # Vector storage (Simple or ChromaDB)
│   ├── load_documents.py            # Document loader with chunking
│   ├── setup_rag.py                 # Setup script
│   ├── quick_test.py                # Quick testing
│   ├── diagnose_rag.py             # Diagnostic tools
│   ├── example_usage.py            # Usage examples
│   ├── documents/                   # Your HMO documents
│   │   ├── policies.txt
│   │   ├── faqs.txt
│   │   └── ...
│   └── simple_vector_data/          # Vector database
├── src/                             # Frontend (Next.js/React)
│   ├── components/
│   ├── pages/
│   └── services/
├── requirements.txt                 # Full dependencies
├── requirements_simple.txt          # Minimal dependencies
├── README.md                        # This file
```

## 🔌 API Endpoints

### GET `/status`
Get system status and document count.

**Response:**
```json
{
  "status": "operational",
  "document_count": 42,
  "collection_name": "hmo_documents"
}
```

### POST `/query`
Query the RAG system.

**Request:**
```json
{
  "query": "What are the coverage benefits?",
  "use_context": true,
  "n_context_docs": 6,
  "min_similarity": 0.0,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Based on the HMO documentation...",
  "contexts_used": 5
}
```

### POST `/chat`
Chat with conversation history.

**Request:**
```json
{
  "query": "How much does it cost?",
  "conversation_history": [
    {"role": "user", "content": "What plans are available?"},
    {"role": "assistant", "content": "We offer..."}
  ],
  "use_context": true
}
```

### GET `/contexts/{query}`
Debug endpoint to see retrieved contexts.

### GET `/debug/{query}`
Detailed debugging information.

### POST `/add-documents`
Add documents programmatically.

### DELETE `/reset`
Reset the vector store.

## 🎨 Frontend Integration

### React/Next.js Example

```typescript
async function queryRAG(question: string) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: question,
      use_context: true,
      n_context_docs: 6
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

### With Conversation History

```typescript
const [history, setHistory] = useState([]);

async function chat(message: string) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: message,
      conversation_history: history,
      use_context: true
    })
  });
  
  const data = await response.json();
  
  // Update history
  setHistory([
    ...history,
    { role: 'user', content: message },
    { role: 'assistant', content: data.response }
  ]);
  
  return data.response;
}
```

## ⚙️ Configuration

### Adjust Chunking Strategy

Edit `load_documents.py`:

```python
loader = DocumentLoader(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200     # Overlap between chunks
)
```

### Adjust Retrieval Settings

```python
response = rag.generate_response(
    query,
    n_context_docs=10,    # Number of contexts to retrieve
    min_similarity=0.3,   # Minimum similarity threshold
    temperature=0.7       # Model temperature (0.0-1.0)
)
```

### Use Different Models

```python
rag = ImprovedRAGService(
    llm_model="llama3.1:8b",           # Different LLM
    embedding_model="mxbai-embed-large" # Different embeddings
)
```

## 🧪 Testing

### Quick Test
```bash
python quick_test.py
```

### Full Diagnostics
```bash
python diagnose_rag.py
```

### Test Specific Query
```python
from improved_rag_service import ImprovedRAGService

rag = ImprovedRAGService()
rag.interactive_debug("Your question here")
```

## 🐛 Troubleshooting

### No documents loaded
```bash
# Check documents folder
ls backend/documents/

# Reload documents
cd backend
python load_documents.py
```

### Poor responses
- Increase `n_context_docs` (try 8-10)
- Lower `min_similarity` (try 0.0-0.3)
- Adjust `temperature` (lower = more focused)
- Use a larger model (llama3.1:8b or llama2:13b)

### ChromaDB installation issues (Windows)
Use the simple vector store instead:
```bash
pip install -r requirements_simple.txt
# Replace vector_store.py with simple_vector_store.py
```

## 📊 Performance Tips

- **Chunk Size**: 1000-1500 characters for most documents
- **Chunk Overlap**: 200-300 characters for context continuity
- **Context Docs**: 6-10 for comprehensive answers
- **Temperature**: 0.3-0.5 for factual responses, 0.7-0.9 for creative
- **Model**: Use llama3.1:8b or larger for better accuracy

## 🔒 Security

- Runs completely locally (no data sent to external APIs)
- No API keys required
- Documents stay on your machine

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [ChromaDB](https://www.trychroma.com/) / Simple Vector Store - Vector database
- The open-source AI community


## ⭐ Star History

If you find this project helpful, please consider giving it a star!

---

Made with ❤️ for better HMO documentation access
