from app.rag.service import qdrant_service


def get_retriever():
    return qdrant_service


def search_documents(query: str, collection_name: str = "industry_knowledge", top_k: int = 5):
    return qdrant_service.search(query, collection_name=collection_name, top_k=top_k)
