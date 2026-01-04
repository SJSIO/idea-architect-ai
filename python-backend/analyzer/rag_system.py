"""
RAG (Retrieval-Augmented Generation) System for India-Focused Startup Analysis.

This module provides:
- Document loading from PDF, TXT, DOCX, CSV, JSON files
- Text chunking with overlap for context preservation
- ChromaDB vector store with persistent storage
- Semantic search using sentence-transformers embeddings
- Separate collections for Legal, Market, and Cost agents
"""

import os
from pathlib import Path
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# Agent-specific knowledge directories
LEGAL_KNOWLEDGE_DIR = KNOWLEDGE_BASE_DIR / "legal"
MARKET_KNOWLEDGE_DIR = KNOWLEDGE_BASE_DIR / "market"
COSTS_KNOWLEDGE_DIR = KNOWLEDGE_BASE_DIR / "costs"

# ChromaDB collections
LEGAL_COLLECTION = "legal_knowledge"
MARKET_COLLECTION = "market_knowledge"
COSTS_COLLECTION = "costs_knowledge"

# Embedding model (runs locally, no API key needed)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunk settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def ensure_directories():
    """Create knowledge base directories if they don't exist."""
    for dir_path in [KNOWLEDGE_BASE_DIR, LEGAL_KNOWLEDGE_DIR, MARKET_KNOWLEDGE_DIR, 
                     COSTS_KNOWLEDGE_DIR, CHROMA_DB_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")


def get_chroma_client():
    """Get ChromaDB client with persistent storage."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        ensure_directories()
        
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(CHROMA_DB_DIR),
            anonymized_telemetry=False
        ))
        return client
    except Exception as e:
        logger.error(f"Error creating ChromaDB client: {e}")
        # Fallback to simpler client
        import chromadb
        return chromadb.PersistentClient(path=str(CHROMA_DB_DIR))


def get_embeddings():
    """Get the sentence-transformers embedding function."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        raise


def load_documents_from_directory(directory: Path) -> List:
    """
    Load all supported documents from a directory.
    
    Supported formats: PDF, TXT, DOCX, CSV, JSON, MD
    """
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        CSVLoader,
        JSONLoader,
        UnstructuredWordDocumentLoader,
    )
    
    documents = []
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return documents
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                suffix = file_path.suffix.lower()
                
                if suffix == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                    docs = loader.load()
                    
                elif suffix in [".txt", ".md"]:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                    
                elif suffix == ".csv":
                    loader = CSVLoader(str(file_path))
                    docs = loader.load()
                    
                elif suffix == ".json":
                    loader = JSONLoader(
                        str(file_path),
                        jq_schema=".",
                        text_content=False
                    )
                    docs = loader.load()
                    
                elif suffix in [".docx", ".doc"]:
                    loader = UnstructuredWordDocumentLoader(str(file_path))
                    docs = loader.load()
                    
                else:
                    logger.debug(f"Skipping unsupported file: {file_path}")
                    continue
                
                # Add source metadata
                for doc in docs:
                    doc.metadata["source_file"] = file_path.name
                    doc.metadata["source_dir"] = directory.name
                
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} documents from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue
    
    return documents


