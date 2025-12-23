import json
import logging
from typing import Any, Dict, List

from ideagen.config import PipelineConfig
from ideagen.generators.idea_generator import IdeaGenerator
from ideagen.generators.scorer import EffortRevenueScorer
from ideagen.models.ideas import IdeaResponse, clean_dict
from ideagen.processors.deduplicator import IdeaDeduplicator
from ideagen.prompts import load_feedback_prompt, load_generation_prompt, load_scoring_prompt

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, config: PipelineConfig = None, api_key: str = None, model: str = None):
        if config is not None:
            self.config = config
        else:
            self.config = PipelineConfig(api_key=api_key, model=model or "openai/gpt-4.1-nano")

    def run(
        self,
        topic: str,
        num_ideas: int,
        iterations: int = 1,
        output_path: str = None,
        scores_output_path: str = None,
        generation_prompt: str = None,
        evaluation_prompt: str = None,
        skip_dedupe: bool = None,
        skip_score: bool = None,
    ) -> IdeaResponse:
        self._validate(topic, num_ideas, iterations)

        skip_dedupe = skip_dedupe if skip_dedupe is not None else self.config.skip_dedupe
        skip_score = skip_score if skip_score is not None else self.config.skip_score
        generation_template = generation_prompt or self.config.generation_prompt or load_generation_prompt()
        evaluation_template = evaluation_prompt or self.config.evaluation_prompt

        llm_config = self.config.to_llm_config()
        accumulated_ideas: List[Dict[str, Any]] = []
        feedback = ""

        for iteration in range(1, iterations + 1):
            logger.info(f"Starting iteration {iteration}/{iterations}")

            rendered_prompt = self._render_prompt(
                generation_template, topic, num_ideas, feedback, accumulated_ideas
            )
            generator = IdeaGenerator(llm_config)
            new_ideas = generator.generate(rendered_prompt)

            for idea in new_ideas.ideas:
                for details in idea.values():
                    if isinstance(details, dict):
                        details["_iteration"] = iteration
                    elif details is None:
                        idea[list(idea.keys())[0]] = {"_iteration": iteration}
            accumulated_ideas.extend(new_ideas.ideas)

            if not skip_dedupe:
                deduplicator = IdeaDeduplicator(self.config.similarity_threshold)
                result = deduplicator.deduplicate(IdeaResponse(ideas=accumulated_ideas))
                accumulated_ideas = result.ideas

            if iteration < iterations:
                feedback_template = evaluation_template or load_feedback_prompt()
                ideas_json = json.dumps(clean_dict(accumulated_ideas), indent=2)
                rendered_feedback = feedback_template.format(ideas_json=ideas_json)
                scorer = EffortRevenueScorer(llm_config)
                _, feedback = scorer.score_with_feedback(None, rendered_feedback)
                logger.info(f"Iteration {iteration} complete")

        scores = {}
        if not skip_score:
            scoring_template = evaluation_template or load_scoring_prompt()
            ideas_json = json.dumps(clean_dict(accumulated_ideas), indent=2)
            rendered_scoring = scoring_template.format(ideas_json=ideas_json)
            scorer = EffortRevenueScorer(llm_config)
            scores = scorer.score(None, rendered_scoring)
            accumulated_ideas = self._sort_by_score(accumulated_ideas, scores)

            if scores_output_path:
                with open(scores_output_path, "w") as f:
                    json.dump(scores, f, indent=2)

        ideas = IdeaResponse(ideas=accumulated_ideas)
        if output_path:
            with open(output_path, "w") as f:
                json.dump(ideas.to_clean_dict(), f, indent=2)

        return ideas

    def _validate(self, topic: str, num_ideas: int, iterations: int) -> None:
        if not topic or not isinstance(topic, str) or not topic.strip():
            raise ValueError("Topic must be a non-empty string")
        if not isinstance(num_ideas, int) or num_ideas <= 0:
            raise ValueError("num_ideas must be a positive integer")
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("iterations must be a positive integer")

    def _render_prompt(
        self, template: str, topic: str, num_ideas: int, feedback: str, ideas: List[Dict[str, Any]]
    ) -> str:
        previous_json = json.dumps(clean_dict(ideas), indent=2) if ideas else ""
        try:
            return template.format(
                topic=topic,
                ideas_n=num_ideas,
                num_ideas=num_ideas,
                topic_description=topic,
                feedback=feedback,
                previous_ideas_json=previous_json,
            )
        except KeyError:
            return template.format(topic=topic, ideas_n=num_ideas, num_ideas=num_ideas, topic_description=topic)

    def _sort_by_score(self, ideas: List[Dict[str, Any]], scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        def get_score(idea: Dict[str, Any]) -> float:
            name = list(idea.keys())[0]
            idea_score = scores.get(name, {})
            if isinstance(idea_score, dict):
                for key in ["revenue_potential", "feasibility", "score", "total"]:
                    if key in idea_score:
                        return float(idea_score[key])
            return 0.0

        return sorted(ideas, key=get_score, reverse=True)
