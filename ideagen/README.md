# ideagen

Generate ideas → Evaluate them → Repeat → Present the best ones.

## Quick Start

```python
from ideagen import Pipeline

pipeline = Pipeline()  # Uses OPENROUTER_API_KEY from .env
ideas = pipeline.run(topic="AI tools for freelancers", num_ideas=10)
```

That's it. Ideas are generated, deduplicated, and scored.

---

## The Loop

The core workflow is simple:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Generate   │ ──▶ │  Deduplicate │ ──▶ │   Evaluate   │ ──▶ │   Present    │
│   (LLM)      │     │  (Semantic)  │     │   (LLM)      │     │   (JSON)     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

Run it multiple times with different topics or prompts, accumulate results, then review.

---

## Custom Prompts Made Simple

The key insight: **you only need to change the text, not the code**.

### Generation Prompt

Your prompt needs two placeholders:
- `{topic}` - what you're generating ideas for
- `{ideas_n}` - how many ideas to generate

**Default prompt** (`prompts/idea_generation.txt`):
```
Generate {ideas_n} business ideas for the following topic:

**Topic:** {topic}

For each idea, provide:
- Problem statement
- Target user
- Value proposition
- Solution overview
- Competitive advantage
- Monetization strategy

Output as a JSON dictionary: key is a short idea name, value is the full idea details.
```

**Your complex prompt** - just write what you want:
```python
my_prompt = """
You are a serial entrepreneur who has built 3 successful SaaS companies.

Generate {ideas_n} business ideas for: {topic}

Focus on:
- Problems you've personally experienced
- Solutions that can reach $10k MRR in 6 months
- Ideas a solo developer can build in 2 weeks

For each idea, provide:
- Problem statement
- Target user  
- Value proposition
- Solution overview
- Competitive advantage
- Monetization strategy

Be specific. No generic ideas. Output as JSON dictionary.
"""

pipeline.run(topic="developer productivity", num_ideas=5, generation_prompt=my_prompt)
```

That's it. Same placeholders, different instructions.

---

### Evaluation Prompt

Your prompt needs one placeholder:
- `{ideas_json}` - the ideas to evaluate (injected automatically)

**Default prompt** (`prompts/scoring.txt`):
```
Score the following business ideas for:
- Implementation effort (hours)
- Monthly revenue (min/max)
- Feasibility for a solo developer
- Key assumptions
- Tech stack alignment
- Business model fit

Output as JSON with a top-level key named "idea_scores".
For each idea_name, include all the score fields provided above.

Ideas:
{ideas_json}
```

**Your complex evaluation** - same pattern:
```python
my_eval = """
You are a VC analyst evaluating early-stage ideas.

Score each idea on a 1-10 scale for:
- Market size potential
- Technical feasibility  
- Competitive moat
- Team-market fit (assume solo technical founder)
- Time to first revenue

Also provide:
- Top 3 risks
- Suggested MVP scope (1 sentence)
- Go/No-Go recommendation

Output as JSON with key "idea_scores". Each idea gets all fields above.

Ideas:
{ideas_json}
"""

pipeline.run(topic="fintech", num_ideas=10, evaluation_prompt=my_eval)
```

---

## Batch Generation Loop

Generate lots of ideas across multiple runs:

```python
from ideagen import Pipeline
import json

pipeline = Pipeline()
all_ideas = []
all_scores = {}

topics = [
    "AI tools for content creators",
    "Automation for small businesses",
    "Developer productivity tools"
]

for topic in topics:
    ideas = pipeline.run(
        topic=topic,
        num_ideas=20,
        scores_output_path=f"scores_{topic.replace(' ', '_')}.json"
    )
    all_ideas.extend(ideas.ideas)

# Save combined results
with open("all_ideas.json", "w") as f:
    json.dump({"ideas": all_ideas}, f, indent=2)

print(f"Generated {len(all_ideas)} total ideas")
```

---

## Using Individual Components

For more control, use the pieces directly:

```python
from ideagen import IdeaGenerator, IdeaDeduplicator, EffortRevenueScorer, LlmConfig

# Configure
config = LlmConfig(
    name="openai/gpt-4.1-nano",
    api_key="sk-or-...",
    temperature=0.8  # More creative
)

# Generate
generator = IdeaGenerator(config)
ideas = generator.generate(topic="AI agents", num_ideas=10)

# Deduplicate (optional)
deduplicator = IdeaDeduplicator(similarity_threshold=0.7)  # Stricter
unique_ideas = deduplicator.deduplicate(ideas)

# Score
scorer = EffortRevenueScorer(config)
scores = scorer.score(unique_ideas)
```