def chunk_documents(documents: List, chunk_size: int = CHUNK_SIZE, 
                   chunk_overlap: int = CHUNK_OVERLAP) -> List:
    """Split documents into chunks for better retrieval."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def create_vector_store(collection_name: str, documents: List):
    """Create or update a ChromaDB vector store with documents."""
    from langchain_chroma import Chroma
    
    if not documents:
        logger.warning(f"No documents to add to {collection_name}")
        return None
    
    embeddings = get_embeddings()
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(CHROMA_DB_DIR)
    )
    
    logger.info(f"Created vector store '{collection_name}' with {len(documents)} chunks")
    return vector_store


def get_vector_store(collection_name: str):
    """Get an existing ChromaDB vector store."""
    from langchain_chroma import Chroma
    
    embeddings = get_embeddings()
    
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DB_DIR)
    )
    
    return vector_store


def query_knowledge_base(collection_name: str, query: str, k: int = 5) -> str:
    """
    Query a knowledge base and return formatted context.
    
    Args:
        collection_name: Name of the ChromaDB collection
        query: Search query
        k: Number of results to return
        
    Returns:
        Formatted string of retrieved context
    """
    try:
        vector_store = get_vector_store(collection_name)
        
        # Perform similarity search
        results = vector_store.similarity_search(query, k=k)
        
        if not results:
            return "No relevant information found in knowledge base."
        
        # Format results
        context_parts = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source_file", "Unknown source")
            context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}")
        
        formatted_context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Retrieved {len(results)} results from {collection_name}")
        return formatted_context
        
    except Exception as e:
        logger.error(f"Error querying {collection_name}: {e}")
        return f"Error retrieving from knowledge base: {str(e)}"


# =============================================================================
# Public API Functions for Agents
# =============================================================================

def query_legal_knowledge(query: str, k: int = 5) -> str:
    """
    Query the legal knowledge base for Indian startup law information.
    
    Args:
        query: Search query related to legal aspects
        k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted context from legal documents
    """
    return query_knowledge_base(LEGAL_COLLECTION, query, k)


def query_market_knowledge(query: str, k: int = 5) -> str:
    """
    Query the market knowledge base for Indian market data.
    
    Args:
        query: Search query related to market analysis
        k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted context from market documents
    """
    return query_knowledge_base(MARKET_COLLECTION, query, k)


def query_cost_knowledge(query: str, k: int = 5) -> str:
    """
    Query the cost knowledge base for Indian startup cost benchmarks.
    
    Args:
        query: Search query related to costs and pricing
        k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted context from cost documents
    """
    return query_knowledge_base(COSTS_COLLECTION, query, k)


# =============================================================================
# Knowledge Base Management Functions
# =============================================================================

def load_agent_knowledge(agent_type: str) -> int:
    """
    Load knowledge base for a specific agent.
    
    Args:
        agent_type: One of 'legal', 'market', 'costs'
        
    Returns:
        Number of chunks loaded
    """
    ensure_directories()
    
    agent_configs = {
        "legal": (LEGAL_KNOWLEDGE_DIR, LEGAL_COLLECTION),
        "market": (MARKET_KNOWLEDGE_DIR, MARKET_COLLECTION),
        "costs": (COSTS_KNOWLEDGE_DIR, COSTS_COLLECTION),
    }
    
    if agent_type not in agent_configs:
        raise ValueError(f"Unknown agent type: {agent_type}. Must be one of {list(agent_configs.keys())}")
    
    directory, collection = agent_configs[agent_type]
    
    # Load documents
    documents = load_documents_from_directory(directory)
    
    if not documents:
        logger.warning(f"No documents found in {directory}")
        return 0
    
    # Chunk documents
    chunks = chunk_documents(documents)
    
    # Create vector store
    create_vector_store(collection, chunks)
    
    return len(chunks)


def initialize_knowledge_base() -> dict:
    """
    Initialize all knowledge bases by loading documents from all agent directories.
    
    Returns:
        Dictionary with counts of chunks loaded per agent
    """
    ensure_directories()
    
    results = {}
    for agent_type in ["legal", "market", "costs"]:
        try:
            count = load_agent_knowledge(agent_type)
            results[agent_type] = count
            logger.info(f"Loaded {count} chunks for {agent_type} agent")
        except Exception as e:
            logger.error(f"Error loading {agent_type} knowledge: {e}")
            results[agent_type] = 0
    
    return results


def refresh_knowledge_base(agent_type: Optional[str] = None) -> dict:
    """
    Refresh knowledge base by reloading documents.
    
    Args:
        agent_type: Specific agent to refresh, or None for all
        
    Returns:
        Dictionary with refresh results
    """
    if agent_type:
        count = load_agent_knowledge(agent_type)
        return {agent_type: count}
    else:
        return initialize_knowledge_base()


def get_knowledge_base_status() -> dict:
    """
    Get status of all knowledge bases.
    
    Returns:
        Dictionary with collection statistics
    """
    status = {}
    
    for agent_type, collection_name in [
        ("legal", LEGAL_COLLECTION),
        ("market", MARKET_COLLECTION),
        ("costs", COSTS_COLLECTION)
    ]:
        try:
            vector_store = get_vector_store(collection_name)
            # Get collection info
            collection = vector_store._collection
            count = collection.count() if collection else 0
            status[agent_type] = {
                "collection": collection_name,
                "chunks": count,
                "directory": str(KNOWLEDGE_BASE_DIR / agent_type)
            }
        except Exception as e:
            status[agent_type] = {
                "collection": collection_name,
                "chunks": 0,
                "error": str(e),
                "directory": str(KNOWLEDGE_BASE_DIR / agent_type)
            }
    
    return status


# =============================================================================
# Directory Information for Users
# =============================================================================

def get_upload_locations() -> dict:
    """
    Get the file upload locations for each agent's knowledge base.
    
    Returns:
        Dictionary with paths and supported formats for each agent
    """
    ensure_directories()
    
    return {
        "legal": {
            "path": str(LEGAL_KNOWLEDGE_DIR),
            "description": "Indian legal documents - Companies Act, Startup India, GST, FDI, Labor Laws, IP",
            "supported_formats": ["PDF", "TXT", "DOCX", "MD", "CSV", "JSON"],
            "example_files": [
                "companies_act_2013.pdf",
                "startup_india_policy.pdf",
                "gst_compliance.pdf",
                "fdi_regulations.pdf",
                "labor_laws_india.pdf"
            ]
        },
        "market": {
            "path": str(MARKET_KNOWLEDGE_DIR),
            "description": "Indian market data - NASSCOM reports, industry analysis, demographics, digital adoption",
            "supported_formats": ["PDF", "TXT", "DOCX", "MD", "CSV", "JSON"],
            "example_files": [
                "nasscom_report_2024.pdf",
                "startup_ecosystem_india.pdf",
                "consumer_demographics.csv",
                "digital_india_stats.pdf"
            ]
        },
        "costs": {
            "path": str(COSTS_KNOWLEDGE_DIR),
            "description": "Indian cost benchmarks - salaries, cloud pricing, office rentals, compliance costs",
            "supported_formats": ["PDF", "TXT", "DOCX", "MD", "CSV", "JSON"],
            "example_files": [
                "salary_benchmarks_india.csv",
                "aws_india_pricing.pdf",
                "office_rental_rates.csv",
                "compliance_costs.pdf"
            ]
        }
    }
