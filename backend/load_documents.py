"""
Document Loader for RAG System
Loads documents from a folder and chunks them appropriately
"""
import os
from pathlib import Path
from typing import List, Dict, Tuple
from vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and chunk documents for vector store"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        vector_store: VectorStore = None
    ):
        """
        Initialize document loader
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
            vector_store: VectorStore instance
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store = vector_store or VectorStore()
    
    def load_text_file(self, filepath: str) -> str:
        """Load text from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Tuple[str, Dict]]:
        """
        Chunk text into smaller pieces with overlap
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If we're not at the end, try to break at a sentence or paragraph
            if end < text_length:
                # Look for paragraph break first
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start:
                    end = paragraph_break
                else:
                    # Look for sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if sentence_break != -1 and sentence_break > start:
                        end = sentence_break + 1
            
            # Extract chunk
            chunk = text[start:end].strip()
            
            if chunk:  # Only add non-empty chunks
                # Create chunk metadata
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = len(chunks)
                chunk_metadata['char_start'] = start
                chunk_metadata['char_end'] = end
                
                chunks.append((chunk, chunk_metadata))
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
    
    def load_documents_from_folder(
        self, 
        folder_path: str,
        file_extensions: List[str] = ['.txt', '.md', '.pdf']
    ) -> int:
        """
        Load all documents from a folder
        
        Args:
            folder_path: Path to folder containing documents
            file_extensions: List of file extensions to process
            
        Returns:
            Number of chunks added
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        all_chunks = []
        all_metadatas = []
        
        # Get all files with specified extensions
        files = []
        for ext in file_extensions:
            files.extend(folder.glob(f"*{ext}"))
        
        if not files:
            raise ValueError(f"No files found in {folder_path} with extensions {file_extensions}")
        
        logger.info(f"Found {len(files)} files to process")
        
        # Process each file
        for filepath in files:
            logger.info(f"Processing: {filepath.name}")
            
            try:
                # Load file content
                if filepath.suffix.lower() == '.pdf':
                    # For PDFs, you'd need additional handling
                    # For now, skip or use a PDF library
                    logger.warning(f"Skipping PDF file: {filepath.name}")
                    continue
                else:
                    content = self.load_text_file(str(filepath))
                
                # Create metadata
                metadata = {
                    'source': filepath.name,
                    'filepath': str(filepath),
                    'file_type': filepath.suffix
                }
                
                # Chunk the document
                chunks = self.chunk_text(content, metadata)
                
                logger.info(f"  Created {len(chunks)} chunks from {filepath.name}")
                
                # Separate texts and metadatas
                for chunk_text, chunk_metadata in chunks:
                    all_chunks.append(chunk_text)
                    all_metadatas.append(chunk_metadata)
                
            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")
                continue
        
        # Add all chunks to vector store
        if all_chunks:
            logger.info(f"Adding {len(all_chunks)} total chunks to vector store...")
            self.vector_store.add_documents(
                texts=all_chunks,
                metadatas=all_metadatas
            )
            logger.info(f"✓ Successfully added {len(all_chunks)} chunks")
        
        return len(all_chunks)
    
    def reset_and_reload(self, folder_path: str) -> int:
        """
        Reset vector store and reload all documents
        
        Args:
            folder_path: Path to folder containing documents
            
        Returns:
            Number of chunks added
        """
        logger.info("Resetting vector store...")
        self.vector_store.reset()
        
        logger.info("Loading documents...")
        return self.load_documents_from_folder(folder_path)


def main():
    """Example usage"""
    
    # Initialize loader
    loader = DocumentLoader(
        chunk_size=1000,  # Adjust based on your needs
        chunk_overlap=200
    )
    
    # Path to your documents folder
    documents_folder = "./documents"  # CHANGE THIS to your folder path
    
    print("\n" + "="*60)
    print("DOCUMENT LOADING")
    print("="*60 + "\n")
    
    # Check if folder exists
    if not os.path.exists(documents_folder):
        print(f"❌ Error: Folder '{documents_folder}' not found!")
        print(f"   Please update the 'documents_folder' variable with the correct path.")
        return
    
    # Load documents
    try:
        num_chunks = loader.reset_and_reload(documents_folder)
        
        print("\n" + "="*60)
        print("LOADING COMPLETE")
        print("="*60)
        print(f"\n✓ Successfully loaded {num_chunks} chunks into vector store")
        
        # Show collection info
        count = loader.vector_store.collection.count()
        print(f"✓ Total documents in collection: {count}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
