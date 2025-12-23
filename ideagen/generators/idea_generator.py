import logging
import json
import os
from ideagen.generators.base import BaseGenerator
from ideagen.models.ideas import IdeaResponse
from ideagen.llm.config import LlmConfig

logger = logging.getLogger(__name__)

DEFAULT_PROMPT_PATH = os.path.join(os.path.dirname(__file__), '../prompts/idea_generation.txt')

def load_default_prompt():
    with open(DEFAULT_PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()

class IdeaGenerator(BaseGenerator):
    def __init__(self, model_config: LlmConfig, prompt: str = None):
        if prompt is None:
            prompt = load_default_prompt()
        super().__init__(model_config, prompt)

    def generate(self, rendered_prompt: str) -> IdeaResponse:
        raw_text, _ = super().generate(rendered_prompt=rendered_prompt)
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        # Accept two formats:
        # 1) {"ideas": [{"Name": {...}}, ...]}
        # 2) {"Name": {...}, "Name2": {...}}
        if isinstance(data, dict) and 'ideas' in data:
            # Normalize each idea's detail keys
            normalized_ideas = []
            for idea in data['ideas']:
                name = list(idea.keys())[0]
                details = idea[name]
                normalized_ideas.append({name: self._normalize_details(details)})
            return IdeaResponse.model_validate({"ideas": normalized_ideas})
        elif isinstance(data, dict):
            ideas_list = []
            for name, details in data.items():
                ideas_list.append({name: self._normalize_details(details)})
            return IdeaResponse.model_validate({"ideas": ideas_list})
        else:
            # If model returns a list already
            normalized_list = []
            for idea in data:
                name = list(idea.keys())[0]
                details = idea[name]
                normalized_list.append({name: self._normalize_details(details)})
            return IdeaResponse.model_validate({"ideas": normalized_list})

    def _normalize_details(self, details: dict) -> dict:
        """Normalize model output keys: lowercase and replace spaces with underscores."""
        if not isinstance(details, dict):
            return details
        normalized = {}
        for k, v in details.items():
            # Normalize key: lowercase, remove colons, replace spaces with underscores
            nk = k.strip().lower().replace(':', '').replace(' ', '_')
            normalized[nk] = v
        return normalized
