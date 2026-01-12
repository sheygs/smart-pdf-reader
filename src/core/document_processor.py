# from langchain_core.documents import Document
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader


class DocumentProcessor:
    """Handles PDF document loading and processing"""

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """
        Load and parse PDF into LangChain documents

        Args:
            file_path: Path to PDF file

        Returns:
            List of Document objects with page content and metadata
        """

        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents

    @staticmethod
    def get_page_count(documents: List[Document]) -> int:
        return len(documents)
