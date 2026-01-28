"""
Document Processing Service for loading and chunking documents
"""
from typing import List, Dict
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_text_file(self, file_path: str) -> str:
        """Load text from a .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            raise
    
    def load_pdf_file(self, file_path: str) -> str:
        """Load text from a PDF file"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {e}")
            raise
    
    def load_markdown_file(self, file_path: str) -> str:
        """Load text from a markdown file"""
        return self.load_text_file(file_path)
    
    def load_document(self, file_path: str) -> str:
        """
        Load document based on file extension
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document text content
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.txt':
            return self.load_text_file(file_path)
        elif ext == '.pdf':
            return self.load_pdf_file(file_path)
        elif ext in ['.md', '.markdown']:
            return self.load_markdown_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word
            if end < text_length:
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundaries
                    space = text.rfind(' ', start, end)
                    if space != -1 and space > start + self.chunk_size // 2:
                        end = space
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= 0 or start >= text_length:
                break
        
        return chunks
    
    def process_document(
        self, 
        file_path: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """
        Process a document into chunks with metadata
        
        Args:
            file_path: Path to the document
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of dictionaries containing chunks and metadata
        """
        try:
            # Load document
            text = self.load_document(file_path)
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Create metadata for each chunk
            file_name = os.path.basename(file_path)
            base_metadata = metadata or {}
            base_metadata.update({
                'source': file_name,
                'file_path': file_path
            })
            
            # Create result
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = base_metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                processed_chunks.append({
                    'text': chunk,
                    'metadata': chunk_metadata
                })
            
            logger.info(f"Processed {file_name} into {len(chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Process all supported documents in a directory
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of processed chunks
        """
        all_chunks = []
        supported_extensions = ['.txt', '.pdf', '.md', '.markdown']
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        chunks = self.process_document(file_path)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        logger.warning(f"Skipping {file}: {e}")
        
        logger.info(f"Processed {len(all_chunks)} chunks from directory {directory_path}")
        return all_chunks
