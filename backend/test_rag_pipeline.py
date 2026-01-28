# test_rag_pipeline.py
from rag_service import RAGService
from vector_store import VectorStore

vs = VectorStore()
rag = RAGService(vector_store=vs)

query = "How can I book an appointment?"

# Get context
contexts = rag.retrieve_context(query, n_results=3)

print("="*60)
print("CONTEXTS RETRIEVED:")
print("="*60)
for i, ctx in enumerate(contexts, 1):
    print(f"\n[{i}] Source: {ctx['metadata'].get('source')}")
    print(f"    Similarity: {ctx['similarity']:.4f}")
    print(f"    Text: {ctx['text'][:200]}...")

print("\n" + "="*60)
print("TESTING FULL RAG RESPONSE:")
print("="*60)

response = rag.chat(query, use_context=True, stream=False)
print(f"\nResponse: {response}")