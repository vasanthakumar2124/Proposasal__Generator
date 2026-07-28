from langchain_qdrant import QdrantVectorStore

from app.config.settings import settings
from app.llm.embeddings import get_embedding_model
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vectorstore import get_qdrant_client


def ingest_pdf(file_path: str):

    documents = load_pdf(file_path)

    chunks = split_documents(documents)

    embedding_model = get_embedding_model()

    client = get_qdrant_client()

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=settings.QDRANT_COLLECTION,
    )

    print("PDF successfully stored in Qdrant.")