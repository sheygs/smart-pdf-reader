from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from config import model_config, api_config


class ConversationService:
    """Manages conversational retrieval chain for Q&A"""

    def __init__(
        self,
        temperature: float = model_config.llm_temperature,
        return_sources: bool = True,
    ):
        """
        Initialize conversation service

        Args:
            temperature: LLM temperature (0.0-1.0)
            return_sources: Whether to return source documents
        """
        self.temperature = temperature
        self.return_sources = return_sources
        self.llm = ChatOpenAI(
            temperature=self.temperature, api_key=api_config.openai_api_key
        )

    def create_chain(self, retriever):
        """
        Create conversational retrieval chain

        Args:
            retriever: Vector store retriever

        Returns:
            ConversationalRetrievalChain instance
        """
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=self.return_sources,
        )
        return chain

    @staticmethod
    def query(chain, question: str, history: list) -> dict:
        """
        Execute query against conversation chain

        Args:
            chain: Conversation chain instance
            question: User question
            chat_history: List of (question, answer) tuples

        Returns:
            Response dict with 'answer' and 'source_documents'
        """
        response = chain(
            {"question": question, "chat_history": history},
            return_only_outputs=True,
        )

        return response
