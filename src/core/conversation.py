from typing import List, Tuple, Dict, Any, Callable, Union

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.retrievers import BaseRetriever

from config import model_config, api_config


class ConversationService:
    """
    Conversational retrieval service using LCEL (LangChain Expression Language).
    Replaces the deprecated ConversationalRetrievalChain.
    """

    def __init__(
        self,
        temperature: float = model_config.llm_temperature,
        return_sources: bool = True,
    ):
        self.temperature = temperature
        self.return_sources = return_sources
        self.llm = ChatOpenAI(
            temperature=self.temperature,
            api_key=api_config.openai_api_key,
            max_retries=api_config.max_retries,
            timeout=api_config.request_timeout,
        )

    def create_chain(self, retriever: BaseRetriever) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Create an LCEL-based conversational retrieval chain.

        Args:
            retriever: The vector store retriever to use for document lookup

        Returns:
            A callable chain that accepts question and chat_history
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant. Answer the question based on the following context. "
             "If you cannot find the answer in the context, say so.\n\n"
             "Context:\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

        def format_docs(docs: List) -> str:
            """Format retrieved documents into a single string."""
            return "\n\n".join(doc.page_content for doc in docs)

        # Store retriever for use in chain with sources
        self._retriever = retriever

        # Build LCEL chain
        answer_chain = (
            {
                "context": lambda x: format_docs(retriever.invoke(x["question"])),
                "chat_history": lambda x: x["chat_history"],
                "question": lambda x: x["question"],
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        if self.return_sources:
            return self._wrap_with_sources(retriever, answer_chain)

        return lambda inputs: {"answer": answer_chain.invoke(inputs), "source_documents": []}

    def _wrap_with_sources(
        self,
        retriever: BaseRetriever,
        answer_chain
    ) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Wrap the answer chain to also return source documents.

        Args:
            retriever: The retriever to get source documents
            answer_chain: The LCEL chain that produces answers

        Returns:
            A callable that returns both answer and source documents
        """
        def get_answer_with_sources(inputs: Dict[str, Any]) -> Dict[str, Any]:
            # Get source documents
            docs = retriever.invoke(inputs["question"])
            # Get answer
            answer = answer_chain.invoke(inputs)
            return {"answer": answer, "source_documents": docs}

        return get_answer_with_sources

    @staticmethod
    def format_history(history: List[Tuple[str, str]]) -> List[Union[HumanMessage, AIMessage]]:
        """
        Convert history tuples to LangChain message format.

        Args:
            history: List of (human_message, ai_message) tuples

        Returns:
            List of LangChain message objects
        """
        messages = []
        for human, ai in history:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))
        return messages

    def query(
        self,
        chain: Callable[[Dict[str, Any]], Dict[str, Any]],
        question: str,
        history: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Query the conversation chain.

        Args:
            chain: The conversation chain created by create_chain()
            question: The user's question
            history: List of (question, answer) tuples from previous conversation

        Returns:
            Dict with 'answer' and 'source_documents' keys
        """
        formatted_history = self.format_history(history)
        return chain({
            "question": question,
            "chat_history": formatted_history
        })
