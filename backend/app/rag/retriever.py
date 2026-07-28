from langchain_qdrant import QdrantVectorStore

from app.config.settings import settings
from app.llm.embeddings import get_embedding_model
from app.rag.vectorstore import get_qdrant_client



def get_retriever():

    embedding_model = get_embedding_model()

    client = get_qdrant_client()

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embedding_model,
    )

    retriever = vector_store.as_retriever(
        search_type = "mmr",
        search_kwargs={
            "k": 5,
            "fetch_k":20
        }
    )

    return retriever



# New function for RAG Agent

def search_documents(query):

    retriever = get_retriever()


    documents = retriever.invoke(query)


    results = []


    for doc in documents:

        results.append(
            {
                "content": doc.page_content,
                
            }
        )


    return results