# Copilot Instructions

## Architecture

Pipeline flow: Generate → Deduplicate → Score → Save. Entry point is [ideagen/pipeline.py](ideagen/pipeline.py).

```
Pipeline (orchestrator)
    IdeaGenerator (LLM) → IdeaResponse
    IdeaDeduplicator (sentence-transformers) → filtered IdeaResponse
    EffortRevenueScorer (LLM) → scores dict
```

All LLM calls go through OpenRouter using the OpenAI SDK in [ideagen/llm/client.py](ideagen/llm/client.py). Config and pricing in [ideagen/config.py](ideagen/config.py).

## Commands

```bash
poetry install                    # Install deps
poetry run pytest -v              # Run tests
poetry run ideagen "topic" -n 5   # CLI
poetry run ideagen "topic" -n 5 --iterations 2 --output ideas.json
```

## Configuration

Use `PipelineConfig` dataclass for all options:

```python
from ideagen import Pipeline, PipelineConfig

config = PipelineConfig(
    model="openai/gpt-4.1-nano",
    skip_dedupe=False,
    skip_score=False,
    generation_prompt=None,  # or custom prompt string
    evaluation_prompt=None,
)
pipeline = Pipeline(config=config)
results = pipeline.run(topic="AI tools", num_ideas=5, iterations=2)
```

## Environment

`OPENROUTER_API_KEY` loaded from: CWD `.env`, repo root `.env`, or environment. Raises if missing.

## Key Patterns

Generators extend `BaseGenerator`. Subclass calls `super().generate()` which returns `(text, cost)`:

```python
class MyGenerator(BaseGenerator):
    def generate(self, prompt: str):
        raw_text, _ = super().generate(prompt)
        return self._parse(raw_text)
```

Prompt placeholders: `{topic}`, `{ideas_n}` for generation; `{ideas_json}` for evaluation. Default prompts in [ideagen/prompts/](ideagen/prompts/).

## Testing

Mock at pipeline level where classes are imported:

```python
monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)
```

## Examples

- `examples/basic/` — simple generation
- `examples/iterative/` — multi-round feedback loop

Pipeline imports classes directly (not modules). See [tests](tests) for expected shapes and validation (ValueError on empty topic or non-positive num_ideas).
