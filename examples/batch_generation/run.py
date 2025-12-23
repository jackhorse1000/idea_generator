from pathlib import Path
import json
from ideagen import Pipeline

# Load prompts from files
example_dir = Path(__file__).parent
generation_prompt = (example_dir / "generation_prompt.txt").read_text()
evaluation_prompt = (example_dir / "evaluation_prompt.txt").read_text()

# Batch generation across multiple topics
pipeline = Pipeline()
all_ideas = []

# Output directory for all artifacts
output_dir = example_dir / "output"
output_dir.mkdir(exist_ok=True)

topics = [
    "AI tools for content creators",
    "Automation for small businesses",
    "Developer productivity tools"
]

for topic in topics:
    print(f"Generating ideas for: {topic}")
    scores_path = output_dir / f"scores_{topic.replace(' ', '_')}.json"
    results = pipeline.run(
        topic=topic,
        num_ideas=5,
        generation_prompt=generation_prompt,
        evaluation_prompt=evaluation_prompt,
        scores_output_path=str(scores_path)
    )
    for idea in results.ideas:
        name = list(idea.keys())[0]
        details = idea[name]
        if hasattr(details, "model_dump"):
            serialized = details.model_dump()
        elif isinstance(details, dict):
            serialized = details
        elif hasattr(details, "__dict__"):
            serialized = details.__dict__
        else:
            serialized = str(details)
        all_ideas.append({name: serialized})

# Save combined results
output_path = output_dir / "all_ideas.json"
with open(output_path, "w") as f:
    json.dump({"ideas": [idea for idea in all_ideas]}, f, indent=2)

print(f"\nGenerated {len(all_ideas)} total ideas")
print(f"Saved to {output_path}")
