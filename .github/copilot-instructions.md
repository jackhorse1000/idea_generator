# Copilot Instructions

## Architecture

Pipeline flow: Generate, Deduplicate, Score, Save. Main entry is [ideagen/pipeline.py](ideagen/pipeline.py).

```
Pipeline (orchestrator)
    IdeaGenerator (LLM) returns IdeaResponse
    IdeaDeduplicator (sentence-transformers) returns filtered IdeaResponse
    EffortRevenueScorer (LLM) returns scores dict
```

All LLM calls go through OpenRouter using the OpenAI SDK in [ideagen/llm/client.py](ideagen/llm/client.py). Costs computed from `MODEL_PRICING` in [ideagen/llm/config.py](ideagen/llm/config.py).

## Commands

```bash
poetry install                    # Install deps
poetry run pytest -v              # Run tests
poetry run ideagen "topic" -n 10  # CLI with defaults
poetry run ideagen "topic" -n 10 --output ideas.json --scores-output scores.json --model openai/gpt-4.1-nano
```

Prompt overrides via `--generation-prompt path.txt` and `--evaluation-prompt path.txt`. Skip steps with `--skip-dedupe` or `--skip-score`.

## Environment

`OPENROUTER_API_KEY` loaded from: passed env_path, CWD `.env`, repo root `.env`, then environment variables. Raises if missing.

## Key Patterns

Generators extend `BaseGenerator`. Subclass calls `super().generate()` which returns raw LLM text, then parses:

```python
class MyGenerator(BaseGenerator):
    def generate(self, rendered_prompt: str):
        raw_text, metadata = super().generate(rendered_prompt)
        return self._parse(raw_text)
```

Prompt placeholders are required: `{topic}` and `{ideas_n}` for generation, `{ideas_json}` for evaluation. Defaults in [ideagen/prompts](ideagen/prompts).

## Parsing

[ideagen/generators/idea_generator.py](ideagen/generators/idea_generator.py) strips code fences, parses JSON, accepts `{"ideas": [{name: details}]}` or `{name: details}` shapes, normalizes keys to lowercase with underscores.

[ideagen/generators/scorer.py](ideagen/generators/scorer.py) strips code fences, returns `idea_scores` dict if present, otherwise parsed dict or `{}`. Include top-level `idea_scores` key in prompts for consistency with [ideagen/models/scores.py](ideagen/models/scores.py).

## Deduplication

[ideagen/processors/deduplicator.py](ideagen/processors/deduplicator.py) uses `sentence-transformers` model `all-MiniLM-L6-v2`. Threshold default 0.8; keeps first occurrence when pairs exceed threshold.

## Testing

Mock at module level for monkeypatch to work:

```python
monkeypatch.setattr('ideagen.generators.idea_generator.IdeaGenerator', DummyGenerator)
```

Pipeline imports modules (not classes) to enable test patching. See [tests](tests) for expected shapes and validation (ValueError on empty topic or non-positive num_ideas).

## Examples

Each example in [examples](examples) is a folder with `generation_prompt.txt`, `evaluation_prompt.txt`, and `run.py` that loads prompts and runs the pipeline.
