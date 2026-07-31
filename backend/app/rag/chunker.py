import re
from typing import Generator


class DocumentChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        paragraphs = re.split(r"\n\s*\n", text.strip())
        chunks = []
        buffer = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            buffer.append(para)
            if len(" ".join(buffer)) >= self.chunk_size:
                chunks.append("\n\n".join(buffer))
                overlap = self._take_overlap(buffer)
                buffer = overlap

        if buffer:
            chunks.append("\n\n".join(buffer))

        return chunks or [text]

    def chunk_documents(self, documents: list[dict]) -> Generator[dict, None, None]:
        for doc in documents:
            content = doc.get("content", doc.get("page_content", ""))
            metadata = doc.get("metadata", {})
            for i, chunk in enumerate(self.chunk_text(content)):
                yield {
                    "content": chunk,
                    "metadata": {**metadata, "chunk_index": i},
                }

    def _take_overlap(self, buffer: list[str]) -> list[str]:
        overlap_chars = 0
        overlap = []
        for para in reversed(buffer):
            overlap.insert(0, para)
            overlap_chars += len(para)
            if overlap_chars >= self.chunk_overlap:
                break
        return overlap
