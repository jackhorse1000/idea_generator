from pathlib import Path
from ideagen import Pipeline

example_dir = Path(__file__).parent
generation_prompt = (example_dir / "generation_prompt.txt").read_text()
evaluation_prompt = (example_dir / "evaluation_prompt.txt").read_text()

output_dir = example_dir / "output"
output_dir.mkdir(exist_ok=True)

pipeline = Pipeline()
results = pipeline.run(
    topic="Quick healthy dinners under 30 minutes with minimal ingredients",
    num_ideas=5,
    generation_prompt=generation_prompt,
    evaluation_prompt=evaluation_prompt,
    output_path=str(output_dir / "dinner_ideas.json"),
    scores_output_path=str(output_dir / "dinner_scores.json")
)

print(f"Generated {len(results.ideas)} dinner ideas")
for idea in results.ideas:
    name = list(idea.keys())[0]
    print(f"  - {name}")
print(f"\nSaved to {output_dir}")
