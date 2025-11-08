from pathlib import Path
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.rag.embeddings import get_embeddings

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

_vectorstore: Optional[Chroma] = None

def get_vectorstore() -> Chroma:
    """Get or create Chroma vectorstore instance."""
    global _vectorstore

    if _vectorstore is None:
        embeddings = get_embeddings()

        if not VECTORSTORE_DIR.exists():
            raise FileNotFoundError(
                f"Vectorstore not found at {VECTORSTORE_DIR}. "
                "Please run ingestion first: python -m app.rag.ingestion"
            )

        _vectorstore = Chroma(
            persist_directory=str(VECTORSTORE_DIR),
            embedding_function=embeddings,
            collection_name="banking_security_docs"
        )

    return _vectorstore

def retrieve_documents(query: str, k: int = 3) -> List[Document]:
    """
    Retrieve relevant documents for a query.

    Args:
        query: The search query
        k: Number of documents to retrieve

    Returns:
        List of relevant documents with metadata
    """
    vectorstore = get_vectorstore()

    # Similarity search
    docs = vectorstore.similarity_search(query, k=k)

    return docs

def retrieve_with_scores(query: str, k: int = 3) -> List[tuple[Document, float]]:
    """
    Retrieve relevant documents with similarity scores.

    Args:
        query: The search query
        k: Number of documents to retrieve

    Returns:
        List of (document, score) tuples
    """
    vectorstore = get_vectorstore()

    # Similarity search with scores
    docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)

    return docs_with_scores

def format_retrieved_docs(docs: List[Document]) -> str:
    """Format retrieved documents into a string for the LLM."""
    if not docs:
        return "No relevant documents found."

    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        content = doc.page_content.strip()

        formatted.append(
            f"[Document {i}]\n"
            f"Source: {source} (Page {page + 1})\n"
            f"Content: {content}\n"
        )

    return "\n".join(formatted)
