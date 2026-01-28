"""
Quick Test Script for RAG System
Run this to quickly test your setup
"""
from improved_rag_service import ImprovedRAGService


def main():
    print("\n" + "="*60)
    print("QUICK RAG SYSTEM TEST")
    print("="*60 + "\n")
    
    # Initialize RAG service
    print("Initializing RAG service...")
    rag = ImprovedRAGService()
    
    # Check collection
    info = rag.get_collection_info()
    print(f"\n📊 Vector Store Status:")
    print(f"   Collection: {info['collection_name']}")
    print(f"   Documents: {info['document_count']}")
    
    if info['document_count'] == 0:
        print("\n❌ No documents found!")
        print("   Please run 'load_documents.py' first to load your documents.")
        return
    
    # Test query - CUSTOMIZE THIS based on your documents
    test_queries = [
        "What are the benefits?",
        "How do I file a claim?",
        "What is the coverage?"
    ]
    
    print(f"\n{'='*60}")
    print("Testing with sample queries...")
    print(f"{'='*60}\n")
    
    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"Query: '{query}'")
        print(f"{'─'*60}\n")
        
        # Use the interactive debug method
        rag.interactive_debug(query)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nIf you see good context retrieval but poor responses,")
    print("the issue is likely with prompt engineering or model choice.")
    print("\nIf you see no/poor context retrieval, the issue is likely")
    print("with document chunking or embedding quality.")


if __name__ == "__main__":
    main()
