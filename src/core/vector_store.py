from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings


class VectorStore:

    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.store = None

    def create_from_store(self, documents: List[Document]) -> "VectorStore":
        self.store = Chroma.from_documents(documents, self.embeddings)
        return self

    def as_retriever(self, k: int = 2):
        if not self.store:
            raise ValueError("VectorStore not initialized")
        return self.store.as_retriever(search_kwargs={"k": k})
