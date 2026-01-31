from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingService
from core.vector_store import VectorStore
from core.conversation import ConversationService
from config import model_config
from utils.file_handlers import FileHandler


class DocumentPipeline:
    """Orchestrates the document processing pipeline."""

    @staticmethod
    def process(uploaded_file):
        """
        Process an uploaded PDF file and return a conversation chain.

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            Conversation chain ready for querying, or None on failure
        """
        # clean up prev. temp files before creating new ones
        FileHandler.cleanup_temp_files()

        temp_path = FileHandler.create_temp_file(uploaded_file)

        documents = DocumentProcessor.load_pdf(temp_path)

        embedding_service = EmbeddingService()
        embeddings = embedding_service.get_embeddings()

        vector_store = VectorStore(embeddings)
        vector_store.create_from_store(documents)
        retriever = vector_store.as_retriever(model_config.retrieval_k)

        conversation_service = ConversationService()
        chain = conversation_service.create_chain(retriever)
        return chain
