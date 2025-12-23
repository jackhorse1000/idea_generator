from typing import Tuple

from ideagen.config import LlmConfig
from ideagen.llm.client import call_llm


class BaseGenerator:
    def __init__(self, config: LlmConfig):
        self.config = config

    def generate(self, prompt: str) -> Tuple[str, float]:
        return call_llm(self.config, prompt)
