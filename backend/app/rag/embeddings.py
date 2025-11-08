from langchain_openai import OpenAIEmbeddings
from app.config import get_settings

settings = get_settings()

def get_embeddings():
    """Get OpenAI embeddings model."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.openai_api_key
    )
