from app.rag.chunker import DocumentChunker


class TestDocumentChunker:
    def setup_method(self):
        self.chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)

    def test_chunk_short_text(self):
        chunks = self.chunker.chunk_text("Short text")
        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_chunk_long_text(self):
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three.\n\nParagraph four.\n\nParagraph five."
        chunks = self.chunker.chunk_text(text)
        assert len(chunks) >= 1

    def test_empty_text(self):
        chunks = self.chunker.chunk_text("")
        assert chunks == [""]

    def test_chunk_documents(self):
        docs = [
            {"content": "Doc one content", "metadata": {"source": "test1"}},
            {"content": "Doc two content", "metadata": {"source": "test2"}},
        ]
        results = list(self.chunker.chunk_documents(docs))
        assert len(results) >= 2
        assert all("content" in r and "metadata" in r for r in results)
