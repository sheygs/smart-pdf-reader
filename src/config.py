import os
from dataclasses import dataclass
from typing import Literal
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
    max_retries: int = 5
    request_timeout: int = 30

    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.huggingface_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        self.max_retries = int(os.getenv("MAX_RETRIES", "5"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.validate()

    def validate(self):
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing in environment config")
        if not self.huggingface_api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN missing in environment config")
        if self.max_retries < 0:
            raise ValueError("MAX_RETRIES must be non-negative")
        if self.request_timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")
        return True


@dataclass
class RateLimitConfig:
    max_queries_per_session: int = 10
    max_file_size_mb: int = 20
    max_history_length: int = 20
    cooldown_seconds: float = 2.0


# global instances
model_config = ModelConfig()
pdf_config = PDFConfig()
ui_config = UIConfig()
api_config = APIConfig()
rate_limit_config = RateLimitConfig()
