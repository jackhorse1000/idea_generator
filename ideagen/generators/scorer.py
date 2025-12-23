import logging
import json
import os
from typing import Dict, Optional, Tuple, Any
from ideagen.generators.base import BaseGenerator
from ideagen.models.scores import EnrichedIdeaScore
from ideagen.llm.config import LlmConfig

logger = logging.getLogger(__name__)

DEFAULT_SCORING_PROMPT_PATH = os.path.join(os.path.dirname(__file__), '../prompts/scoring.txt')
DEFAULT_FEEDBACK_PROMPT_PATH = os.path.join(os.path.dirname(__file__), '../prompts/feedback_evaluation.txt')

def load_default_scoring_prompt():
    with open(DEFAULT_SCORING_PROMPT_PATH, 'r') as f:
        return f.read()


def load_default_feedback_prompt():
    with open(DEFAULT_FEEDBACK_PROMPT_PATH, 'r') as f:
        return f.read()


class EffortRevenueScorer(BaseGenerator):
    def __init__(self, model_config: LlmConfig, prompt: str = None):
        if prompt is None:
            prompt = load_default_scoring_prompt()
        super().__init__(model_config, prompt)

    def _parse_response(self, raw_text: str) -> Dict[str, Any]:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def score(self, ideas_response, rendered_prompt: str, batch_size: Optional[int] = 5) -> Dict[str, EnrichedIdeaScore]:
        raw_text, _ = super().generate(rendered_prompt=rendered_prompt)
        data = self._parse_response(raw_text)
        if 'idea_scores' in data:
            return data['idea_scores']
        return data

    def score_with_feedback(self, ideas_response, rendered_prompt: str) -> Tuple[Dict[str, EnrichedIdeaScore], str]:
        raw_text, _ = super().generate(rendered_prompt=rendered_prompt)
        data = self._parse_response(raw_text)
        scores = data.get('idea_scores', data) if isinstance(data, dict) else {}
        feedback = data.get('feedback', '') if isinstance(data, dict) else ''
        return scores, feedback
