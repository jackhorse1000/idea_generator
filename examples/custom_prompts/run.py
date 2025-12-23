from pathlib import Path
from ideagen import Pipeline

# Load prompts from files
example_dir = Path(__file__).parent
generation_prompt = (example_dir / "generation_prompt.txt").read_text()
evaluation_prompt = (example_dir / "evaluation_prompt.txt").read_text()

# Run pipeline with custom prompts
pipeline = Pipeline()
results = pipeline.run(
    topic="Fintech solutions",
    num_ideas=5,
    generation_prompt=generation_prompt,
    evaluation_prompt=evaluation_prompt
)

print(f"Generated {len(results.ideas)} ideas with custom prompts")
print(results)
