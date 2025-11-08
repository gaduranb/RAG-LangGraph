from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.rag.embeddings import get_embeddings

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PDFS_DIR = DATA_DIR / "pdfs"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

def load_pdfs() -> List[Document]:
    """Load all PDFs from the pdfs directory."""
    documents = []

    if not PDFS_DIR.exists():
        print(f"⚠️  PDFs directory not found: {PDFS_DIR}")
        return documents

    pdf_files = list(PDFS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"⚠️  No PDF files found in {PDFS_DIR}")
        return documents

    print(f"📄 Found {len(pdf_files)} PDF(s)")

    for pdf_file in pdf_files:
        print(f"  Loading: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        # Add metadata
        for doc in docs:
            doc.metadata["source"] = pdf_file.name
            doc.metadata["file_path"] = str(pdf_file)

        documents.extend(docs)
        print(f"    ✓ Loaded {len(docs)} pages")

    return documents

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    print(f"✂️  Split into {len(chunks)} chunks")

    return chunks

def create_vectorstore(chunks: List[Document]) -> Chroma:
    """Create and populate Chroma vectorstore."""
    embeddings = get_embeddings()

    # Ensure directory exists
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"🔢 Creating embeddings and storing in Chroma...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
        collection_name="banking_security_docs"
    )

    print(f"✓ Vectorstore created at {VECTORSTORE_DIR}")
    print(f"✓ Total documents in vectorstore: {vectorstore._collection.count()}")

    return vectorstore

def ingest_pdfs():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("🚀 Starting PDF Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load PDFs
    documents = load_pdfs()

    if not documents:
        print("❌ No documents to process. Exiting.")
        return

    print(f"✓ Total pages loaded: {len(documents)}")

    # Step 2: Chunk documents
    chunks = chunk_documents(documents)

    # Step 3: Create vectorstore
    vectorstore = create_vectorstore(chunks)

    print("=" * 60)
    print("✅ Ingestion Complete!")
    print("=" * 60)

    return vectorstore

if __name__ == "__main__":
    ingest_pdfs()
