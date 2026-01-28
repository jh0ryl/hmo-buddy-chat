"""
Improved RAG Service for retrieval-augmented generation using Ollama
"""
import ollama
from typing import List, Dict, Optional, Iterator
from vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedRAGService:
    def __init__(
        self,
        llm_model: str = "llama3.2",
        embedding_model: str = "mxbai-embed-large",
        vector_store: Optional[VectorStore] = None
    ):
        """
        Initialize RAG service with improved prompting
        
        Args:
            llm_model: Ollama LLM model name
            embedding_model: Ollama embedding model name
            vector_store: Optional VectorStore instance
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.vector_store = vector_store or VectorStore(embedding_model=embedding_model)
        
        logger.info(f"Improved RAG Service initialized with LLM: {llm_model}")
    
    def get_collection_info(self) -> Dict:
        """Get information about the vector store collection"""
        try:
            count = self.vector_store.collection.count()
            return {
                'document_count': count,
                'collection_name': self.vector_store.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {'document_count': 0, 'error': str(e)}
    
    def retrieve_context(
        self, 
        query: str, 
        n_results: int = 6,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Retrieve relevant context from vector store with detailed logging
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of relevant context chunks with metadata
        """
        try:
            results = self.vector_store.search(query, n_results=n_results)
            
            # Extract and format results
            contexts = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    # Calculate similarity (distance to similarity)
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    # Log each retrieved document for debugging
                    logger.info(f"Retrieved doc {i+1}: similarity={similarity:.3f}, "
                               f"source={metadata.get('source', 'Unknown')}")
                    logger.debug(f"Content preview: {doc[:100]}...")
                    
                    if similarity >= min_similarity:
                        contexts.append({
                            'text': doc,
                            'metadata': metadata,
                            'similarity': similarity
                        })
            
            logger.info(f"Retrieved {len(contexts)} context chunks for query: '{query}'")
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def format_prompt_with_context(
        self, 
        query: str, 
        contexts: List[Dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Format prompt with retrieved context using improved structure
        
        Args:
            query: User query
            contexts: Retrieved context chunks
            system_prompt: Optional system prompt
            
        Returns:
            Formatted prompt
        """
        if not contexts:
            return query
        
        # Build context section with clear numbering and sources
        context_sections = []
        for i, ctx in enumerate(contexts, 1):
            source = ctx['metadata'].get('source', 'Unknown')
            similarity = ctx['similarity']
            context_sections.append(
                f"Document {i} (from {source}, relevance: {similarity:.2f}):\n{ctx['text']}"
            )
        
        context_text = "\n\n".join(context_sections)
        
        # Improved system prompt with explicit instructions
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that answers questions based on provided documents. "
                "Follow these guidelines:\n"
                "1. Base your answer PRIMARILY on the information in the documents below\n"
                "2. Quote or reference specific documents when appropriate\n"
                "3. If the documents don't contain enough information, clearly state this\n"
                "4. You may use general knowledge to supplement, but make it clear when you do so"
            )
        
        # Format full prompt with clear sections
        formatted_prompt = f"""{system_prompt}

{'='*60}
RELEVANT DOCUMENTS
{'='*60}

{context_text}

{'='*60}
END OF DOCUMENTS
{'='*60}

USER QUESTION: {query}

Please provide a clear, comprehensive answer based on the documents above. Reference specific documents when quoting or citing information.

ANSWER:"""
        
        return formatted_prompt
    
    def generate_response(
        self,
        query: str,
        use_context: bool = True,
        n_context_docs: int = 6,
        min_similarity: float = 0.0,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7
    ) -> Iterator[str] | str:
        """
        Generate response using RAG with improved prompting
        
        Args:
            query: User query
            use_context: Whether to use RAG context
            n_context_docs: Number of context documents to retrieve
            min_similarity: Minimum similarity threshold for context
            system_prompt: Optional system prompt
            stream: Whether to stream the response
            temperature: Model temperature (0.0-1.0)
            
        Returns:
            Generated response (string or iterator)
        """
        try:
            # Retrieve context if enabled
            contexts = []
            if use_context:
                contexts = self.retrieve_context(
                    query, 
                    n_results=n_context_docs,
                    min_similarity=min_similarity
                )
                
                if not contexts:
                    logger.warning("No contexts retrieved - falling back to non-RAG response")
            
            # Format prompt
            if contexts:
                prompt = self.format_prompt_with_context(query, contexts, system_prompt)
                logger.debug(f"Formatted prompt length: {len(prompt)} characters")
            else:
                prompt = query
            
            # Generate response with options
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                stream=stream,
                options={
                    'temperature': temperature,
                }
            )
            
            if stream:
                # Return generator for streaming
                def response_generator():
                    for chunk in response:
                        if 'message' in chunk and 'content' in chunk['message']:
                            yield chunk['message']['content']
                return response_generator()
            else:
                # Return complete response
                return response['message']['content']
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def chat(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        use_context: bool = True,
        n_context_docs: int = 6,
        min_similarity: float = 0.0,
        stream: bool = False,
        temperature: float = 0.7
    ) -> Iterator[str] | str:
        """
        Chat with context awareness and conversation history
        
        Args:
            query: User query
            conversation_history: List of previous messages
            use_context: Whether to use RAG context
            n_context_docs: Number of context documents
            min_similarity: Minimum similarity for retrieved context
            stream: Whether to stream response
            temperature: Model temperature
            
        Returns:
            Response (string or iterator)
        """
        try:
            # Retrieve context if enabled
            contexts = []
            if use_context:
                contexts = self.retrieve_context(
                    query, 
                    n_results=n_context_docs,
                    min_similarity=min_similarity
                )
            
            # Build messages list
            messages = []
            
            # Add system message with context if available
            if contexts:
                context_sections = []
                for i, ctx in enumerate(contexts, 1):
                    source = ctx['metadata'].get('source', 'Unknown')
                    context_sections.append(
                        f"[Document {i} from {source}]:\n{ctx['text']}"
                    )
                
                context_text = "\n\n".join(context_sections)
                
                system_message = (
                    "You are a helpful assistant. Use the following documents to answer questions:\n\n"
                    f"{'='*50}\n"
                    f"{context_text}\n"
                    f"{'='*50}\n\n"
                    "When answering:\n"
                    "- Base your response on the documents above when relevant\n"
                    "- Reference specific documents when appropriate\n"
                    "- Use general knowledge to supplement if needed, but be clear about it"
                )
                messages.append({'role': 'system', 'content': system_message})
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current query
            messages.append({'role': 'user', 'content': query})
            
            # Generate response
            response = ollama.chat(
                model=self.llm_model,
                messages=messages,
                stream=stream,
                options={
                    'temperature': temperature,
                }
            )
            
            if stream:
                def response_generator():
                    for chunk in response:
                        if 'message' in chunk and 'content' in chunk['message']:
                            yield chunk['message']['content']
                return response_generator()
            else:
                return response['message']['content']
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def interactive_debug(self, query: str):
        """
        Interactive debugging method to see what's happening
        
        Args:
            query: User query to debug
        """
        print(f"\n{'='*60}")
        print(f"DEBUGGING QUERY: '{query}'")
        print(f"{'='*60}\n")
        
        # Step 1: Check collection
        info = self.get_collection_info()
        print(f"📊 Collection Info:")
        print(f"   Documents: {info.get('document_count', 0)}")
        print(f"   Collection: {info.get('collection_name', 'Unknown')}\n")
        
        # Step 2: Retrieve context
        print(f"🔍 Retrieving context...")
        contexts = self.retrieve_context(query, n_results=3, min_similarity=0.0)
        
        if not contexts:
            print("   ❌ No contexts retrieved!\n")
        else:
            print(f"   ✓ Retrieved {len(contexts)} contexts:\n")
            for i, ctx in enumerate(contexts, 1):
                print(f"   Context {i}:")
                print(f"      Similarity: {ctx['similarity']:.3f}")
                print(f"      Source: {ctx['metadata'].get('source', 'Unknown')}")
                print(f"      Length: {len(ctx['text'])} chars")
                print(f"      Preview: {ctx['text'][:150]}...\n")
        
        # Step 3: Show formatted prompt
        if contexts:
            print(f"📝 Formatted Prompt Preview:")
            prompt = self.format_prompt_with_context(query, contexts)
            print(f"   Length: {len(prompt)} characters")
            print(f"   First 500 chars:\n")
            print(f"   {prompt[:500]}...\n")
        
        # Step 4: Generate response
        print(f"🤖 Generating response...\n")
        try:
            response = self.generate_response(query, use_context=True, n_context_docs=3)
            print(f"📤 Response:")
            print(f"   {response}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        print(f"{'='*60}\n")
