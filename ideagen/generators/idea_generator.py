import json

from ideagen.config import LlmConfig
from ideagen.generators.base import BaseGenerator
from ideagen.models.ideas import IdeaResponse


class IdeaGenerator(BaseGenerator):
    def __init__(self, config: LlmConfig):
        super().__init__(config)

    def generate(self, rendered_prompt: str) -> IdeaResponse:
        raw_text, _ = super().generate(rendered_prompt)
        return self._parse(raw_text)

    def _parse(self, raw_text: str) -> IdeaResponse:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        if isinstance(data, dict) and "ideas" in data:
            ideas = [
                {name: self._normalize_keys(details)}
                for idea in data["ideas"]
                for name, details in [next(iter(idea.items()))]
            ]
        elif isinstance(data, dict):
            ideas = [{name: self._normalize_keys(details)} for name, details in data.items()]
        else:
            ideas = [
                {name: self._normalize_keys(details)}
                for idea in data
                for name, details in [next(iter(idea.items()))]
            ]
        return IdeaResponse(ideas=ideas)

    def _normalize_keys(self, details: dict) -> dict:
        if not isinstance(details, dict):
            return details
        return {
            k.strip().lower().replace(":", "").replace(" ", "_"): v
            for k, v in details.items()
        }
