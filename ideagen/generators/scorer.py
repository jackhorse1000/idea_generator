import logging
import json
from typing import Dict, Optional
from ideagen.generators.base import BaseGenerator
from ideagen.models.scores import EnrichedIdeaScore
from ideagen.llm.config import LlmConfig

logger = logging.getLogger(__name__)

DEFAULT_SCORING_PROMPT_PATH = __import__('os').path.join(__import__('os').path.dirname(__file__), '../prompts/scoring.txt')

def load_default_scoring_prompt():
    with open(DEFAULT_SCORING_PROMPT_PATH, 'r') as f:
        return f.read()

class EffortRevenueScorer(BaseGenerator):
    def __init__(self, model_config: LlmConfig, prompt: str = None):
        if prompt is None:
            prompt = load_default_scoring_prompt()
        super().__init__(model_config, prompt)

    def score(self, ideas_response, rendered_prompt: str, batch_size: Optional[int] = 5) -> Dict[str, EnrichedIdeaScore]:
        raw_text, _ = super().generate(rendered_prompt=rendered_prompt)
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except Exception:
            return {}
        if isinstance(data, dict) and 'idea_scores' in data:
            return data['idea_scores']
        # Fallback: try return the whole dict as scores if it looks like scores
        return data if isinstance(data, dict) else {}
