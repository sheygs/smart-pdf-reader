from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader


class DocumentProcessor:

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        return loader.load()

    @staticmethod
    def get_page_count(documents: List[Document]) -> int:
        return len(documents)
