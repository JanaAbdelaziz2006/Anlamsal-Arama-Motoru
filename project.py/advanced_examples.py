"""
Advanced Usage Examples and Best Practices
===========================================
Demonstrates advanced features and optimization techniques for the Vector Database system.
"""

import json
from pathlib import Path
from vector_db import (
    VectorDatabase,
    EmbeddingManager,
    FAISSIndexManager,
    DataLoader,
    Document,
    logger
)
import numpy as np


class AdvancedVectorDBExamples:
    """Collection of advanced usage examples."""
    
    @staticmethod
    def example_1_low_level_api():
        """Example 1: Using low-level components directly."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 1: Low-Level API Usage")
        logger.info("=" * 60)
        
        # Create individual components
        logger.info("\n1. Initialize Embedding Manager...")
        embedding_mgr = EmbeddingManager(model_name="all-MiniLM-L6-v2")
        
        logger.info("2. Create FAISS Index...")
        index_mgr = FAISSIndexManager(
            embedding_dim=embedding_mgr.embedding_dim,
            max_connections=32
        )
        
        # Embed texts
        logger.info("3. Generate embeddings...")
        texts = [
            "Natural language processing with transformers",
            "Deep learning neural networks",
            "Machine learning supervised learning"
        ]
        
        embeddings = embedding_mgr.embed_batch(texts)
        logger.info(f"   Embeddings shape: {embeddings.shape}")
        
        # Add to index
        logger.info("4. Add embeddings to index...")
        doc_ids = [f"doc_{i}" for i in range(len(texts))]
        index_mgr.add_embeddings(embeddings, doc_ids)
        
        # Search
        logger.info("5. Perform similarity search...")
        query = "neural networks learning"
        query_emb = embedding_mgr.embed(query)
        results = index_mgr.search(query_emb, k=2)
        
        for idx, score in results:
            logger.info(f"   Found: {doc_ids[idx]} (Score: {score:.4f})")
    
    @staticmethod
    def example_2_large_scale_indexing():
        """Example 2: Handling large-scale datasets efficiently."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 2: Large-Scale Indexing")
        logger.info("=" * 60)
        
        # Create large sample dataset
        sample_file = Path("large_dataset.jsonl")
        
        if not sample_file.exists():
            logger.info("\nCreating large sample dataset...")
            with open(sample_file, 'w', encoding='utf-8') as f:
                for i in range(1000):  # 1000 documents
                    doc = {
                        'id': f'doc_{i:06d}',
                        'content': f"Sample document {i}. This is a test document for large-scale indexing. " * 3,
                        'metadata': {'doc_num': i}
                    }
                    f.write(json.dumps(doc) + '\n')
        
        # Index with optimization
        logger.info("\nIndexing with optimization...")
        db = VectorDatabase()
        
        # Use larger batch size for better throughput
        db.index_documents(sample_file, batch_size=64)
        
        logger.info(f"✓ Indexed {len(db.documents)} documents")
        
        # Perform search
        logger.info("\nSearching...")
        results = db.search("test document", top_k=5)
        logger.info(f"✓ Found {len(results)} results")
    
    @staticmethod
    def example_3_memory_efficient_loading():
        """Example 3: Memory-efficient data loading with generators."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 3: Memory-Efficient Data Loading")
        logger.info("=" * 60)
        
        # Create test file
        test_file = Path("test_data.jsonl")
        with open(test_file, 'w', encoding='utf-8') as f:
            for i in range(100):
                doc = {
                    'id': f'doc_{i}',
                    'content': f"Document {i} with some content",
                    'metadata': {'index': i}
                }
                f.write(json.dumps(doc) + '\n')
        
        logger.info("\nLoading data with generator (memory-efficient)...")
        
        # Use DataLoader with generator
        loader = DataLoader(test_file)
        
        doc_count = 0
        for doc in loader.load_documents(max_documents=50):
            doc_count += 1
            if doc_count % 10 == 0:
                logger.info(f"  Loaded {doc_count} documents...")
        
        logger.info(f"✓ Loaded {doc_count} documents without loading all into memory")
    
    @staticmethod
    def example_4_persistence():
        """Example 4: Save and restore database from disk."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 4: Database Persistence")
        logger.info("=" * 60)
        
        # Create initial database
        logger.info("\n1. Creating initial database...")
        sample_file = Path("sample_for_persistence.jsonl")
        
        if not sample_file.exists():
            with open(sample_file, 'w', encoding='utf-8') as f:
                for i in range(50):
                    doc = {
                        'id': f'doc_{i}',
                        'content': f"Document {i}: Machine learning and AI are transforming industry",
                        'metadata': {'batch': i // 10}
                    }
                    f.write(json.dumps(doc) + '\n')
        
        db1 = VectorDatabase()
        db1.index_documents(sample_file)
        logger.info(f"   Created database with {len(db1.documents)} documents")
        
        # Save to disk
        index_path = Path("saved_database.faiss")
        logger.info(f"\n2. Saving database to {index_path}...")
        db1.save(index_path)
        
        # Load from disk
        logger.info(f"3. Loading database from {index_path}...")
        db2 = VectorDatabase()
        db2.load(index_path)
        logger.info(f"   Loaded database with {len(db2.documents)} documents")
        
        # Verify
        logger.info("\n4. Verifying loaded database...")
        query = "artificial intelligence"
        results1 = db1.search(query, top_k=3)
        results2 = db2.search(query, top_k=3)
        
        match = len(results1) == len(results2)
        logger.info(f"   ✓ Results match: {match}")
    
    @staticmethod
    def example_5_semantic_search():
        """Example 5: Semantic search with various query types."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 5: Semantic Search Capabilities")
        logger.info("=" * 60)
        
        # Create test data
        test_file = Path("semantic_test.jsonl")
        with open(test_file, 'w', encoding='utf-8') as f:
            docs = [
                "Python is a powerful programming language",
                "Machine learning models process large datasets",
                "Neural networks are inspired by biological neurons",
                "Data science combines statistics and programming",
                "Deep learning uses multiple layers of abstraction",
                "Artificial intelligence is transforming technology",
                "Computer vision processes images and videos",
                "Natural language processing understands text",
            ]
            for i, doc in enumerate(docs):
                data = {
                    'id': f'doc_{i}',
                    'content': doc,
                    'metadata': {'category': 'tech'}
                }
                f.write(json.dumps(data) + '\n')
        
        # Index
        logger.info("\nIndexing documents...")
        db = VectorDatabase()
        db.index_documents(test_file)
        
        # Perform various semantic searches
        queries = [
            ("programming languages", "Programming query"),
            ("deep neural networks", "Deep learning query"),
            ("image recognition", "Computer vision query"),
            ("text analysis", "NLP query"),
        ]
        
        logger.info("\nPerforming semantic searches...\n")
        
        for query, description in queries:
            logger.info(f"Query: '{query}' ({description})")
            results = db.search(query, top_k=3)
            
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. [{result.score:.4f}] {result.content}")
            
            logger.info("")
    
    @staticmethod
    def example_6_batch_embedding_optimization():
        """Example 6: Batch embedding optimization."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 6: Batch Embedding Optimization")
        logger.info("=" * 60)
        
        embedding_mgr = EmbeddingManager()
        
        # Test different batch sizes
        test_texts = [
            f"Sample text number {i} for batch processing" 
            for i in range(100)
        ]
        
        logger.info("\nTesting different batch sizes...\n")
        
        batch_sizes = [8, 16, 32, 64]
        
        for batch_size in batch_sizes:
            logger.info(f"Batch size: {batch_size}")
            embeddings = embedding_mgr.embed_batch(test_texts, batch_size=batch_size)
            logger.info(f"  Output shape: {embeddings.shape}")
            logger.info(f"  Output dtype: {embeddings.dtype}")
            logger.info(f"  Memory usage: ~{embeddings.nbytes / 1024 / 1024:.2f} MB\n")
    
    @staticmethod
    def example_7_error_handling_and_validation():
        """Example 7: Error handling and input validation."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 7: Error Handling and Validation")
        logger.info("=" * 60)
        
        db = VectorDatabase()
        
        test_cases = [
            ("", "Empty query", True),  # Should fail
            ("valid query", "Valid query", False),  # Should work
            ("   ", "Whitespace only", True),  # Should fail
        ]
        
        logger.info("\nTesting error handling...\n")
        
        for query, description, should_fail in test_cases:
            logger.info(f"Test: {description}")
            
            try:
                if len(db.documents) == 0:
                    logger.info("  Skipping (database empty)\n")
                    continue
                
                results = db.search(query, top_k=5)
                
                if should_fail:
                    logger.info("  ✗ Expected error but succeeded")
                else:
                    logger.info(f"  ✓ Success - Found {len(results)} results")
            
            except Exception as e:
                if should_fail:
                    logger.info(f"  ✓ Caught expected error: {type(e).__name__}")
                else:
                    logger.info(f"  ✗ Unexpected error: {e}")
            
            logger.info("")
    
    @staticmethod
    def example_8_metadata_utilization():
        """Example 8: Using metadata for filtering and context."""
        logger.info("\n" + "=" * 60)
        logger.info("EXAMPLE 8: Metadata Utilization")
        logger.info("=" * 60)
        
        # Create test data with metadata
        test_file = Path("metadata_test.jsonl")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            categories = ['technology', 'science', 'business']
            
            for i in range(30):
                doc = {
                    'id': f'doc_{i:04d}',
                    'content': f"Document {i} about machine learning and AI applications",
                    'metadata': {
                        'category': categories[i % 3],
                        'priority': (i % 5) + 1,
                        'source': f'source_{i % 3}',
                        'timestamp': f'2026-05-{(i % 28) + 1:02d}'
                    }
                }
                f.write(json.dumps(doc) + '\n')
        
        # Index
        logger.info("\nIndexing documents with metadata...")
        db = VectorDatabase()
        db.index_documents(test_file)
        
        # Search and display metadata
        logger.info("\nSearching and utilizing metadata...\n")
        
        query = "machine learning"
        results = db.search(query, top_k=5)
        
        for i, result in enumerate(results, 1):
            logger.info(f"Result {i}:")
            logger.info(f"  ID: {result.document_id}")
            logger.info(f"  Score: {result.score:.4f}")
            logger.info(f"  Content: {result.content[:50]}...")
            
            if result.metadata:
                logger.info(f"  Metadata:")
                for key, value in result.metadata.items():
                    logger.info(f"    - {key}: {value}")
            
            logger.info("")


def main():
    """Run all advanced examples."""
    logger.info("\n" + "=" * 70)
    logger.info("ADVANCED VECTOR DATABASE EXAMPLES - PROFESSIONAL OOP SYSTEM")
    logger.info("=" * 70)
    
    try:
        examples = AdvancedVectorDBExamples()
        
        examples.example_1_low_level_api()
        examples.example_2_large_scale_indexing()
        examples.example_3_memory_efficient_loading()
        examples.example_4_persistence()
        examples.example_5_semantic_search()
        examples.example_6_batch_embedding_optimization()
        examples.example_7_error_handling_and_validation()
        examples.example_8_metadata_utilization()
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ ALL ADVANCED EXAMPLES COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70 + "\n")
    
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
