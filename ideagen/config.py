import os
from pathlib import Path
from dotenv import load_dotenv
from ideagen.llm.config import LlmConfig


def load_keys(env_path: str | None = None) -> str:
    """Load OPENROUTER_API_KEY from environment or .env files.

    Resolution order:
    1) Provided env_path
    2) Current working directory .env
    3) Repository root .env (two directories up from this file)
    4) Existing environment variables
    """
    key = None
    if env_path:
        load_dotenv(env_path, override=True)
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        # Try CWD .env
        load_dotenv(override=True)
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        # Try repo root .env
        repo_root = Path(__file__).resolve().parents[2]
        root_env = repo_root / ".env"
        if root_env.exists():
            load_dotenv(root_env, override=True)
            key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY not found in environment or .env files")
    return key


class PipelineConfig:
    def __init__(self, api_key: str, model_name: str = "openai/gpt-4.1-nano"):
        self.llm_config = LlmConfig(
            name=model_name,
            api_key=api_key,
            temperature=0.7,
            max_tokens=10000,
            top_p=0.95,
            response_format={"type": "json_object"},
            base_url="https://openrouter.ai/api/v1"
        )
