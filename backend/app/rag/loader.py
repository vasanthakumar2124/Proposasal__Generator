from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from docx import Document


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents


def load_docx(file_path: str):
    document = Document(file_path)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    return [{"page_content": text, "metadata": {"source": str(Path(file_path).name)}}]


def load_text_file(file_path: str):
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    return [{"page_content": text, "metadata": {"source": Path(file_path).name}}]
