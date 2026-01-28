"""
Quick test script to verify RAG system is working
"""
import sys
import ollama
from vector_store import VectorStore
from document_processor import DocumentProcessor
from rag_service import RAGService

def test_ollama():
    """Test Ollama connection"""
    print("=" * 50)
    print("Testing Ollama Connection")
    print("=" * 50)
    
    try:
        models = ollama.list()
        print("✓ Ollama is running")
        print("\nAvailable models:")
        for model in models.get('models', []):
            print(f"  - {model['name']}")
        
        # Check for required models
        model_names = [m['name'] for m in models.get('models', [])]
        
        has_llm = any('llama3.2' in name for name in model_names)
        has_embed = any('mxbai-embed-large' in name for name in model_names)
        
        if not has_llm:
            print("\n⚠ Warning: llama3.2 not found. Run: ollama pull llama3.2")
        if not has_embed:
            print("\n⚠ Warning: mxbai-embed-large not found. Run: ollama pull mxbai-embed-large")
        
        if has_llm and has_embed:
            print("\n✓ All required models are available")
            return True
        return False
        
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        return False

def test_document_processing():
    """Test document processing"""
    print("\n" + "=" * 50)
    print("Testing Document Processing")
    print("=" * 50)
    
    try:
        processor = DocumentProcessor()
        
        # Test with sample document
        import os
        sample_path = "documents/sample_hmo_info.txt"
        
        if not os.path.exists(sample_path):
            print(f"✗ Sample document not found: {sample_path}")
            return False
        
        chunks = processor.process_document(sample_path)
        print(f"✓ Processed sample document")
        print(f"  - File: {sample_path}")
        print(f"  - Chunks created: {len(chunks)}")
        print(f"  - First chunk preview: {chunks[0]['text'][:100]}...")
        
        return chunks
        
    except Exception as e:
        print(f"✗ Document processing failed: {e}")
        return None

def test_vector_store(chunks):
    """Test vector store"""
    print("\n" + "=" * 50)
    print("Testing Vector Store")
    print("=" * 50)
    
    try:
        vector_store = VectorStore(collection_name="test_collection")
        
        # Clear any existing data
        vector_store.reset()
        print("✓ Vector store initialized")
        
        # Add documents
        if chunks:
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            vector_store.add_documents(texts=texts, metadatas=metadatas)
            print(f"✓ Added {len(texts)} documents")
        
        # Test search
        query = "What is an HMO?"
        results = vector_store.search(query, n_results=2)
        
        print(f"\n✓ Search test successful")
        print(f"  - Query: {query}")
        print(f"  - Results found: {len(results['documents'][0])}")
        
        if results['documents'][0]:
            print(f"  - Top result preview: {results['documents'][0][0][:100]}...")
        
        return vector_store
        
    except Exception as e:
        print(f"✗ Vector store failed: {e}")
        return None

def test_rag_service(vector_store):
    """Test RAG service"""
    print("\n" + "=" * 50)
    print("Testing RAG Service")
    print("=" * 50)
    
    try:
        rag_service = RAGService(vector_store=vector_store)
        print("✓ RAG service initialized")
        
        # Test query
        query = "How can i book for an appointment?"
        print(f"\n  Query: {query}")
        print("  Generating response...")
        
        response = rag_service.generate_response(
            query=query,
            use_context=True,
            stream=False
        )
        
        print(f"\n✓ Response generated successfully")
        print(f"\n  Response preview:")
        print(f"  {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG service failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 HMO Buddy Chat - RAG System Test\n")
    
    # Test 1: Ollama
    if not test_ollama():
        print("\n⚠ Ollama test failed. Please ensure Ollama is running with required models.")
        sys.exit(1)
    
    # Test 2: Document Processing
    chunks = test_document_processing()
    if not chunks:
        print("\n⚠ Document processing failed.")
        sys.exit(1)
    
    # Test 3: Vector Store
    vector_store = test_vector_store(chunks)
    if not vector_store:
        print("\n⚠ Vector store test failed.")
        sys.exit(1)
    
    # Test 4: RAG Service
    if not test_rag_service(vector_store):
        print("\n⚠ RAG service test failed.")
        sys.exit(1)
    
    # All tests passed
    print("\n" + "=" * 50)
    print("✓ All Tests Passed!")
    print("=" * 50)
    print("\nYour RAG system is working correctly!")
    print("\nNext steps:")
    print("  1. Start the backend: python -m uvicorn main:app --reload --port 8000")
    print("  2. Visit API docs: http://localhost:8000/docs")
    print("  3. Test the chat endpoint")
    print() 


vs = VectorStore()

print("="*60)
print("TESTING APPOINTMENT SEARCH")
print("="*60)

# Test different queries
queries = [
    "How can I book an appointment?",
    "appointment booking",
    "book appointment",
    "schedule consultation",
    "make appointment"
]

for query in queries:
    print(f"\n🔍 Query: '{query}'")
    results = vs.search(query, n_results=3)
    
    print(f"   Found {len(results['documents'][0])} results:")
    
    for i, (doc, meta, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"\n   [{i}] Source: {meta.get('source')}")
        print(f"       Distance: {distance:.4f}")
        print(f"       Content: {doc[:100]}...")

if __name__ == "__main__":
    main()
