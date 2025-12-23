import logging
from typing import Any, Tuple
from ideagen.llm.client import call_model_completion
from ideagen.llm.config import LlmConfig
from ideagen.models.execution import ExecutionMetadata

logger = logging.getLogger(__name__)

class BaseGenerator:
    """Base LLM generator.

    Receives an already-rendered prompt, calls the model, and returns raw text + metadata.
    Subclasses are responsible for parsing the raw text into structured models.
    """

    def __init__(self, model_config: LlmConfig, prompt: str):
        self.model_config = model_config
        self.prompt = prompt
        logger.info(f"Initialized {self.__class__.__name__}")

    def generate(self, rendered_prompt: str) -> Tuple[str, ExecutionMetadata]:
        response_text, cost = call_model_completion(self.model_config, rendered_prompt)
        metadata = ExecutionMetadata(
            cost=cost,
            duration_seconds=0.0,
            errors=[],
            prompt=rendered_prompt,
            response_text=response_text
        )
        return response_text, metadata
