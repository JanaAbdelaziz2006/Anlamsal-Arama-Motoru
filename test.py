#!/usr/bin/env python3
"""
Professional Semantic Search Interface
═══════════════════════════════════════════════════════════════════════════

Modern Vector Database - Interactive Semantic Search Engine
A production-grade interface for semantic search using FAISS and embeddings.

Features:
  • Automatic data indexing from JSONL
  • Real-time semantic search
  • Professional interactive UI
  • Comprehensive error handling
  • Performance metrics
  • Type safety with type hints

Author: Senior Python Developer & AI Expert
Date: May 1, 2026
"""

import sys
from pathlib import Path
from typing import Optional, List
import time
import os

# Import vector database system
from vector_db import VectorDatabase, SearchResult, logger


# ═════════════════════════════════════════════════════════════════════════════
# UI UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

class SemanticSearchUI:
    """Professional user interface for semantic search."""
    
    # Color and formatting constants
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Special characters
    SEPARATOR_MAIN = "═" * 80
    SEPARATOR_SUB = "─" * 80
    ARROW = "→"
    BULLET = "•"
    SCORE_BAR = "█"
    
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header() -> None:
        """Print application header."""
        header = f"""
{SemanticSearchUI.BOLD}{SemanticSearchUI.CYAN}
╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║       🔍 MODERN VECTOR DATABASE - SEMANTIC SEARCH ENGINE 🔍                ║
║                                                                             ║
║   Büyük veri kümelerinde anlamsal arama yapabilen ölçeklenebilir bir sistem ║
║   Search millions of documents using semantic similarity                    ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
{SemanticSearchUI.RESET}"""
        print(header)
    
    @staticmethod
    def print_separator(style: str = "main") -> None:
        """Print separator line."""
        sep = SemanticSearchUI.SEPARATOR_MAIN if style == "main" else SemanticSearchUI.SEPARATOR_SUB
        print(f"{SemanticSearchUI.CYAN}{sep}{SemanticSearchUI.RESET}")
    
    @staticmethod
    def print_status_message(message: str, status: str = "info") -> None:
        """
        Print status message with color coding.
        
        Args:
            message: Message to display
            status: 'info', 'success', 'warning', 'error'
        """
        colors = {
            "info": SemanticSearchUI.BLUE,
            "success": SemanticSearchUI.GREEN,
            "warning": SemanticSearchUI.YELLOW,
            "error": SemanticSearchUI.RED,
        }
        
        symbols = {
            "info": "[ℹ]",
            "success": "[✓]",
            "warning": "[⚠]",
            "error": "[✗]",
        }
        
        color = colors.get(status, SemanticSearchUI.BLUE)
        symbol = symbols.get(status, "[•]")
        
        print(f"{color}{symbol} {message}{SemanticSearchUI.RESET}")
    
    @staticmethod
    def print_results(results: List[SearchResult], query: str, search_time: float) -> None:
        """
        Display search results in professional format.
        
        Args:
            results: List of SearchResult objects
            query: Original query string
            search_time: Time taken for search in seconds
        """
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}Query:{SemanticSearchUI.RESET} {query}")
        print(f"{SemanticSearchUI.CYAN}Search Time: {search_time*1000:.2f}ms{SemanticSearchUI.RESET}")
        
        if not results:
            SemanticSearchUI.print_status_message("No results found", "warning")
            return
        
        SemanticSearchUI.print_separator("sub")
        
        for i, result in enumerate(results, 1):
            # Score visualization
            if result.score < 0.40:  # Threshold for relevance
                continue
            score_pct = int(result.score * 100)
            score_bar = SemanticSearchUI.SCORE_BAR * (score_pct // 5)
            empty_bar = " " * ((100 // 5) - (score_pct // 5))
            
            print(f"\n{SemanticSearchUI.BOLD}Result #{i}{SemanticSearchUI.RESET}")
            print(f"  {SemanticSearchUI.ARROW} ID: {SemanticSearchUI.BLUE}{result.document_id}{SemanticSearchUI.RESET}")
            print(f"  {SemanticSearchUI.ARROW} Similarity Score: {SemanticSearchUI.GREEN}{result.score:.4f}{SemanticSearchUI.RESET} "
                  f"[{SemanticSearchUI.GREEN}{score_bar}{SemanticSearchUI.RESET}{empty_bar}] {score_pct}%")
            
            # Display metadata if available
            if result.metadata:
                print(f"  {SemanticSearchUI.ARROW} Metadata: {result.metadata}")
            
            # Display content (truncated if too long)
            content_preview = result.content[:120]
            if len(result.content) > 120:
                content_preview += "..."
            
            print(f"  {SemanticSearchUI.ARROW} Content:\n     {SemanticSearchUI.CYAN}{content_preview}{SemanticSearchUI.RESET}")
        
        SemanticSearchUI.print_separator("sub")
    
    @staticmethod
    def print_welcome_message(doc_count: int) -> None:
        """Display welcome message with database info."""
        SemanticSearchUI.clear_screen()
        SemanticSearchUI.print_header()
        
        print(f"\n{SemanticSearchUI.GREEN}✓ Database initialized successfully{SemanticSearchUI.RESET}")
        print(f"  {SemanticSearchUI.BULLET} Documents indexed: {SemanticSearchUI.BOLD}{doc_count}{SemanticSearchUI.RESET}")
        print(f"  {SemanticSearchUI.BULLET} Model: sentence-transformers (all-MiniLM-L6-v2)")
        print(f"  {SemanticSearchUI.BULLET} Index: FAISS (IndexHNSWFlat)")
        print(f"  {SemanticSearchUI.BULLET} Embedding dimension: 384-D vectors")
        
        SemanticSearchUI.print_separator()
        
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}How to use:{SemanticSearchUI.RESET}")
        print(f"  1. Type your semantic query (e.g., 'BTÜ'de nasıl başarılı olunur?')")
        print(f"  2. Press Enter to search")
        print(f"  3. View top 3 most similar documents")
        print(f"  4. Type 'q' to quit")
        print(f"  5. Type 'clear' to clear screen")
        
        SemanticSearchUI.print_separator()
    
    @staticmethod
    def print_input_prompt() -> None:
        """Print input prompt."""
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.GREEN}Enter query (or 'q' to quit):{SemanticSearchUI.RESET}")
        print(f"{SemanticSearchUI.BLUE}>>> {SemanticSearchUI.RESET}", end="", flush=True)


# ═════════════════════════════════════════════════════════════════════════════
# SEMANTIC SEARCH ENGINE
# ═════════════════════════════════════════════════════════════════════════════

class SemanticSearchEngine:
    """
    High-performance semantic search engine for vector database.
    
    Manages vector database initialization, indexing, and search operations.
    """
    
    def __init__(self, data_file: Path = Path("data.jsonl"), top_k: int = 3):
        """
        Initialize semantic search engine.
        
        Args:
            data_file: Path to JSONL data file
            top_k: Number of top results to return
            
        Raises:
            FileNotFoundError: If data file not found
            ValueError: If data file is empty or invalid
        """
        self.data_file = data_file
        self.top_k = top_k
        self.db: Optional[VectorDatabase] = None
        self.doc_count: int = 0
        
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """
        Initialize vector database with error handling.
        
        Raises:
            FileNotFoundError: If data file not found
            ValueError: If data file is empty
        """
        try:
            # Check if data file exists
            if not self.data_file.exists():
                raise FileNotFoundError(
                    f"Data file not found: {self.data_file}\n"
                    f"Please ensure data.jsonl exists in the project directory."
                )
            
            # Check if file is not empty
            if self.data_file.stat().st_size == 0:
                raise ValueError(
                    f"Data file is empty: {self.data_file}\n"
                    f"Please populate data.jsonl with JSONL formatted data."
                )
            
            # Initialize vector database
            logger.info(f"Initializing VectorDatabase from {self.data_file}")
            self.db = VectorDatabase()
            
            # Index documents
            logger.info(f"Indexing documents from {self.data_file}")
            self.db.index_documents(
                self.data_file,
                batch_size=32
            )
            
            # Get document count
            self.doc_count = len(self.db.documents)
            
            if self.doc_count == 0:
                raise ValueError(
                    "No valid documents found in data file.\n"
                    "Ensure each line is valid JSON with 'id' and 'content' fields."
                )
            
            logger.info(f"Successfully indexed {self.doc_count} documents")
            SemanticSearchUI.print_status_message(
                f"Indexed {self.doc_count} documents successfully",
                "success"
            )
        
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid data: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise
    
    def search(self, query: str) -> tuple[List[SearchResult], float]:
        """
        Perform semantic search.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (search_results, search_time_in_seconds)
            
        Raises:
            ValueError: If query is empty
            Exception: If search fails
        """
        try:
            if not query.strip():
                raise ValueError("Query cannot be empty")
            
            if self.db is None:
                raise RuntimeError("Database not initialized")
            
            start_time = time.time()
            results = self.db.search(query, top_k=self.top_k)
            search_time = time.time() - start_time
            
            logger.info(f"Search completed for query: '{query}' in {search_time*1000:.2f}ms")
            return results, search_time
        
        except ValueError as e:
            logger.warning(f"Invalid query: {e}")
            raise
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise
    
    def get_statistics(self) -> dict:
        """
        Get engine statistics.
        
        Returns:
            Dictionary with engine statistics
        """
        return {
            "documents_indexed": self.doc_count,
            "data_file": str(self.data_file),
            "top_k": self.top_k,
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": 384,
            "index_type": "FAISS IndexHNSWFlat"
        }


# ═════════════════════════════════════════════════════════════════════════════
# INTERACTIVE SEARCH LOOP
# ═════════════════════════════════════════════════════════════════════════════

class InteractiveSearchLoop:
    """
    Interactive search loop for user interface.
    
    Manages user input, query processing, and result display.
    """
    
    def __init__(self, engine: SemanticSearchEngine):
        """
        Initialize interactive loop.
        
        Args:
            engine: SemanticSearchEngine instance
        """
        self.engine = engine
        self.query_count = 0
        self.total_search_time = 0.0
    
    def run(self) -> None:
        """
        Run interactive search loop.
        
        Continues until user presses 'q'.
        """
        SemanticSearchUI.print_welcome_message(self.engine.doc_count)
        
        try:
            while True:
                SemanticSearchUI.print_input_prompt()
                
                user_input = input().strip()
                
                # Handle special commands
                if user_input.lower() == 'q':
                    self._print_exit_message()
                    break
                
                elif user_input.lower() == 'clear':
                    SemanticSearchUI.clear_screen()
                    SemanticSearchUI.print_header()
                    continue
                
                elif user_input.lower() == 'stats':
                    self._print_statistics()
                    continue
                
                elif user_input.lower() == 'help':
                    self._print_help()
                    continue
                
                elif not user_input:
                    SemanticSearchUI.print_status_message("Please enter a query", "warning")
                    continue
                
                # Process search query
                self._process_query(user_input)
        
        except KeyboardInterrupt:
            self._print_interrupt_message()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            SemanticSearchUI.print_status_message(
                f"An unexpected error occurred: {e}",
                "error"
            )
    
    def _process_query(self, query: str) -> None:
        """
        Process a search query.
        
        Args:
            query: User's search query
        """
        try:
            results, search_time = self.engine.search(query)
            self.query_count += 1
            self.total_search_time += search_time
            
            SemanticSearchUI.print_results(results, query, search_time)
        
        except ValueError as e:
            SemanticSearchUI.print_status_message(str(e), "error")
        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            SemanticSearchUI.print_status_message(
                f"Search failed: {str(e)}",
                "error"
            )
    
    def _print_statistics(self) -> None:
        """Display search statistics."""
        SemanticSearchUI.print_separator("sub")
        
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}Search Statistics:{SemanticSearchUI.RESET}")
        
        stats = self.engine.get_statistics()
        print(f"  {SemanticSearchUI.BULLET} Documents indexed: {stats['documents_indexed']}")
        print(f"  {SemanticSearchUI.BULLET} Queries executed: {self.query_count}")
        
        if self.query_count > 0:
            avg_time = self.total_search_time / self.query_count
            print(f"  {SemanticSearchUI.BULLET} Average search time: {avg_time*1000:.2f}ms")
            print(f"  {SemanticSearchUI.BULLET} Total search time: {self.total_search_time*1000:.2f}ms")
        
        print(f"  {SemanticSearchUI.BULLET} Embedding dimension: {stats['embedding_dimension']}")
        print(f"  {SemanticSearchUI.BULLET} Index type: {stats['index_type']}")
        
        SemanticSearchUI.print_separator("sub")
    
    def _print_help(self) -> None:
        """Display help information."""
        SemanticSearchUI.print_separator("sub")
        
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}Available Commands:{SemanticSearchUI.RESET}")
        print(f"  {SemanticSearchUI.BULLET} Type any query to search")
        print(f"  {SemanticSearchUI.BULLET} 'stats' - View search statistics")
        print(f"  {SemanticSearchUI.BULLET} 'clear' - Clear screen")
        print(f"  {SemanticSearchUI.BULLET} 'help' - Show this help message")
        print(f"  {SemanticSearchUI.BULLET} 'q' - Quit application")
        
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}Example Queries:{SemanticSearchUI.RESET}")
        print(f"  {SemanticSearchUI.BULLET} 'BTÜ'de nasıl başarılı olunur?'")
        print(f"  {SemanticSearchUI.BULLET} 'Vektör veritabanı nedir?'")
        print(f"  {SemanticSearchUI.BULLET} 'Machine learning uygulamaları'")
        print(f"  {SemanticSearchUI.BULLET} 'Yapay zeka ve etik'")
        
        SemanticSearchUI.print_separator("sub")
    
    def _print_exit_message(self) -> None:
        """Print exit message with summary."""
        print()
        SemanticSearchUI.print_separator()
        
        print(f"\n{SemanticSearchUI.GREEN}✓ Goodbye!{SemanticSearchUI.RESET}")
        print(f"\n{SemanticSearchUI.BOLD}{SemanticSearchUI.YELLOW}Session Summary:{SemanticSearchUI.RESET}")
        print(f"  {SemanticSearchUI.BULLET} Queries executed: {self.query_count}")
        
        if self.query_count > 0:
            avg_time = self.total_search_time / self.query_count
            print(f"  {SemanticSearchUI.BULLET} Average search time: {avg_time*1000:.2f}ms")
        
        print(f"  {SemanticSearchUI.BULLET} Documents searched: {self.engine.doc_count}")
        
        print(f"\n{SemanticSearchUI.CYAN}Thank you for using the Semantic Search Engine!{SemanticSearchUI.RESET}\n")
        
        SemanticSearchUI.print_separator()
    
    def _print_interrupt_message(self) -> None:
        """Print interrupt message."""
        print(f"\n\n{SemanticSearchUI.YELLOW}⚠ Application interrupted by user{SemanticSearchUI.RESET}\n")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """
    Main entry point for semantic search application.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize semantic search engine
        engine = SemanticSearchEngine(
            data_file=Path("data.jsonl"),
            top_k=3
        )
        
        # Run interactive loop
        loop = InteractiveSearchLoop(engine)
        loop.run()
        
        return 0
    
    except FileNotFoundError as e:
        SemanticSearchUI.clear_screen()
        SemanticSearchUI.print_header()
        SemanticSearchUI.print_status_message(str(e), "error")
        print()
        return 1
    
    except ValueError as e:
        SemanticSearchUI.clear_screen()
        SemanticSearchUI.print_header()
        SemanticSearchUI.print_status_message(str(e), "error")
        print()
        return 1
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        SemanticSearchUI.print_status_message(
            f"Fatal error: {e}",
            "error"
        )
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())