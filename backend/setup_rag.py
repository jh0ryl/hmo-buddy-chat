"""
Setup Script for RAG System
Run this in your backend folder to set everything up
"""
import os
import sys
from pathlib import Path

def check_structure():
    """Check if we're in the right directory"""
    current_files = os.listdir('.')
    expected_files = ['vector_store.py', 'rag_service.py', 'documents']
    
    print("\n" + "="*60)
    print("CHECKING PROJECT STRUCTURE")
    print("="*60 + "\n")
    
    for file in expected_files:
        if file in current_files:
            print(f"✓ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            if file == 'documents':
                print(f"   Please create a 'documents' folder and add your 6 files")
    
    print()

def check_documents():
    """Check documents folder"""
    print("\n" + "="*60)
    print("CHECKING DOCUMENTS")
    print("="*60 + "\n")
    
    docs_folder = Path('./documents')
    
    if not docs_folder.exists():
        print("❌ Documents folder not found!")
        print("   Creating documents folder...")
        docs_folder.mkdir(exist_ok=True)
        print("✓ Created documents folder")
        print("   Please add your 6 document files there")
        return False
    
    # Count documents
    doc_files = list(docs_folder.glob('*.txt')) + list(docs_folder.glob('*.md'))
    
    print(f"Found {len(doc_files)} documents:")
    for i, doc in enumerate(doc_files, 1):
        size = doc.stat().st_size
        print(f"  {i}. {doc.name} ({size:,} bytes)")
    
    print()
    
    if len(doc_files) == 0:
        print("⚠️  No documents found!")
        print("   Please add your .txt or .md files to the documents folder")
        return False
    
    return True

def load_documents():
    """Load documents into vector store"""
    print("\n" + "="*60)
    print("LOADING DOCUMENTS")
    print("="*60 + "\n")
    
    try:
        from load_documents import DocumentLoader
        
        loader = DocumentLoader(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        num_chunks = loader.reset_and_reload('./documents')
        
        print(f"\n✓ Successfully loaded {num_chunks} chunks")
        return True
        
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return False

def test_system():
    """Test the RAG system"""
    print("\n" + "="*60)
    print("TESTING SYSTEM")
    print("="*60 + "\n")
    
    try:
        from improved_rag_service import ImprovedRAGService
        
        rag = ImprovedRAGService()
        
        # Check collection
        info = rag.get_collection_info()
        print(f"Collection: {info['collection_name']}")
        print(f"Documents: {info['document_count']}")
        
        if info['document_count'] == 0:
            print("\n❌ No documents in vector store")
            return False
        
        # Test retrieval
        print("\nTesting retrieval...")
        test_query = "benefits"  # Generic test query
        contexts = rag.retrieve_context(test_query, n_results=3)
        
        print(f"✓ Retrieved {len(contexts)} contexts for test query")
        
        if len(contexts) > 0:
            print(f"✓ Top similarity: {contexts[0]['similarity']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing system: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run setup"""
    print("\n" + "="*60)
    print("RAG SYSTEM SETUP")
    print("="*60)
    
    # Step 1: Check structure
    check_structure()
    
    # Step 2: Check documents
    has_docs = check_documents()
    
    if not has_docs:
        print("\n" + "="*60)
        print("SETUP INCOMPLETE")
        print("="*60)
        print("\nPlease add your documents to the 'documents' folder")
        print("Then run this script again")
        return
    
    # Step 3: Load documents
    print("\nProceed with loading documents? (y/n): ", end='')
    response = input().strip().lower()
    
    if response != 'y':
        print("\nSetup cancelled")
        return
    
    loaded = load_documents()
    
    if not loaded:
        print("\n❌ Failed to load documents")
        return
    
    # Step 4: Test system
    tested = test_system()
    
    # Summary
    print("\n" + "="*60)
    if tested:
        print("✅ SETUP COMPLETE")
        print("="*60)
        print("\nYour RAG system is ready!")
        print("\nNext steps:")
        print("1. Run: python main.py  (to start the API)")
        print("2. Or run: python quick_test.py  (to test queries)")
        print("3. Or run: python example_usage.py  (to see examples)")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("="*60)
        print("\nThere were some issues. Please check the errors above.")
    print()

if __name__ == "__main__":
    main()