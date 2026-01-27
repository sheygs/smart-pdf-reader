from langchain_huggingface import HuggingFaceEmbeddings
from config import model_config


class EmbeddingService:

    def __init__(
        self,
        model_name: str = model_config.embedding_model,
        model_device: str = model_config.embedding_device,
        normalize: bool = model_config.normalize_embeddings,
    ):
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": model_device},
            encode_kwargs={"normalize_embeddings": normalize},
        )

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        return self.embeddings
