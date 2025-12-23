from ideagen.generators.idea_generator import IdeaGenerator
from ideagen.config import LlmConfig

def test_idea_generator(monkeypatch):
    class DummyClient:
        def chat(self, *args, **kwargs):
            return ('{"ideas": [{"Test": {"problem_statement": "p", "target_user": "u", "value_proposition": "v", "solution_overview": "s", "competitive_advantage": "c", "monetization_strategy": "m"}}]}', 0.01)
    monkeypatch.setattr('ideagen.llm.client.OpenRouterClient', lambda api_key, base_url=None: DummyClient())
    config = LlmConfig(name='openai/gpt-4.1-nano', api_key='test')
    generator = IdeaGenerator(config)
    response = generator.generate(rendered_prompt="rendered prompt")
    assert response.ideas[0]['Test']['problem_statement'] == 'p'
