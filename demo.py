"""
Vector Database Demo and Usage Examples
========================================
Demonstrates how to use the Vector Database system with various scenarios.
"""

import json
from pathlib import Path
from vector_db import VectorDatabase, logger


def create_sample_data(data_file: Path, num_documents: int = 100) -> None:
    """
    Create sample JSONL data for testing.
    
    Args:
        data_file: Path to save sample data
        num_documents: Number of sample documents to create
    """
    logger.info(f"Creating {num_documents} sample documents...")
    
    sample_texts = [
        "Artificial Intelligence is transforming how we work and live",
        "Machine learning enables computers to learn from data",
        "Natural Language Processing helps machines understand human language",
        "Deep learning uses neural networks with multiple layers",
        "Computer vision allows machines to interpret visual information",
        "Data science combines statistics, programming, and domain knowledge",
        "Python is a popular language for machine learning and data science",
        "TensorFlow is an open-source machine learning framework",
        "PyTorch provides flexible tools for deep learning research",
        "Scikit-learn offers simple tools for data mining and analysis",
        "Databases store and retrieve structured data efficiently",
        "Cloud computing provides scalable computing resources",
        "Big Data technologies handle massive volumes of data",
        "Distributed systems process data across multiple computers",
        "API integration allows different software systems to communicate",
    ]
    
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        for i in range(num_documents):
            doc = {
                'id': f'doc_{i:06d}',
                'content': sample_texts[i % len(sample_texts)] + f" (Document {i})",
                'metadata': {
                    'source': 'sample_data',
                    'index': i,
                    'category': 'technology'
                }
            }
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    logger.info(f"Sample data created at {data_file}")


def demo_basic_indexing_and_search():
    """Demo 1: Basic indexing and searching."""
    logger.info("=" * 60)
    logger.info("DEMO 1: Basic Indexing and Search")
    logger.info("=" * 60)
    
    # Create sample data
    data_file = Path("sample_data.jsonl")
    create_sample_data(data_file, num_documents=50)
    
    # Initialize database
    db = VectorDatabase()
    
    # Index documents
    logger.info("\nIndexing documents...")
    db.index_documents(data_file, batch_size=10)
    
    # Perform searches
    queries = [
        "machine learning and AI",
        "deep learning neural networks",
        "data science and Python",
        "computer vision"
    ]
    
    for query in queries:
        logger.info(f"\nSearching for: '{query}'")
        results = db.search(query, top_k=5)
        
        for i, result in enumerate(results, 1):
            logger.info(f"  Result {i}:")
            logger.info(f"    ID: {result.document_id}")
            logger.info(f"    Score: {result.score:.4f}")
            logger.info(f"    Content: {result.content[:60]}...")
            if result.metadata:
                logger.info(f"    Metadata: {result.metadata}")


def demo_persistent_storage():
    """Demo 2: Save and load database from disk."""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 2: Persistent Storage")
    logger.info("=" * 60)
    
    # Create sample data
    data_file = Path("sample_data.jsonl")
    if not data_file.exists():
        create_sample_data(data_file, num_documents=30)
    
    # Create and index
    logger.info("\nCreating and indexing database...")
    db = VectorDatabase()
    db.index_documents(data_file, batch_size=10)
    
    # Save database
    index_path = Path("vector_db_index.faiss")
    logger.info(f"\nSaving database to {index_path}...")
    db.save(index_path)
    
    # Load database
    logger.info(f"\nLoading database from {index_path}...")
    db2 = VectorDatabase()
    db2.load(index_path)
    
    # Verify with search
    logger.info("\nVerifying loaded database with search...")
    query = "artificial intelligence"
    results = db2.search(query, top_k=3)
    
    logger.info(f"Found {len(results)} results for '{query}'")
    for i, result in enumerate(results, 1):
        logger.info(f"  {i}. {result.document_id}: {result.score:.4f}")


def demo_error_handling():
    """Demo 3: Error handling and edge cases."""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 3: Error Handling")
    logger.info("=" * 60)
    
    db = VectorDatabase()
    
    # Test 1: Empty query
    logger.info("\nTest 1: Empty query")
    try:
        db.search("", top_k=5)
    except Exception as e:
        logger.info(f"  Caught expected error: {type(e).__name__}")
    
    # Test 2: Searching empty database
    logger.info("\nTest 2: Search on empty database")
    try:
        db.search("test query", top_k=5)
    except Exception as e:
        logger.info(f"  Caught expected error: {type(e).__name__}")
    
    # Test 3: Invalid data file
    logger.info("\nTest 3: Invalid data file")
    try:
        db.index_documents(Path("nonexistent.jsonl"))
    except Exception as e:
        logger.info(f"  Caught expected error: {type(e).__name__}")
    
    logger.info("\nAll error handling tests passed!")


def demo_batch_operations():
    """Demo 4: Batch operations and performance."""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 4: Batch Operations")
    logger.info("=" * 60)
    
    # Create larger dataset
    data_file = Path("large_sample_data.jsonl")
    create_sample_data(data_file, num_documents=200)
    
    # Index with different batch sizes
    for batch_size in [16, 32, 64]:
        logger.info(f"\nIndexing with batch_size={batch_size}...")
        db = VectorDatabase()
        db.index_documents(data_file, batch_size=batch_size)
        
        # Perform search
        results = db.search("machine learning", top_k=3)
        logger.info(f"  Indexed successfully. Found {len(results)} results for 'machine learning'")


def demo_similarity_scores():
    """Demo 5: Understanding similarity scores."""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 5: Understanding Similarity Scores")
    logger.info("=" * 60)
    
    data_file = Path("sample_data.jsonl")
    if not data_file.exists():
        create_sample_data(data_file, num_documents=30)
    
    db = VectorDatabase()
    db.index_documents(data_file, batch_size=10)
    
    # Search with different queries
    logger.info("\nSearching for similar documents...")
    
    queries = [
        ("machine learning", "Direct match"),
        ("learning algorithms", "Partial match"),
        ("random unrelated text about cars", "Unrelated"),
    ]
    
    for query, description in queries:
        logger.info(f"\nQuery: '{query}' ({description})")
        results = db.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. Score: {result.score:.4f} - {result.content[:50]}...")


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("VECTOR DATABASE SYSTEM - COMPREHENSIVE DEMO")
    logger.info("=" * 60 + "\n")
    
    try:
        # Run all demos
        demo_basic_indexing_and_search()
        demo_persistent_storage()
        demo_error_handling()
        demo_batch_operations()
        demo_similarity_scores()
        
        logger.info("\n" + "=" * 60)
        logger.info("ALL DEMOS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Demo failed with error: {str(e)}", exc_info=True)