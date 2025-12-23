from ideagen import Pipeline

def test_pipeline_runs(monkeypatch):
    class DummyGenerator:
        def generate(self, rendered_prompt):
            return type('DummyResponse', (), {'ideas': [{'Test': None}]})()
    class DummyDeduplicator:
        def deduplicate(self, ideas):
            return ideas
    class DummyScorer:
        def score(self, ideas, rendered_prompt):
            return {'Test': None}
    monkeypatch.setattr('ideagen.generators.idea_generator.IdeaGenerator', DummyGenerator)
    monkeypatch.setattr('ideagen.processors.deduplicator.IdeaDeduplicator', DummyDeduplicator)
    monkeypatch.setattr('ideagen.generators.scorer.EffortRevenueScorer', DummyScorer)
    pipeline = Pipeline(api_key='test')
    results = pipeline.run(topic='Test', num_ideas=1)
    assert hasattr(results, 'ideas')
