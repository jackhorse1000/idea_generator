from ideagen import Pipeline

def test_pipeline_runs(monkeypatch):
    class DummyGenerator:
        def __init__(self, *args, **kwargs): pass
        def generate(self, rendered_prompt):
            return type('DummyResponse', (), {'ideas': [{'Test': None}]})()
    class DummyDeduplicator:
        def __init__(self, *args, **kwargs): pass
        def deduplicate(self, ideas):
            return ideas
    class DummyScorer:
        def __init__(self, *args, **kwargs): pass
        def score(self, ideas, rendered_prompt):
            return {'Test': None}
    monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
    monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
    monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)
    pipeline = Pipeline(api_key='test')
    results = pipeline.run(topic='Test', num_ideas=1)
    assert hasattr(results, 'ideas')
