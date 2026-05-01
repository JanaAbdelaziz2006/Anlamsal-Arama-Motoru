"""
Vector Database System - Main Entry Point
==========================================
This is the main entry point for the Vector Database system.
It provides a command-line interface and practical examples.
"""

import sys
import json
from pathlib import Path
from vector_db import VectorDatabase, logger
import argparse


def create_sample_dataset(output_file: Path, num_docs: int = 100) -> None:
    """Create a sample JSONL dataset for testing."""
    logger.info(f"Creating sample dataset with {num_docs} documents...")
    
    sample_contents = [
        "Python is a versatile programming language used in web development",
        "Machine learning algorithms can learn patterns from data",
        "Neural networks are inspired by biological neurons",
        "Natural language processing enables computers to understand text",
        "Data science combines statistics, mathematics and programming",
        "Cloud computing provides scalable infrastructure",
        "Database systems store and manage large amounts of data",
        "API endpoints allow different software to communicate",
        "DevOps practices combine development and operations",
        "Microservices architecture breaks applications into smaller services",
        "Containerization using Docker simplifies deployment",
        "Kubernetes orchestrates containers in production",
        "Git version control tracks changes in source code",
        "Agile methodology emphasizes iterative development",
        "Test-driven development improves code quality",
        "Design patterns provide reusable solutions to problems",
        "SOLID principles guide object-oriented design",
        "RESTful APIs follow architectural constraints",
        "GraphQL provides flexible data querying",
        "Authentication and authorization secure applications",
    ]
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(num_docs):
            doc = {
                'id': f'doc_{i:06d}',
                'content': sample_contents[i % len(sample_contents)] + f" (Document {i})",
                'metadata': {
                    'doc_number': i,
                    'category': 'technology',
                    'timestamp': '2026-05-01'
                }
            }
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    logger.info(f"✓ Sample dataset created: {output_file}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Professional Vector Database System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py --create-sample      # Create sample dataset
  python start.py --index data.jsonl   # Index a dataset
  python start.py --search "query"     # Search for similar documents
        """
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create sample JSONL dataset for testing'
    )
    
    parser.add_argument(
        '--num-docs',
        type=int,
        default=100,
        help='Number of sample documents to create (default: 100)'
    )
    
    parser.add_argument(
        '--index',
        type=str,
        help='Index documents from a JSONL file'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search for similar documents'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of top results to return (default: 5)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for embedding generation (default: 32)'
    )
    
    parser.add_argument(
        '--save',
        type=str,
        help='Save the indexed database to a file'
    )
    
    parser.add_argument(
        '--load',
        type=str,
        help='Load a previously indexed database'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run a quick demonstration'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("VECTOR DATABASE SYSTEM - PROFESSIONAL OOP IMPLEMENTATION")
    logger.info("=" * 60 + "\n")
    
    try:
        # Create sample dataset
        if args.create_sample:
            create_sample_dataset(Path("sample_data.jsonl"), args.num_docs)
            return
        
        # Initialize database
        db = VectorDatabase()
        
        # Load existing database
        if args.load:
            logger.info(f"Loading database from {args.load}...")
            db.load(Path(args.load))
        
        # Index documents
        if args.index:
            logger.info(f"Indexing documents from {args.index}...")
            db.index_documents(Path(args.index), batch_size=args.batch_size)
            
            if args.save:
                logger.info(f"Saving database to {args.save}...")
                db.save(Path(args.save))
        
        # Search
        if args.search:
            if len(db.documents) == 0:
                logger.error("No documents indexed. Use --index to index documents first.")
                return
            
            logger.info(f"\nSearching for: '{args.search}'")
            logger.info("-" * 60)
            
            results = db.search(args.search, top_k=args.top_k)
            
            if not results:
                logger.info("No results found.")
            else:
                for i, result in enumerate(results, 1):
                    logger.info(f"\n[Result {i}]")
                    logger.info(f"  Document ID: {result.document_id}")
                    logger.info(f"  Similarity Score: {result.score:.6f}")
                    logger.info(f"  Content: {result.content}")
                    if result.metadata:
                        logger.info(f"  Metadata: {result.metadata}")
        
        # Demo mode
        if args.demo:
            demo_vectordb()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Operation completed successfully")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)


def demo_vectordb():
    """Run a quick demonstration of the Vector Database system."""
    logger.info("\n" + "=" * 60)
    logger.info("QUICK DEMONSTRATION")
    logger.info("=" * 60 + "\n")
    
    # Create sample data
    sample_file = Path("demo_sample.jsonl")
    create_sample_dataset(sample_file, num_docs=50)
    
    # Create and index
    logger.info("\n[Step 1] Initializing Vector Database...")
    db = VectorDatabase()
    
    logger.info("[Step 2] Indexing sample documents...")
    db.index_documents(sample_file, batch_size=16)
    
    logger.info(f"[Step 3] Successfully indexed {len(db.documents)} documents\n")
    
    # Perform searches
    demo_queries = [
        "machine learning and artificial intelligence",
        "Python programming language",
        "cloud computing and infrastructure",
    ]
    
    logger.info("[Step 4] Performing semantic searches...\n")
    
    for query in demo_queries:
        logger.info(f"Query: '{query}'")
        results = db.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. [{result.score:.4f}] {result.content[:55]}...")
        
        logger.info("")
    
    # Save database
    index_path = Path("demo_database.faiss")
    logger.info(f"[Step 5] Saving database to {index_path}...")
    db.save(index_path)
    
    logger.info("\n[Step 6] Loading database from disk...")
    db2 = VectorDatabase()
    db2.load(index_path)
    
    # Verify
    logger.info(f"✓ Database loaded successfully with {len(db2.documents)} documents")
    
    logger.info("\n" + "-" * 60)
    logger.info("Demo completed successfully!")
    logger.info("-" * 60)


if __name__ == "__main__":
    # If no arguments provided, show usage
    if len(sys.argv) == 1:
        logger.info("Vector Database System - Professional OOP Implementation\n")
        logger.info("Usage: python start.py [options]\n")
        logger.info("Quick Examples:")
        logger.info("  python start.py --demo                    # Run demonstration")
        logger.info("  python start.py --create-sample           # Create sample data")
        logger.info("  python start.py --index data.jsonl --search 'query'")
        logger.info("\nFor full help: python start.py --help\n")
        
        # Run demo by default
        logger.info("Running demo mode...\n")
        demo_vectordb()
    else:
        main()
