"""
Updated main.py with improved RAG service
Replace your existing main.py with this version
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging

# Import the improved RAG service instead of the old one
from improved_rag_service import ImprovedRAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize improved RAG service
rag_service = ImprovedRAGService(
    llm_model="llama3.2",
    embedding_model="mxbai-embed-large"
)

# Request models
class QueryRequest(BaseModel):
    query: str
    use_context: bool = True
    n_context_docs: int = 6
    min_similarity: float = 0.0
    temperature: float = 0.7

class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None
    use_context: bool = True
    n_context_docs: int = 6
    min_similarity: float = 0.0

class DocumentRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[dict]] = None

# Response models
class QueryResponse(BaseModel):
    response: str
    contexts_used: int
    
class ChatResponse(BaseModel):
    response: str
    contexts_used: int

class StatusResponse(BaseModel):
    status: str
    document_count: int
    collection_name: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG API is running"}


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get vector store status"""
    try:
        info = rag_service.get_collection_info()
        return StatusResponse(
            status="operational",
            document_count=info.get('document_count', 0),
            collection_name=info.get('collection_name', 'unknown')
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system
    
    This endpoint uses the improved RAG service with better prompting
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Generate response using improved service
        response = rag_service.generate_response(
            query=request.query,
            use_context=request.use_context,
            n_context_docs=request.n_context_docs,
            min_similarity=request.min_similarity,
            temperature=request.temperature,
            stream=False
        )
        
        # Get context count for response
        contexts_used = 0
        if request.use_context:
            contexts = rag_service.retrieve_context(
                request.query,
                n_results=request.n_context_docs,
                min_similarity=request.min_similarity
            )
            contexts_used = len(contexts)
        
        return QueryResponse(
            response=response,
            contexts_used=contexts_used
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with conversation history
    
    Uses improved RAG service for better context handling
    """
    try:
        logger.info(f"Received chat message: {request.query}")
        
        response = rag_service.chat(
            query=request.query,
            conversation_history=request.conversation_history,
            use_context=request.use_context,
            n_context_docs=request.n_context_docs,
            min_similarity=request.min_similarity,
            stream=False
        )
        
        # Get context count
        contexts_used = 0
        if request.use_context:
            contexts = rag_service.retrieve_context(
                request.query,
                n_results=request.n_context_docs,
                min_similarity=request.min_similarity
            )
            contexts_used = len(contexts)
        
        return ChatResponse(
            response=response,
            contexts_used=contexts_used
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-documents")
async def add_documents(request: DocumentRequest):
    """Add documents to vector store"""
    try:
        rag_service.vector_store.add_documents(
            texts=request.texts,
            metadatas=request.metadatas
        )
        
        count = rag_service.vector_store.collection.count()
        
        return {
            "message": f"Added {len(request.texts)} documents",
            "total_documents": count
        }
        
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contexts/{query}")
async def get_contexts(query: str, n_results: int = 6, min_similarity: float = 0.0):
    """
    Get retrieved contexts for a query (useful for debugging)
    """
    try:
        contexts = rag_service.retrieve_context(
            query=query,
            n_results=n_results,
            min_similarity=min_similarity
        )
        
        return {
            "query": query,
            "contexts": [
                {
                    "text": ctx['text'][:200] + "...",  # Truncate for API response
                    "full_text": ctx['text'],
                    "source": ctx['metadata'].get('source', 'Unknown'),
                    "similarity": ctx['similarity']
                }
                for ctx in contexts
            ],
            "total_contexts": len(contexts)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reset")
async def reset_vector_store():
    """Reset the vector store (delete all documents)"""
    try:
        rag_service.vector_store.reset()
        return {"message": "Vector store reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/{query}")
async def debug_query(query: str):
    """
    Debug endpoint to see what's happening with a query
    Returns detailed information about context retrieval and processing
    """
    try:
        # Get collection info
        info = rag_service.get_collection_info()
        
        # Get contexts
        contexts = rag_service.retrieve_context(query, n_results=3)
        
        # Format contexts for response
        context_info = [
            {
                "similarity": ctx['similarity'],
                "source": ctx['metadata'].get('source', 'Unknown'),
                "preview": ctx['text'][:150] + "...",
                "length": len(ctx['text'])
            }
            for ctx in contexts
        ]
        
        # Get formatted prompt (without generating response)
        formatted_prompt = ""
        if contexts:
            formatted_prompt = rag_service.format_prompt_with_context(query, contexts)
        
        return {
            "query": query,
            "collection_info": info,
            "contexts_retrieved": len(contexts),
            "context_details": context_info,
            "formatted_prompt_length": len(formatted_prompt),
            "formatted_prompt_preview": formatted_prompt[:500] + "..."
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Check if documents are loaded
    info = rag_service.get_collection_info()
    logger.info(f"Starting server with {info.get('document_count', 0)} documents loaded")
    
    if info.get('document_count', 0) == 0:
        logger.warning("⚠️  No documents loaded! Run load_documents.py first")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)