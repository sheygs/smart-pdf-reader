from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    embedding_model: str = "thenlper/gte-small"  # add as an environment variable
    embedding_device: Literal["cpu", "cuda"] = "cpu"
    llm_temperature: float = 0.2
    retrieval_k: int = 2
    normalize_embeddings: bool = False


@dataclass
class PDFConfig:
    context_page_before: int = 2
    context_page_after: int = 2
    default_page: int = 0


@dataclass
class UIConfig:
    page_title: str = "Interactive PDF Reader"
    page_icon: str = "📚"
    page_layout: Literal["wide", "centred"] = "wide"


@dataclass
class APIConfig:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    huggingface_api_token: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

    def validate(self):
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing in environment config")
        if not self.huggingface_api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN missing in environment config")
        return True
