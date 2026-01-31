import os

# Disable ChromaDB telemetry before importing
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import uuid
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class VectorStore:

    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.store = None

    def create_from_store(self, documents: List[Document]) -> "VectorStore":
        # Use unique collection name and no persist_directory for in-memory storage
        self.store = Chroma.from_documents(
            documents,
            self.embeddings,
            collection_name=f"pdf_collection_{uuid.uuid4().hex[:8]}",
        )
        return self

    def as_retriever(self, k: int = 2):
        if not self.store:
            raise ValueError("VectorStore not initialized")
        return self.store.as_retriever(search_kwargs={"k": k})
