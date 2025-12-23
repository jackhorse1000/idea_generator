import json
from typing import Any, Dict, Tuple

from ideagen.config import LlmConfig
from ideagen.generators.base import BaseGenerator


class EffortRevenueScorer(BaseGenerator):
    def __init__(self, config: LlmConfig):
        super().__init__(config)

    def score(self, ideas_response, rendered_prompt: str) -> Dict[str, Any]:
        raw_text, _ = super().generate(rendered_prompt)
        data = self._parse(raw_text)
        return data.get("idea_scores", data)

    def score_with_feedback(self, ideas_response, rendered_prompt: str) -> Tuple[Dict[str, Any], str]:
        raw_text, _ = super().generate(rendered_prompt)
        data = self._parse(raw_text)
        scores = data.get("idea_scores", data) if isinstance(data, dict) else {}
        feedback = data.get("feedback", "") if isinstance(data, dict) else ""
        return scores, feedback

    def _parse(self, raw_text: str) -> Dict[str, Any]:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
