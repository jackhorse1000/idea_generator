import json
import logging
from typing import List, Dict, Any
from ideagen.config import load_keys, PipelineConfig
import ideagen.generators.idea_generator as idea_generator_module
import ideagen.processors.deduplicator as deduplicator_module
import ideagen.generators.scorer as scorer_module
from ideagen.generators.idea_generator import load_default_prompt
from ideagen.generators.scorer import load_default_scoring_prompt, load_default_feedback_prompt
from ideagen.models.ideas import IdeaResponse, clean_dict

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, api_key: str = None, model_name: str = "openai/gpt-4.1-nano"):
        if api_key is None:
            api_key = load_keys()
        self.config = PipelineConfig(api_key, model_name)

    def _validate_inputs(self, topic: str, num_ideas: int, iterations: int) -> None:
        if not topic or not isinstance(topic, str) or not topic.strip():
            raise ValueError("Topic must be a non-empty string")
        if not isinstance(num_ideas, int) or num_ideas <= 0:
            raise ValueError("num_ideas must be a positive integer")
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("iterations must be a positive integer")

    def _add_iteration_field(self, ideas: List[Dict[str, Any]], iteration: int) -> List[Dict[str, Any]]:
        for idea in ideas:
            for name, details in idea.items():
                if details is None:
                    idea[name] = {'_iteration': iteration}
                elif isinstance(details, dict):
                    details['_iteration'] = iteration
        return ideas

    def _create_generator(self):
        try:
            return idea_generator_module.IdeaGenerator(self.config.llm_config)
        except TypeError:
            return idea_generator_module.IdeaGenerator()

    def _create_deduplicator(self):
        try:
            return deduplicator_module.IdeaDeduplicator()
        except TypeError:
            return deduplicator_module.IdeaDeduplicator

    def _create_scorer(self):
        try:
            return scorer_module.EffortRevenueScorer(self.config.llm_config)
        except TypeError:
            return scorer_module.EffortRevenueScorer()

    def _render_generation_prompt(self, template: str, topic: str, num_ideas: int, 
                                   feedback: str = "", previous_ideas_json: str = "") -> str:
        return template.format(
            topic=topic,
            ideas_n=num_ideas,
            num_ideas=num_ideas,
            topic_description=topic,
            feedback=feedback,
            previous_ideas_json=previous_ideas_json
        )

    def _sort_ideas_by_score(self, ideas: List[Dict[str, Any]], 
                              scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        def get_score(idea: Dict[str, Any]) -> float:
            name = list(idea.keys())[0]
            idea_score = scores.get(name, {})
            if isinstance(idea_score, dict):
                for key in ['revenue_potential', 'feasibility', 'score', 'total']:
                    if key in idea_score:
                        return float(idea_score[key])
            return 0.0
        return sorted(ideas, key=get_score, reverse=True)

    def run(self, topic: str, num_ideas: int, output_path: str = None,
            generation_prompt: str = None, evaluation_prompt: str = None,
            skip_dedupe: bool = False, skip_score: bool = False,
            scores_output_path: str | None = None, iterations: int = 1) -> IdeaResponse:
        self._validate_inputs(topic, num_ideas, iterations)

        generation_template = generation_prompt or load_default_prompt()
        accumulated_ideas: List[Dict[str, Any]] = []
        feedback = ""
        scores = {}

        for iteration in range(1, iterations + 1):
            logger.info(f"Starting iteration {iteration}/{iterations}")

            previous_ideas_json = json.dumps(clean_dict(accumulated_ideas), indent=2) if accumulated_ideas else ""
            
            try:
                rendered_generation_prompt = self._render_generation_prompt(
                    generation_template, topic, num_ideas, feedback, previous_ideas_json
                )
            except KeyError:
                rendered_generation_prompt = generation_template.format(
                    topic=topic,
                    ideas_n=num_ideas,
                    num_ideas=num_ideas,
                    topic_description=topic
                )

            generator = self._create_generator()
            new_ideas = generator.generate(rendered_prompt=rendered_generation_prompt)
            
            new_ideas_with_iteration = self._add_iteration_field(new_ideas.ideas.copy(), iteration)
            accumulated_ideas.extend(new_ideas_with_iteration)

            ideas = IdeaResponse(ideas=accumulated_ideas)
            if not skip_dedupe:
                deduplicator = self._create_deduplicator()
                ideas = deduplicator.deduplicate(ideas)
                accumulated_ideas = ideas.ideas

            if iteration < iterations:
                feedback_template = evaluation_prompt or load_default_feedback_prompt()
                ideas_json = json.dumps(clean_dict(accumulated_ideas), indent=2)
                rendered_feedback_prompt = feedback_template.format(ideas_json=ideas_json)
                
                scorer = self._create_scorer()
                scores, feedback = scorer.score_with_feedback(ideas, rendered_prompt=rendered_feedback_prompt)
                logger.info(f"Iteration {iteration} complete, received feedback")
                logger.debug(f"Iteration {iteration} feedback: {feedback}")

        if not skip_score:
            evaluation_template = evaluation_prompt or load_default_scoring_prompt()
            ideas_json = json.dumps(clean_dict(accumulated_ideas), indent=2)
            rendered_evaluation_prompt = evaluation_template.format(ideas_json=ideas_json)

            scorer = self._create_scorer()
            scores = scorer.score(ideas, rendered_prompt=rendered_evaluation_prompt)
            
            accumulated_ideas = self._sort_ideas_by_score(accumulated_ideas, scores)
            ideas = IdeaResponse(ideas=accumulated_ideas)
            
            if scores_output_path:
                with open(scores_output_path, 'w') as sf:
                    json.dump(scores, sf, indent=2)

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(ideas.to_clean_dict(), f, indent=2)
        
        return ideas
