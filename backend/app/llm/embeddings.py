import os

from dotenv import load_dotenv
from huggingface_hub import login
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

hf_token = os.getenv("HF_TOKEN")

if hf_token:
    login(token=hf_token)

def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    return embedding_model