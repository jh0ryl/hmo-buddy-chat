"""
FastAPI Backend for HMO Buddy Chat with RAG capabilities
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import os
import tempfile
from pathlib import Path

from rag_service import RAGService
from vector_store import VectorStore
from document_processor import DocumentProcessor
import ollama 


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

# Add this function after your imports and before app initialization
def load_initial_documents():
    """Load documents from the documents directory on startup"""
    logger.info("Loading initial documents...")
    
    if not os.path.exists(DOCUMENTS_DIR):
        logger.info("Documents directory not found, skipping initial load")
        return
    
    doc_files = [f for f in os.listdir(DOCUMENTS_DIR) 
                 if f.endswith(('.txt', '.pdf', '.md', '.markdown'))]
    
    if not doc_files:
        logger.info("No documents found in documents directory")
        return
    
    # Check if documents are already loaded
    existing_docs = vector_store.get_all_documents()
    existing_sources = set()
    if existing_docs['metadatas']:
        existing_sources = {meta.get('source', '') for meta in existing_docs['metadatas']}
    
    loaded_count = 0
    for filename in doc_files:
        # Skip if already loaded
        if filename in existing_sources:
            logger.info(f"Document {filename} already in database, skipping")
            continue
            
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        try:
            logger.info(f"Loading document: {filename}")
            
            # Process document
            chunks = doc_processor.process_document(
                filepath, 
                metadata={'filename': filename}
            )
            
            # Add to vector store
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            vector_store.add_documents(texts=texts, metadatas=metadatas)
            loaded_count += 1
            logger.info(f"✓ Loaded {filename}: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"✗ Error loading {filename}: {e}")
    
    logger.info(f"Initial document load complete: {loaded_count} new documents loaded")


# Initialize FastAPI app
app = FastAPI(
    title="HMO Buddy Chat API",
    description="Local LLM with RAG capabilities using Ollama",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vector_store = VectorStore()
rag_service = RAGService(vector_store=vector_store)
doc_processor = DocumentProcessor()

# Create documents directory
DOCUMENTS_DIR = "./documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

load_initial_documents() 

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    use_context: bool = True
    stream: bool = False
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict]] = None


class HealthResponse(BaseModel):
    status: str
    llm_model: str
    embedding_model: str
    documents_count: int
    ollama_available: bool


class DocumentInfo(BaseModel):
    id: str
    source: str
    chunk_index: int
    total_chunks: int


# API Endpoints

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "HMO Buddy Chat API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "upload": "/api/upload",
            "documents": "/api/documents"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API and Ollama health"""
    try:
        # Check if Ollama is available
        ollama_available = False
        try:
            ollama.list()
            ollama_available = True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        
        # Get document count
        doc_count = vector_store.collection.count()
        
        return HealthResponse(
            status="healthy" if ollama_available else "degraded",
            llm_model=rag_service.llm_model,
            embedding_model=rag_service.embedding_model,
            documents_count=doc_count,
            ollama_available=ollama_available
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with RAG support
    
    - Supports streaming and non-streaming responses
    - Can use context from vector store or just LLM
    - Maintains conversation history
    """
    try:
        logger.info(f"Chat request: {request.message[:50]}...")
        
        if request.stream:
            # Streaming response
            async def stream_generator():
                try:
                    response_gen = rag_service.chat(
                        query=request.message,
                        conversation_history=request.conversation_history,
                        use_context=request.use_context,
                        stream=True
                    )
                    
                    for chunk in response_gen:
                        yield chunk
                        
                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    yield f"\n\n[Error: {str(e)}]"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/plain"
            )
        else:
            # Non-streaming response
            response_text = rag_service.chat(
                query=request.message,
                conversation_history=request.conversation_history,
                use_context=request.use_context,
                stream=False
            )
            
            # Get sources if context was used
            sources = None
            if request.use_context:
                contexts = rag_service.retrieve_context(request.message, n_results=3)
                sources = [{
                    'source': ctx['metadata'].get('source', 'Unknown'),
                    'similarity': ctx['similarity']
                } for ctx in contexts]
            
            return ChatResponse(
                response=response_text,
                sources=sources
            )
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    Supported formats: PDF, TXT, MD
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.md', '.markdown']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Process document
            chunks = doc_processor.process_document(tmp_path, metadata={'filename': file.filename})
            
            # Add to vector store
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            vector_store.add_documents(texts=texts, metadatas=metadatas)
            
            # Save to documents directory
            save_path = os.path.join(DOCUMENTS_DIR, file.filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(content)
            
            return {
                "message": f"Successfully processed {file.filename}",
                "chunks_created": len(chunks),
                "filename": file.filename
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    """List all indexed documents"""
    try:
        results = vector_store.get_all_documents()
        
        if not results['documents']:
            return {"documents": [], "count": 0}
        
        # Group by source
        documents = {}
        for i, metadata in enumerate(results['metadatas']):
            source = metadata.get('source', 'Unknown')
            if source not in documents:
                documents[source] = {
                    'source': source,
                    'chunks': 0,
                    'ids': []
                }
            documents[source]['chunks'] += 1
            documents[source]['ids'].append(results['ids'][i])
        
        return {
            "documents": list(documents.values()),
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_source}")
async def delete_document(document_source: str):
    """Delete a document by source name"""
    try:
        # Get all documents
        results = vector_store.get_all_documents()
        
        # Find IDs matching the source
        ids_to_delete = []
        for i, metadata in enumerate(results['metadatas']):
            if metadata.get('source') == document_source:
                ids_to_delete.append(results['ids'][i])
        
        if not ids_to_delete:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from vector store
        vector_store.delete_documents(ids_to_delete)
        
        # Delete from documents directory
        doc_path = os.path.join(DOCUMENTS_DIR, document_source)
        if os.path.exists(doc_path):
            os.remove(doc_path)
        
        return {
            "message": f"Deleted {document_source}",
            "chunks_deleted": len(ids_to_delete)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/reset")
async def reset_documents():
    """Clear all documents from the vector store"""
    try:
        vector_store.reset()
        return {"message": "All documents cleared"}
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
