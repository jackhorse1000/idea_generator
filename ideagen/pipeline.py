import json
import logging
from ideagen.config import load_keys, PipelineConfig
import ideagen.generators.idea_generator as idea_generator_module
import ideagen.processors.deduplicator as deduplicator_module
import ideagen.generators.scorer as scorer_module
from ideagen.generators.idea_generator import load_default_prompt
from ideagen.generators.scorer import load_default_scoring_prompt
from ideagen.models.ideas import IdeaResponse, clean_dict

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, api_key: str = None, model_name: str = "openai/gpt-4.1-nano"):
        if api_key is None:
            api_key = load_keys()
        self.config = PipelineConfig(api_key, model_name)

    def _validate_inputs(self, topic: str, num_ideas: int) -> None:
        if not topic or not isinstance(topic, str) or not topic.strip():
            raise ValueError("Topic must be a non-empty string")
        if not isinstance(num_ideas, int) or num_ideas <= 0:
            raise ValueError("num_ideas must be a positive integer")

    def run(self, topic: str, num_ideas: int, output_path: str = None,
            generation_prompt: str = None, evaluation_prompt: str = None,
            skip_dedupe: bool = False, skip_score: bool = False,
            scores_output_path: str | None = None) -> IdeaResponse:
        # Validate inputs
        self._validate_inputs(topic, num_ideas)

        # Render generation prompt
        generation_template = generation_prompt or load_default_prompt()
        rendered_generation_prompt = generation_template.format(
            topic=topic,
            ideas_n=num_ideas,
            num_ideas=num_ideas,
            topic_description=topic
        )

        # Generate ideas
        try:
            generator = idea_generator_module.IdeaGenerator(self.config.llm_config)
        except TypeError:
            generator = idea_generator_module.IdeaGenerator()
        ideas = generator.generate(rendered_prompt=rendered_generation_prompt)

        # Deduplicate
        if not skip_dedupe:
            try:
                deduplicator = deduplicator_module.IdeaDeduplicator()
            except TypeError:
                deduplicator = deduplicator_module.IdeaDeduplicator
            ideas = deduplicator.deduplicate(ideas)

        # Score
        if not skip_score:
            # Clean ideas for scorer (remove None and empty strings)
            clean_ideas = clean_dict(ideas.ideas)

            evaluation_template = evaluation_prompt or load_default_scoring_prompt()
            ideas_json = json.dumps(clean_ideas, indent=2)
            rendered_evaluation_prompt = evaluation_template.format(ideas_json=ideas_json)

            try:
                scorer = scorer_module.EffortRevenueScorer(self.config.llm_config)
            except TypeError:
                scorer = scorer_module.EffortRevenueScorer()
            scores = scorer.score(ideas, rendered_prompt=rendered_evaluation_prompt)
            if scores_output_path:
                with open(scores_output_path, 'w') as sf:
                    json.dump(scores, sf, indent=2)

        # Save output (clean: no None or empty strings)
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(ideas.to_clean_dict(), f, indent=2)
        return ideas
