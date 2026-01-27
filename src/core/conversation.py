from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from config import model_config, api_config


class ConversationService:

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
            max_retries=int(api_config.max_retries),
            request_timeout=int(api_config.request_timeout),
        )

    def create_chain(self, retriever):
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=self.return_sources,
        )
        return chain

    @staticmethod
    def query(chain, question: str, history: list) -> dict:
        response = chain.invoke(
            {"question": question, "chat_history": history},
            return_only_outputs=True,
        )
        return response
