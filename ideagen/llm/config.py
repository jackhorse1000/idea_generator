from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "openai/gpt-4.1-nano": {"input": 0.1, "output": 0.4},
    "openai/gpt-4.1-mini": {"input": 0.4, "output": 1.6},
    "openai/gpt-4.1": {"input": 2.0, "output": 8.0},
    # Add more as needed
}

class LlmConfig(BaseModel):
    name: str
    api_key: Optional[str] = Field(default=None, exclude=True)
    max_tokens: int = Field(default=10000)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.95)
    response_format: Optional[Dict[str, str]] = Field(default=None)
    base_url: Optional[str] = Field(default="https://openrouter.ai/api/v1")


def get_model_pricing(model_name: str) -> Dict[str, float]:
    model_name = model_name.strip()
    try:
        return MODEL_PRICING[model_name]
    except KeyError:
        raise ValueError(f"Pricing not found for model: {model_name}")
