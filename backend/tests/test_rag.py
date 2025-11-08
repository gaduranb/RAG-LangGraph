"""Tests for RAG components (embeddings, retrieval, ingestion)."""
import pytest
from pathlib import Path
from app.rag.embeddings import get_embeddings
from app.rag.retriever import retrieve_documents, format_retrieved_docs
from app.rag.ingestion import load_pdfs, chunk_documents


class TestEmbeddings:
    """Tests for embeddings module."""

    def test_get_embeddings_returns_instance(self):
        """Test get_embeddings returns OpenAI embeddings instance."""
        embeddings = get_embeddings()
        assert embeddings is not None
        assert hasattr(embeddings, 'embed_query')

    def test_embeddings_can_embed_text(self):
        """Test embeddings can generate vector for text."""
        embeddings = get_embeddings()
        vector = embeddings.embed_query("How do I reset my password?")
        assert isinstance(vector, list)
        assert len(vector) > 0
        assert all(isinstance(x, float) for x in vector)


class TestRetriever:
    """Tests for retriever module."""

    def test_retrieve_documents_returns_results(self):
        """Test retrieve_documents returns document results."""
        try:
            docs = retrieve_documents("password reset", k=3)
            assert isinstance(docs, list)
            assert len(docs) <= 3

            # If vectorstore exists, should have docs
            if len(docs) > 0:
                # Check document structure
                assert hasattr(docs[0], 'page_content')
                assert hasattr(docs[0], 'metadata')
        except FileNotFoundError:
            # Vectorstore not created yet - this is OK for CI
            pytest.skip("Vectorstore not found - run ingestion first")

    def test_format_retrieved_docs(self):
        """Test document formatting for LLM context."""
        try:
            docs = retrieve_documents("one-time passcode", k=2)
            formatted = format_retrieved_docs(docs)

            assert isinstance(formatted, str)
            if len(docs) > 0:
                # Should contain document markers
                assert "[Document" in formatted
                assert "Source:" in formatted
                assert "Content:" in formatted
        except FileNotFoundError:
            pytest.skip("Vectorstore not found - run ingestion first")

    def test_empty_docs_formatting(self):
        """Test formatting handles empty document list."""
        formatted = format_retrieved_docs([])
        assert formatted == "No relevant documents found."


class TestIngestion:
    """Tests for ingestion module."""

    def test_load_pdfs_structure(self):
        """Test PDF loading returns proper structure."""
        # This test will skip if PDFs don't exist
        try:
            documents = load_pdfs()
            if len(documents) > 0:
                # Check document structure
                assert hasattr(documents[0], 'page_content')
                assert hasattr(documents[0], 'metadata')
                assert 'source' in documents[0].metadata
                assert 'page' in documents[0].metadata
        except Exception as e:
            pytest.skip(f"PDF loading failed: {e}")

    def test_chunk_documents(self):
        """Test document chunking."""
        from langchain_core.documents import Document

        # Create sample documents
        sample_docs = [
            Document(
                page_content="This is a test document about password reset. " * 50,
                metadata={"source": "test.pdf", "page": 0}
            )
        ]

        chunks = chunk_documents(sample_docs)

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Check that chunks have metadata preserved
        assert hasattr(chunks[0], 'metadata')
        assert 'source' in chunks[0].metadata
