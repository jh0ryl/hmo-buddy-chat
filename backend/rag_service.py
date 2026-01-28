"""
RAG Service for retrieval-augmented generation using Ollama
"""
import ollama
from typing import List, Dict, Optional, Iterator
from vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    def __init__(
        self,
        llm_model: str = "llama3.2",
        embedding_model: str = "mxbai-embed-large",
        vector_store: Optional[VectorStore] = None
    ):
        """
        Initialize RAG service
        
        Args:
            llm_model: Ollama LLM model name
            embedding_model: Ollama embedding model name
            vector_store: Optional VectorStore instance
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.vector_store = vector_store or VectorStore(embedding_model=embedding_model)
        
        logger.info(f"RAG Service initialized with LLM: {llm_model}")
    
    def retrieve_context(
        self, 
        query: str, 
        n_results: int = 6,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Retrieve relevant context from vector store
        
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
                    
                    if similarity >= min_similarity:
                        contexts.append({
                            'text': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'similarity': similarity
                        })
            
            logger.info(f"Retrieved {len(contexts)} context chunks for query")
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
        Format prompt with retrieved context
        
        Args:
            query: User query
            contexts: Retrieved context chunks
            system_prompt: Optional system prompt
            
        Returns:
            Formatted prompt
        """
        if not contexts:
            return query
        
        # Build context section
        context_text = "\n\n".join([
            f"[Source: {ctx['metadata'].get('source', 'Unknown')}]\n{ctx['text']}"
            for ctx in contexts
        ])
        
        # Default system prompt
        if system_prompt is None:
            system_prompt = (
                "You are HMO Buddy, a helpful assistant for Health Maintenance Organization (HMO) queries.\n\n"
                "INSTRUCTIONS:\n"
                "1. Use the CONTEXT below to answer the user's question\n"
                "2. If the context contains the answer, provide a clear and specific response based on it\n"
                "3. If the context doesn't contain relevant information, say so clearly and then provide general guidance if appropriate\n"
                "4. Always be helpful, clear, and professional"
            )
        
        # Format full prompt
        formatted_prompt = f"""{system_prompt}

CONTEXT:
{context_text}

USER QUESTION:
{query}

ANSWER:"""
        
        return formatted_prompt
    
    def generate_response(
        self,
        query: str,
        use_context: bool = True,
        n_context_docs: int = 6,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Iterator[str] | str:
        """
        Generate response using RAG
        
        Args:
            query: User query
            use_context: Whether to use RAG context
            n_context_docs: Number of context documents to retrieve
            system_prompt: Optional system prompt
            stream: Whether to stream the response
            
        Returns:
            Generated response (string or iterator)
        """
        try:
            # Retrieve context if enabled
            contexts = []
            if use_context:
                contexts = self.retrieve_context(query, n_results=n_context_docs)
            
            # Format prompt
            if contexts:
                prompt = self.format_prompt_with_context(query, contexts, system_prompt)
            else:
                prompt = query
            
            # Generate response
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                stream=stream
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
        stream: bool = False
    ) -> Iterator[str] | str:
        """
        Chat with context awareness and history
        
        Args:
            query: User query
            conversation_history: List of previous messages
            use_context: Whether to use RAG context
            n_context_docs: Number of context documents
            stream: Whether to stream response
            
        Returns:
            Response (string or iterator)
        """
        try:
            # Retrieve context if enabled
            contexts = []
            if use_context:
                contexts = self.retrieve_context(query, n_results=n_context_docs)
            
            # Build messages
            messages = []
            
            # Add system message with context
            if contexts:
                context_text = "\n\n".join([
                    f"[Source: {ctx['metadata'].get('source', 'Unknown')}]\n{ctx['text']}"
                    for ctx in contexts
                ])
                
                system_message = (
                    "You are HMO Buddy, a helpful assistant for Health Maintenance Organization (HMO) queries.\n\n"
                    "IMPORTANT INSTRUCTIONS:\n"
                    "- Answer questions using the CONTEXT provided below\n"
                    "- If the context contains relevant information, base your answer on it\n"
                    "- Be specific and cite information from the context when applicable\n"
                    "- If the context doesn't contain the answer, clearly state that and provide general guidance if appropriate\n"
                    "- Always be helpful, professional, and accurate\n\n"
                    f"CONTEXT:\n{context_text}\n"
                )
                messages.append({'role': 'system', 'content': system_message})
            else:
                # No context available
                system_message = (
                    "You are HMO Buddy, a helpful assistant for Health Maintenance Organization (HMO) queries. "
                    "Provide accurate and helpful information based on your knowledge."
                )
                messages.append({'role': 'system', 'content': system_message})
            
            # Add conversation history (limit to last 5 exchanges to avoid context overflow)
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages = 5 exchanges
            
            # Add current query
            messages.append({'role': 'user', 'content': query})
            
            # Log what we're sending to the LLM
            logger.debug(f"Sending {len(messages)} messages to LLM")
            if contexts:
                logger.debug(f"Context from sources: {[ctx['metadata'].get('source') for ctx in contexts]}")
            
            # Generate response
            response = ollama.chat(
                model=self.llm_model,
                messages=messages,
                stream=stream
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