# idea-gen-lib

Standalone library for generating, deduplicating, and scoring business ideas using LLMs.

## Features
- Generate ideas from a topic using LLMs
- Deduplicate ideas using semantic similarity
- Score ideas for effort, revenue, and feasibility
- **Feedback loop**: iteratively refine ideas with LLM feedback
- Simple CLI and Python API

## Quickstart

1. Install dependencies:
   ```bash
   poetry install
   ```
2. Provide your OpenRouter API key via environment or `.env` (not committed):
   ```
   OPENROUTER_API_KEY=sk-or-...
   ```
   Note: `.env` is ignored by `.gitignore`. Do not commit secrets.
3. Run the CLI:
   ```bash
   poetry run ideagen "AI tools for small businesses" -n 10 --output results.json --scores-output scores.json
   ```

## Library Usage

```python
from ideagen import Pipeline
pipeline = Pipeline(api_key="sk-or-...")
results = pipeline.run(topic="AI tools", num_ideas=10)
```

## CLI Usage

```bash
ideagen "AI tools" -n 10 --output results.json
```

## Custom Prompts

You can pass your own generation and evaluation prompts via the API or CLI.

## Feedback Loop

Run multiple generate-evaluate iterations where evaluation feedback guides subsequent generations:

```python
from ideagen import Pipeline

pipeline = Pipeline()
results = pipeline.run(
    topic="AI tools for small businesses",
    num_ideas=5,
    iterations=3  # Run 3 generate-evaluate cycles
)

# Ideas include _iteration field showing which round generated them
for idea in results.ideas:
    name = list(idea.keys())[0]
    print(f"{name} (iteration {idea[name].get('_iteration')})")
```

CLI usage:
```bash
poetry run ideagen "AI tools" -n 5 --iterations 3 --output results.json
```

See `examples/feedback_loop/` for a complete example with custom prompts.

## Testing

```bash
poetry run pytest -v
```
