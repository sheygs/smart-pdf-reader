from dataclasses import dataclass, fields
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    # models available @ https://huggingface.co/spaces/mteb/leaderboard
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
    dpi: int = 150


@dataclass
class UIConfig:
    page_title: str = "Interactive PDF Reader"
    page_icon: str = "📚"
    page_layout: Literal["wide", "centred"] = "wide"


@dataclass
class APIConfig:
    openai_api_key: str = ""
    huggingface_api_token: str = ""
    max_retries: str = ""
    request_timeout: str = ""

    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.huggingface_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        self.max_retries = os.getenv("MAX_RETRIES", "5")
        self.request_timeout = os.getenv("REQUEST_TIMEOUT", "30")
        self.validate()

    def validate(self):
        for field in fields(self):
            if not getattr(self, field.name):
                raise ValueError(f"{field.name} missing in environment config")
        return True


# global instances
model_config = ModelConfig()
pdf_config = PDFConfig()
ui_config = UIConfig()
api_config = APIConfig()
