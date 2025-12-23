from typing import Tuple

from openai import OpenAI

from ideagen.config import LlmConfig, get_model_pricing


class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/jackhorse1000/idea_generation",
                "X-Title": "Idea Generation Project",
            },
        )

    def chat(self, model: str, prompt: str, temperature: float, max_tokens: int, top_p: float, response_format=None) -> Tuple[str, float]:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format=response_format,
        )
        text = response.choices[0].message.content
        usage = response.usage
        pricing = get_model_pricing(model)
        cost = (pricing["input"] * usage.prompt_tokens + pricing["output"] * usage.completion_tokens) / 1_000_000
        return text, cost


def call_llm(config: LlmConfig, prompt: str) -> Tuple[str, float]:
    client = OpenRouterClient(api_key=config.api_key, base_url=config.base_url)
    return client.chat(
        model=config.name,
        prompt=prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        response_format=config.response_format,
    )