---

## Prompt Tips

### Keep It Simple
❌ Don't do this:
```
As an AI assistant specialized in entrepreneurship with deep knowledge of 
market dynamics and technical feasibility assessment, leveraging your 
understanding of current market trends and emerging technologies...
```

✅ Do this:
```
You are a startup founder. Generate {ideas_n} ideas for {topic}.
Be specific and practical.
```

### Be Specific About Output
The LLM needs to know the JSON structure. Always end with:
```
Output as JSON dictionary: key is idea name, value is the details.
```

### Required Fields
Generation prompts should ask for these (the model expects them):
- Problem statement
- Target user
- Value proposition
- Solution overview
- Competitive advantage
- Monetization strategy

You can add more fields, but keep these for compatibility.

---

## File Structure

```
ideagen/
├── pipeline.py          # Main Pipeline class - start here
├── config.py            # API key loading, model config
├── cli.py               # Command-line interface
├── generators/
│   ├── base.py          # Base LLM caller
│   ├── idea_generator.py # Generates ideas from topic
│   └── scorer.py        # Evaluates/scores ideas
├── processors/
│   ├── deduplicator.py  # Removes similar ideas
│   └── similarity.py    # Semantic similarity (sentence-transformers)
├── models/
│   ├── ideas.py         # IdeaDetails, IdeaResponse
│   ├── scores.py        # IdeaScore, ScoringResponse
│   └── execution.py     # Metadata, errors
├── llm/
│   ├── client.py        # OpenRouter API client
│   └── config.py        # LlmConfig, model pricing
└── prompts/
    ├── idea_generation.txt  # Default generation prompt
    └── scoring.txt          # Default evaluation prompt
```

---

## Extending

### Add a New Evaluation Metric

Create a new scorer by extending `BaseGenerator`:

```python
from ideagen.generators.base import BaseGenerator
from ideagen.llm.config import LlmConfig

class MarketSizeScorer(BaseGenerator):
    def __init__(self, model_config: LlmConfig):
        prompt = """
        Estimate the market size for each idea.
        
        For each idea provide:
        - TAM (Total Addressable Market)
        - SAM (Serviceable Addressable Market)  
        - SOM (Serviceable Obtainable Market)
        - Market growth rate
        
        Output as JSON with key "market_scores".
        
        Ideas:
        {ideas_json}
        """
        super().__init__(model_config, prompt)
    
    def score(self, ideas_response):
        import json
        ideas_json = json.dumps([idea for idea in ideas_response.ideas], indent=2)
        raw_text, _ = super().generate(ideas_json=ideas_json)
        return json.loads(raw_text.replace("```json", "").replace("```", ""))
```

### Add a Filter Step

Filter ideas before scoring:

```python
def filter_ideas(ideas_response, min_fields=4):
    """Remove ideas missing too many fields."""
    filtered = []
    for idea in ideas_response.ideas:
        name = list(idea.keys())[0]
        details = idea[name]
        filled = sum(1 for v in vars(details).values() if v)
        if filled >= min_fields:
            filtered.append(idea)
    return IdeaResponse(ideas=filtered)
```

### Chain Multiple Evaluations

Run ideas through multiple scorers:

```python
from ideagen import Pipeline, EffortRevenueScorer, LlmConfig

pipeline = Pipeline()
ideas = pipeline.run(topic="AI tools", num_ideas=10, skip_score=True)

config = LlmConfig(name="openai/gpt-4.1-nano", api_key="...")

# Score 1: Effort/Revenue
scorer1 = EffortRevenueScorer(config)
scores1 = scorer1.score(ideas)

# Score 2: Your custom scorer
scorer2 = MarketSizeScorer(config)
scores2 = scorer2.score(ideas)

# Combine scores
combined = {name: {**scores1.get(name, {}), **scores2.get(name, {})} 
            for name in set(list(scores1.keys()) + list(scores2.keys()))}
```

---

## CLI Usage

```bash
# Basic
ideagen "AI tools for freelancers" -n 10

# With outputs
ideagen "fintech ideas" -n 20 --output ideas.json --scores-output scores.json

# Custom prompts
ideagen "developer tools" -n 5 --generation-prompt my_prompt.txt --evaluation-prompt my_eval.txt

# Skip steps
ideagen "quick ideas" -n 5 --skip-dedupe --skip-score
```

---

## Environment

Set your API key in `.env`:
```
OPENROUTER_API_KEY=sk-or-...
```

Or pass directly:
```python
Pipeline(api_key="sk-or-...")
```
