# idea-gen-lib

Generate, deduplicate, and score business ideas using LLMs.

## Features

- Generate ideas from a topic using LLMs (via OpenRouter)
- Deduplicate ideas using semantic similarity
- Score ideas for effort, revenue, and feasibility
- Iterative feedback loop to refine ideas across multiple rounds
- Simple CLI and Python API

## Quickstart

1. Install:

   ```bash
   poetry install
   ```

2. Set your OpenRouter API key:

   ```bash
   export OPENROUTER_API_KEY=sk-or-...
   ```

   Or create a `.env` file (ignored by git).

3. Run:

   ```bash
   poetry run ideagen "AI tools for small businesses" -n 5
   ```

## Python API

```python
from ideagen import Pipeline, PipelineConfig

# Simple usage
pipeline = Pipeline()
results = pipeline.run(topic="AI tools", num_ideas=5)

# With config
config = PipelineConfig(
    model="openai/gpt-4.1-nano",
    skip_dedupe=False,
    skip_score=False,
)
pipeline = Pipeline(config=config)
results = pipeline.run(topic="AI tools", num_ideas=5, iterations=2)

for idea in results.ideas:
    name = list(idea.keys())[0]
    print(f"{name} (iteration {idea[name].get('_iteration')})")
```

## CLI

```bash
# Basic
poetry run ideagen "AI tools" -n 5 --output ideas.json

# With iterations and scoring
poetry run ideagen "AI tools" -n 5 --iterations 3 --scores-output scores.json

# Custom prompts
poetry run ideagen "AI tools" -n 5 --generation-prompt prompt.txt
```

## Examples

See `examples/` for complete usage:

- `examples/basic/` — simple generation with custom prompts
- `examples/iterative/` — multi-round feedback loop

## Testing

```bash
poetry run pytest -v
```
