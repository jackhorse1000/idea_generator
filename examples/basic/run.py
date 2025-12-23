from pathlib import Path

from ideagen import Pipeline, PipelineConfig

example_dir = Path(__file__).parent
generation_prompt = (example_dir / "generation_prompt.txt").read_text()
evaluation_prompt = (example_dir / "evaluation_prompt.txt").read_text()

config = PipelineConfig(
    generation_prompt=generation_prompt,
    evaluation_prompt=evaluation_prompt,
)
pipeline = Pipeline(config=config)
results = pipeline.run(topic="AI tools for small businesses", num_ideas=5)

print(f"Generated {len(results.ideas)} ideas:")
for idea in results.ideas:
    name = list(idea.keys())[0]
    print(f"  - {name}")
