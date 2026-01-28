"""
Vector Store Service using ChromaDB for document embeddings
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import ollama
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(
        self, 
        collection_name: str = "hmo_documents",
        persist_directory: str = "./chromadb_data",
        embedding_model: str = "mxbai-embed-large"
    ):
        """
        Initialize ChromaDB vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
            embedding_model: Ollama embedding model name
        """
        self.embedding_model = embedding_model
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized with collection: {collection_name}")
        logger.info(f"Current document count: {self.collection.count()}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Ollama"""
        try:
            response = ollama.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def add_documents(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        try:
            # Generate embeddings for all texts
            embeddings = [self._generate_embedding(text) for text in texts]
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        n_results: int = 6,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with documents, metadatas, and distances
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Get collection count to avoid requesting more than available
            collection_count = self.collection.count()
            adjusted_n_results = min(n_results, collection_count)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=adjusted_n_results,
                where=where
            )
            
            actual_results = len(results['documents'][0]) if results['documents'] else 0
            logger.info(f"Search found {actual_results} results (requested: {n_results}, available: {collection_count})")
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by IDs"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_all_documents(self) -> Dict:
        """Get all documents in the collection"""
        try:
            count = self.collection.count()
            if count == 0:
                return {"documents": [], "metadatas": [], "ids": []}
            
            results = self.collection.get()
            return results
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise
    
    def reset(self) -> None:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.create_collection(
                name=self.collection.name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Vector store reset")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
