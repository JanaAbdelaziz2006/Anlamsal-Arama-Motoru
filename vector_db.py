"""
Professional Vector Database (VectorDB) System
=============================================
A high-performance, OOP-based vector database implementation using:
- FAISS (IndexHNSWFlat) for efficient similarity search
- Sentence Transformers for embeddings
- Batch processing for scalability
- Generator-based data loading to minimize memory usage
- Comprehensive logging and error handling

Author: Vector DB System
Date: 2026
"""

import logging
import numpy as np
from typing import List, Tuple, Dict, Generator, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import json
import os
import re
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


# ==================== Logging Configuration ====================

def setup_logger(name: str, log_file: str = "vector_db.log") -> logging.Logger:
    """
    Configure logging with both file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    
    # Formatter for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logger("VectorDB")


# ==================== Custom Exceptions ====================

class VectorDBException(Exception):
    """Base exception for VectorDB system."""
    pass


class EmbeddingException(VectorDBException):
    """Exception raised during embedding generation."""
    pass


class IndexingException(VectorDBException):
    """Exception raised during indexing operations."""
    pass


class SearchException(VectorDBException):
    """Exception raised during search operations."""
    pass


class DataLoadingException(VectorDBException):
    """Exception raised during data loading."""
    pass


# ==================== Data Models ====================

@dataclass
class Document:
    """Represents a document in the vector database."""
    id: str
    content: str
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        """Validate document structure."""
        if not self.id:
            raise ValueError("Document ID cannot be empty")
        if not self.content:
            raise ValueError("Document content cannot be empty")


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    document_id: str
    content: str
    score: float
    metadata: Optional[Dict] = None


# ==================== Embedding Manager ====================

class EmbeddingManager:
    """
    Manages text embedding generation using Sentence Transformers.
    Handles model loading, caching, and error handling.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the sentence-transformers model
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the sentence transformer model with error handling."""
        try:
            # Lazy import to speed up initial system start
            from sentence_transformers import SentenceTransformer
            import torch
            
            logger.info(f"Loading embedding model: {self.model_name}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer(self.model_name, device=device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise EmbeddingException(f"Model loading failed: {str(e)}")
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
            
        Raises:
            EmbeddingException: If embedding generation fails
        """
        try:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Input text must be a non-empty string")
            
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise EmbeddingException(f"Failed to generate embedding: {str(e)}")
    
    def embed_batch(self, texts: List[str], batch_size: int = 256) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            Matrix of embeddings (n_texts, embedding_dim)
            
        Raises:
            EmbeddingException: If batch embedding fails
        """
        try:
            if not texts:
                raise ValueError("Input text list cannot be empty")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            raise EmbeddingException(f"Failed to generate batch embeddings: {str(e)}")


# ==================== Data Loader ====================

class DataLoader:
    """
    Generator-based data loader for efficient memory usage.
    Reads documents from disk without loading entire dataset into memory.
    """
    
    def __init__(self, data_file: Path):
        """
        Initialize data loader.
        
        Args:
            data_file: Path to JSONL data file (one JSON per line)
        """
        self.data_file = Path(data_file)
        self._validate_file()
    
    def _validate_file(self) -> None:
        """Validate that data file exists and is readable."""
        if not self.data_file.exists():
            raise DataLoadingException(f"Data file not found: {self.data_file}")
        
        if not self.data_file.is_file():
            raise DataLoadingException(f"Data path is not a file: {self.data_file}")
        
        logger.info(f"Data file validated: {self.data_file}")
    
    def load_documents(self, max_documents: Optional[int] = None) -> Generator[Document, None, None]:
        """
        Generator that yields documents from file one by one.
        
        Args:
            max_documents: Maximum number of documents to load (None for all)
            
        Yields:
            Document objects
            
        Raises:
            DataLoadingException: If document parsing fails
        """
        try:
            count = 0
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if max_documents and count >= max_documents:
                        break
                    
                    try:
                        line = line.strip()
                        if not line:
                            continue
                        
                        data = json.loads(line)
                        
                        # Validate required fields
                        if 'id' not in data or 'content' not in data:
                            logger.warning(f"Skipping invalid document: missing required fields")
                            continue
                        
                        doc = Document(
                            id=data['id'],
                            content=data['content'],
                            metadata=data.get('metadata', None)
                        )
                        
                        count += 1
                        yield doc
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON line: {str(e)}")
                        continue
                    except ValueError as e:
                        logger.warning(f"Invalid document format: {str(e)}")
                        continue
            
            logger.info(f"Loaded {count} documents from {self.data_file}")
        
        except Exception as e:
            logger.error(f"Error during data loading: {str(e)}")
            raise DataLoadingException(f"Failed to load data: {str(e)}")

class DocumentProcessor:
    """Handles different file formats and text chunking for large documents."""
    
    @staticmethod
    def extract_pages_from_pdf(pdf_path: Path) -> List[Dict]:
        """Extract text and page numbers from PDF."""
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is required for PDF processing. Install with: pip install pymupdf")
        
        pages = []
        try:
            with fitz.open(str(pdf_path)) as doc:
                for page_num, page in enumerate(doc, 1):
                    # Metni bloklar halinde alarak yapısal bütünlüğü koruyoruz
                    text = page.get_text("text", sort=True)
                    clean = DocumentProcessor.clean_text(text)
                    # Çok kısa sayfaları (boş veya sadece resim) atla
                    if len(clean) > 30: 
                        pages.append({
                            "text": clean,
                            "page": page_num
                        })
            return pages
        except Exception as e:
            logger.error(f"Failed to read PDF {pdf_path}: {e}")
            return []

    @staticmethod
    def clean_text(text: str) -> str:
        """Extract edilen metindeki sayfa numaraları, hoca isimleri ve gereksiz boşlukları temizler."""
        # 1. Sayfa numaraları ve altbilgileri temizle (Örn: 13 / 47, sayfa 1)
        text = re.sub(r'\d+\s*/\s*\d+', '', text)
        text = re.sub(r'Sayfa\s*\d+', '', text, flags=re.IGNORECASE)
        # 2. Hocanın ismini ve ünvanını temizle
        text = re.sub(r'Dr\.\s*Öğr\.\s*Üyesi\s*Adem\s*AVCI', '', text, flags=re.IGNORECASE)
        # 3. URL, mail ve gereksiz karakterleri temizle (Algoritma sembollerini koru)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s\.\,\?\!\:\(\)\[\]\<\>\=\+\-\*\/]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Implement overlapping chunks to maintain context between snippets."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            # Don't cut in the middle of a word if possible
            if end < text_len:
                last_space = text.rfind(' ', start, end)
                if last_space != -1:
                    end = last_space
            
            chunks.append(text[start:end].strip())
            start = end - overlap if end < text_len else text_len
            if start < 0: start = 0
            if end >= text_len: break
            
        return chunks

# ==================== FAISS Index Manager ====================

class FAISSIndexManager:
    """
    Manages FAISS indexing using HNSW algorithm for fast similarity search.
    Supports async indexing for large datasets.
    """
    
    def __init__(self, embedding_dim: int, max_connections: int = 32):
        """
        Initialize FAISS index.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            max_connections: Max connections per node in HNSW graph
        """
        self.embedding_dim = embedding_dim
        self.max_connections = max_connections
        self.index = None
        self.document_map = {}  # Maps index position to document ID
        self.doc_count = 0
        self._create_index()
    
    def _create_index(self) -> None:
        """Create HNSW index with optimized parameters."""
        try:
            # Lazy import to speed up initial system start
            import faiss
            
            # Create HNSW index
            # ef_construction: controls index quality/speed trade-off (higher = more accurate but slower)
            self.index = faiss.IndexHNSWFlat(
                self.embedding_dim,
                self.max_connections
            )
            
            # Set ef_search for query time (lower = faster)
            self.index.hnsw.ef_search = 256
            
            # Disable GPU and use CPU
            
            
            logger.info(f"HNSW index created with dimension={self.embedding_dim}, "
                       f"max_connections={self.max_connections}")
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise IndexingException(f"Index creation failed: {str(e)}")
    
    def add_embeddings(self, embeddings: np.ndarray, doc_ids: List[str]) -> None:
        """
        Add embeddings to the index.
        
        Args:
            embeddings: Matrix of embeddings (n_vectors, embedding_dim)
            doc_ids: List of document IDs corresponding to embeddings
            
        Raises:
            IndexingException: If adding embeddings fails
        """
        try:
            if len(embeddings) != len(doc_ids):
                raise ValueError("Number of embeddings must match number of document IDs")
            
            if embeddings.shape[1] != self.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                               f"got {embeddings.shape[1]}")
            
            # Embeddings are already normalized by EmbeddingManager
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Update document map
            start_idx = self.doc_count
            for i, doc_id in enumerate(doc_ids):
                self.document_map[start_idx + i] = doc_id
            
            self.doc_count += len(doc_ids)
            logger.info(f"Added {len(doc_ids)} embeddings to index. Total: {self.doc_count}")
        
        except Exception as e:
            logger.error(f"Failed to add embeddings: {str(e)}")
            raise IndexingException(f"Adding embeddings failed: {str(e)}")
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for similar vectors in the index.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of nearest neighbors to return
            
        Returns:
            List of (index_position, distance) tuples
            
        Raises:
            SearchException: If search fails
        """
        try:
            if self.doc_count == 0:
                raise ValueError("Index is empty")
            
            if query_embedding.shape[0] != self.embedding_dim:
                raise ValueError(f"Query embedding dimension mismatch: "
                               f"expected {self.embedding_dim}, got {query_embedding.shape[0]}")
            
            # Query is already normalized
            query = query_embedding.reshape(1, -1).astype(np.float32)
            
            distances, indices = self.index.search(
                query,
                min(k, self.doc_count)
            )
            
            # For normalized vectors, L2 distance can be converted to cosine similarity
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx >= 0:  # Valid result
                    similarity = 1 - (dist / 2)  # Normalize HNSW distance
                    results.append((idx, similarity))
            
            return results
        
        except Exception as e:
            logger.error(f"Search operation failed: {str(e)}")
            raise SearchException(f"Search failed: {str(e)}")
    
    def save_index(self, filepath: Path) -> None:
        """
        Save index to disk.
        
        Args:
            filepath: Path to save index
        """
        try:
            import faiss
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            faiss.write_index(self.index, str(filepath))
            
            # Save document map
            map_file = filepath.with_suffix('.json')
            with open(map_file, 'w') as f:
                json.dump(self.document_map, f)
            
            logger.info(f"Index saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            raise IndexingException(f"Index saving failed: {str(e)}")
    
    def load_index(self, filepath: Path) -> None:
        """
        Load index from disk.
        
        Args:
            filepath: Path to load index from
        """
        try:
            import faiss
            filepath = Path(filepath)
            if not filepath.exists():
                raise ValueError(f"Index file not found: {filepath}")
            
            self.index = faiss.read_index(str(filepath))
            
            # Load document map
            map_file = filepath.with_suffix('.json')
            if map_file.exists():
                with open(map_file, 'r') as f:
                    doc_map = json.load(f)
                    # Convert keys back to integers
                    self.document_map = {int(k): v for k, v in doc_map.items()}
                    self.doc_count = len(self.document_map)
            
            logger.info(f"Index loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            raise IndexingException(f"Index loading failed: {str(e)}")


# ==================== Main VectorDB System ====================

class VectorDatabase:
    """
    Main Vector Database class combining all components.
    Provides high-level interface for indexing and searching.
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize Vector Database.
        
        Args:
            embedding_model: Name of embedding model to use
        """
        self.embedding_manager = EmbeddingManager(embedding_model)
        self.index_manager = FAISSIndexManager(
            embedding_dim=self.embedding_manager.embedding_dim
        )
        self.documents = {}  # Store document content by ID
        logger.info("Vector Database initialized")

    def index_directory(self, directory_path: Path, chunk_size: int = 400, batch_size: int = 128) -> None:
        """Dizin içindeki dosyaları tara ve sayfa bazlı indeksle."""
        path = Path(directory_path)
        processor = DocumentProcessor()
        
        all_chunks = []
        all_ids = []
        
        for file_path in path.rglob("*"):
            if file_path.suffix.lower() == ".pdf":
                logger.info(f"Processing PDF: {file_path.name}")
                pages = processor.extract_pages_from_pdf(file_path)
                for page_data in pages:
                    chunks = processor.chunk_text(page_data["text"], chunk_size=chunk_size)
                    batch_ids = [f"{file_path.name}_p{page_data['page']}_s{i}" for i in range(len(chunks))]
                    
                    for i, chunk in enumerate(chunks):
                        self.documents[batch_ids[i]] = {
                            'content': chunk,
                            'metadata': {
                                'source': file_path.name,
                                'page': page_data["page"],
                                'type': 'pdf'
                            }
                        }
                    all_chunks.extend(chunks)
                    all_ids.extend(batch_ids)
            elif file_path.suffix.lower() in [".txt", ".md"]:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                clean_content = processor.clean_text(content)
                chunks = processor.chunk_text(clean_content, chunk_size=chunk_size)
                batch_ids = [f"{file_path.name}_c{i}" for i in range(len(chunks))]
                for i, chunk in enumerate(chunks):
                    self.documents[batch_ids[i]] = {
                        'content': chunk,
                        'metadata': {'source': file_path.name, 'page': 1, 'type': 'text'}
                    }
                all_chunks.extend(chunks)
                all_ids.extend(batch_ids)

        # Hızlandırma: Tüm parçaları tek tek değil, büyük paketler (batch) halinde işle
        if all_chunks:
            for i in range(0, len(all_chunks), batch_size):
                self._process_batch(all_chunks[i:i + batch_size], all_ids[i:i + batch_size], batch_size=batch_size)

    def index_documents(self, data_file: Path, batch_size: int = 32, 
                       max_documents: Optional[int] = None) -> None:
        """
        Index documents from file.
        
        Args:
            data_file: Path to JSONL data file
            batch_size: Number of documents to embed at once
            max_documents: Maximum documents to index
        """
        try:
            logger.info(f"Starting document indexing from {data_file}")
            
            loader = DataLoader(data_file)
            batch_docs = []
            batch_ids = []
            
            for doc in loader.load_documents(max_documents):
                batch_docs.append(doc.content)
                batch_ids.append(doc.id)
                
                # Store document
                self.documents[doc.id] = {
                    'content': doc.content,
                    'metadata': doc.metadata
                }
                
                # Process batch
                if len(batch_docs) >= batch_size:
                    self._process_batch(batch_docs, batch_ids, batch_size=batch_size)
                    batch_docs = []
                    batch_ids = []
            
            # Process remaining documents
            if batch_docs:
                self._process_batch(batch_docs, batch_ids, batch_size=batch_size)
            
            logger.info(f"Indexing complete. Total documents: {len(self.documents)}")
        
        except Exception as e:
            logger.error(f"Document indexing failed: {str(e)}")
            raise
    
    def _process_batch(self, texts: List[str], doc_ids: List[str], batch_size: int = 256) -> None:
        """
        Process a batch of documents.
        
        Args:
            texts: List of document texts
            doc_ids: List of document IDs
            batch_size: Number of items to process
        """
        try:
            # Generate embeddings
            embeddings = self.embedding_manager.embed_batch(texts, batch_size=batch_size)
            
            # Add to index
            self.index_manager.add_embeddings(embeddings, doc_ids)
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        Search for documents similar to query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
            
        Raises:
            SearchException: If search fails
        """
        try:
            if not query.strip():
                raise ValueError("Query cannot be empty")
            
            # Semantik arama yap
            query_embedding = self.embedding_manager.embed(query)
            results = self.index_manager.search(query_embedding, top_k)
            
            search_results = []
            for idx, score in results:
                if idx in self.index_manager.document_map:
                    doc_id = self.index_manager.document_map[idx]
                    doc = self.documents.get(doc_id, {})
                    
                    search_results.append(SearchResult(
                        document_id=doc_id,
                        content=doc.get('content', ''),
                        score=float(score),
                        metadata=doc.get('metadata', None)
                    ))
            
            logger.info(f"Search completed for query: '{query}'. Results: {len(search_results)}")
            return search_results
        
        except Exception as e:
            logger.error(f"Search operation failed: {str(e)}")
            raise SearchException(f"Search failed: {str(e)}")
    
    def save(self, index_path: Path) -> None:
        """
        Save the database to disk.
        
        Args:
            index_path: Path to save index
        """
        try:
            self.index_manager.save_index(index_path)
            
            # Save documents
            docs_file = Path(index_path).with_name("documents.json")
            with open(docs_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Database saved to {index_path}")
        except Exception as e:
            logger.error(f"Failed to save database: {str(e)}")
            raise
    
    def load(self, index_path: Path) -> None:
        """
        Load the database from disk.
        
        Args:
            index_path: Path to load index from
        """
        try:
            self.index_manager.load_index(index_path)
            
            # Load documents
            docs_file = Path(index_path).with_name("documents.json")
            if docs_file.exists():
                with open(docs_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            
            logger.info(f"Database loaded from {index_path}")
        except Exception as e:
            logger.error(f"Failed to load database: {str(e)}")
            raise
    def add_list_of_documents(self, contents: List[str]) -> None:
        """Hızlı testler için liste üzerinden döküman ekler."""
        doc_ids = [f"doc_{i}" for i in range(len(contents))]
        embeddings = self.embedding_manager.embed_batch(contents)
    
        # Dökümanları sözlüğe kaydet
        for doc_id, text in zip(doc_ids, contents):
            self.documents[doc_id] = {'content': text, 'metadata': None}
        
        self.index_manager.add_embeddings(embeddings, doc_ids)

if __name__ == "__main__":
    logger.info("Vector Database module ready")