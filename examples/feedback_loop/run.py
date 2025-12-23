from pathlib import Path
from ideagen import Pipeline

example_dir = Path(__file__).parent
generation_prompt = (example_dir / "generation_prompt.txt").read_text()
evaluation_prompt = (example_dir / "evaluation_prompt.txt").read_text()

output_dir = example_dir / "output"
output_dir.mkdir(exist_ok=True)

pipeline = Pipeline()
results = pipeline.run(
    topic="Productivity apps for remote workers",
    num_ideas=3,
    iterations=2,
    generation_prompt=generation_prompt,
    evaluation_prompt=evaluation_prompt,
    output_path=str(output_dir / "ideas.json"),
    scores_output_path=str(output_dir / "scores.json")
)

print(f"Generated {len(results.ideas)} ideas across 2 iterations")
print("\nIdeas ranked by score:")
for i, idea in enumerate(results.ideas, 1):
    name = list(idea.keys())[0]
    details = idea[name]
    iteration = details.get('_iteration', '?')
    print(f"  {i}. {name} (iteration {iteration})")
