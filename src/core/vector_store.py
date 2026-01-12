from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings


class VectorStore:
    def __init__(self, embeddings: Embeddings):
        """
        Initialize vector store

        Args:
            embeddings: Embedding model instance
        """
        self.embeddings = embeddings
        self.store = None

    def create_from_store(self, documents: List[Document]) -> "VectorStore":
        """
        Create vector store from documents

        Args:
            documents: List of LangChain documents

        Returns:
            Self for method chaining
        """
        self.store = Chroma.from_documents(documents, self.embeddings)
        return self

    def as_retriever(self, k: int = 2):
        """
        Get retriever for similarity search

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever instance
        """
        if not self.store:
            raise ValueError("VectorStore not initialized")
        return self.store.as_retriever(search_kwargs={"k": k})
