import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv


MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "openai/gpt-4.1-nano": {"input": 0.1, "output": 0.4},
    "openai/gpt-4.1-mini": {"input": 0.4, "output": 1.6},
    "openai/gpt-4.1": {"input": 2.0, "output": 8.0},
}

DEFAULT_MODEL = "openai/gpt-4.1-nano"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def get_model_pricing(model_name: str) -> Dict[str, float]:
    model_name = model_name.strip()
    if model_name not in MODEL_PRICING:
        raise ValueError(f"Pricing not found for model: {model_name}")
    return MODEL_PRICING[model_name]


def load_api_key(env_path: str | None = None) -> str:
    key = None
    if env_path:
        load_dotenv(env_path, override=True)
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        load_dotenv(override=True)
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        repo_root = Path(__file__).resolve().parents[1]
        root_env = repo_root / ".env"
        if root_env.exists():
            load_dotenv(root_env, override=True)
            key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY not found in environment or .env files")
    return key


@dataclass
class LlmConfig:
    name: str = DEFAULT_MODEL
    api_key: Optional[str] = None
    max_tokens: int = 10000
    temperature: float = 0.7
    top_p: float = 0.95
    response_format: Optional[Dict[str, str]] = field(default_factory=lambda: {"type": "json_object"})
    base_url: str = DEFAULT_BASE_URL


@dataclass
class PipelineConfig:
    api_key: Optional[str] = None
    model: str = DEFAULT_MODEL
    skip_dedupe: bool = False
    skip_score: bool = False
    similarity_threshold: float = 0.8
    generation_prompt: Optional[str] = None
    evaluation_prompt: Optional[str] = None

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = load_api_key()

    def to_llm_config(self) -> LlmConfig:
        return LlmConfig(name=self.model, api_key=self.api_key)
