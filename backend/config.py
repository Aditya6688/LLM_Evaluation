from enum import Enum

from pydantic_settings import BaseSettings


class ChunkingStrategy(str, Enum):
    FIXED = "fixed"
    SEMANTIC = "semantic"


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # Models
    generation_model: str = "gpt-4o-mini"
    judge_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma_db"

    # Database
    sqlite_url: str = "sqlite+aiosqlite:///./data/llm_eval.db"

    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    # Self-healing
    faithfulness_threshold: float = 0.7

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.FIXED

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
