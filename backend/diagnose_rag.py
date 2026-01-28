"""
Diagnostic script to test RAG system
"""
from vector_store import VectorStore
from rag_service import RAGService
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def diagnose_vector_store():
    """Check vector store status"""
    print("\n" + "="*60)
    print("STEP 1: Checking Vector Store")
    print("="*60)
    
    vs = VectorStore()
    
    # Check document count
    count = vs.collection.count()
    print(f"\n✓ Total documents in vector store: {count}")
    
    if count == 0:
        print("❌ ERROR: No documents found in vector store!")
        print("   You need to load your documents first.")
        return False
    
    # Get sample documents
    print("\n📄 Sample documents:")
    results = vs.collection.get(limit=3)
    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
        print(f"\nDocument {i}:")
        print(f"  Source: {metadata.get('source', 'Unknown')}")
        print(f"  Preview: {doc[:150]}...")
        print(f"  Length: {len(doc)} characters")
    
    return True


def test_retrieval():
    """Test document retrieval"""
    print("\n" + "="*60)
    print("STEP 2: Testing Document Retrieval")
    print("="*60)
    
    rag = RAGService()
    
    # Test queries - CUSTOMIZE THESE based on your actual documents
    test_queries = [
        "What are the coverage benefits?",
        "How do I file a claim?",
        "What is covered under this plan?",
        "eligibility requirements",
        "premium costs"
    ]
    
    print("\nTesting retrieval with sample queries:\n")
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        contexts = rag.retrieve_context(query, n_results=3, min_similarity=0.0)
        
        if not contexts:
            print("   ❌ No contexts retrieved!")
        else:
            print(f"   ✓ Retrieved {len(contexts)} contexts")
            for i, ctx in enumerate(contexts, 1):
                print(f"\n   Context {i}:")
                print(f"     Similarity: {ctx['similarity']:.3f}")
                print(f"     Source: {ctx['metadata'].get('source', 'Unknown')}")
                print(f"     Preview: {ctx['text'][:100]}...")


def test_response_generation():
    """Test full RAG response generation"""
    print("\n" + "="*60)
    print("STEP 3: Testing Response Generation")
    print("="*60)
    
    rag = RAGService()
    
    # Test query - CUSTOMIZE THIS based on your documents
    test_query = "What are the main benefits covered in this plan?"
    
    print(f"\n📝 Test Query: '{test_query}'")
    
    # First, show what context is retrieved
    print("\n--- Retrieved Context ---")
    contexts = rag.retrieve_context(test_query, n_results=3)
    for i, ctx in enumerate(contexts, 1):
        print(f"\nContext {i} (similarity: {ctx['similarity']:.3f}):")
        print(ctx['text'][:200] + "...")
    
    # Generate response
    print("\n--- Generated Response ---")
    try:
        response = rag.generate_response(
            test_query,
            use_context=True,
            n_context_docs=3,
            stream=False
        )
        print(f"\n{response}")
    except Exception as e:
        print(f"❌ Error generating response: {e}")


def compare_with_without_context():
    """Compare responses with and without context"""
    print("\n" + "="*60)
    print("STEP 4: Comparing Responses (With vs Without Context)")
    print("="*60)
    
    rag = RAGService()
    
    test_query = "What is covered under this plan?"
    
    print(f"\n📝 Query: '{test_query}'")
    
    # Response WITH context
    print("\n--- Response WITH Context ---")
    try:
        response_with = rag.generate_response(
            test_query,
            use_context=True,
            n_context_docs=3,
            stream=False
        )
        print(response_with[:500] + "..." if len(response_with) > 500 else response_with)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Response WITHOUT context
    print("\n--- Response WITHOUT Context ---")
    try:
        response_without = rag.generate_response(
            test_query,
            use_context=False,
            stream=False
        )
        print(response_without[:500] + "..." if len(response_without) > 500 else response_without)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG SYSTEM DIAGNOSTICS")
    print("="*60)
    
    # Run diagnostics
    if diagnose_vector_store():
        test_retrieval()
        test_response_generation()
        compare_with_without_context()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)
