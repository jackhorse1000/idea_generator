import logging
from typing import Tuple
from openai import OpenAI
from .config import LlmConfig, get_model_pricing

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        # Include default headers required by OpenRouter for authentication context
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/jackhorse1000/idea_generation",
                "X-Title": "Idea Generation Project"
            }
        )

    def create_chat_completion(self, model: str, prompt: str, temperature: float, max_tokens: int, top_p: float, response_format=None) -> Tuple[str, float]:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format=response_format
        )
        response_text = response.choices[0].message.content
        usage = response.usage
        pricing = get_model_pricing(model)
        input_cost = (pricing["input"] * usage.prompt_tokens) / 1_000_000
        output_cost = (pricing["output"] * usage.completion_tokens) / 1_000_000
        cost = input_cost + output_cost
        return response_text, cost

def call_model_completion(model_config: LlmConfig, prompt: str) -> Tuple[str, float]:
    client = OpenRouterClient(api_key=model_config.api_key, base_url=model_config.base_url)
    return client.create_chat_completion(
        model=model_config.name,
        prompt=prompt,
        temperature=model_config.temperature,
        max_tokens=model_config.max_tokens,
        top_p=model_config.top_p,
        response_format=model_config.response_format
    )
