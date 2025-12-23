import json
import os
from ideagen import Pipeline

def test_invalid_topic(monkeypatch, tmp_path):
    class DummyGenerator:
        def __init__(self, *args, **kwargs): pass
        def generate(self, rendered_prompt):
            return type('DummyResponse', (), {'ideas': [{'X': type('D', (), {})()}]})()
    class DummyDeduplicator:
        def __init__(self, *args, **kwargs): pass
        def deduplicate(self, ideas):
            return ideas
    class DummyScorer:
        def __init__(self, *args, **kwargs): pass
        def score(self, ideas):
            return {'X': {}}
    monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
    monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
    monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)
    p = Pipeline(api_key='test')
    try:
        p.run(topic='', num_ideas=1)
        assert False, 'Expected ValueError for empty topic'
    except ValueError as e:
        assert 'Topic' in str(e)


def test_invalid_num_ideas(monkeypatch):
    class DummyGenerator:
        def __init__(self, *args, **kwargs): pass
        def generate(self, rendered_prompt):
            return type('DummyResponse', (), {'ideas': [{'X': type('D', (), {})()}]})()
    monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
    p = Pipeline(api_key='test')
    try:
        p.run(topic='ok', num_ideas=0)
        assert False, 'Expected ValueError for num_ideas <= 0'
    except ValueError as e:
        assert 'num_ideas' in str(e)


def test_scores_output(monkeypatch, tmp_path):
    from ideagen.models.ideas import IdeaResponse
    class DummyGenerator:
        def __init__(self, *args, **kwargs): pass
        def generate(self, rendered_prompt):
            return IdeaResponse(ideas=[{'X': {'description': 'test idea'}}])
    class DummyDeduplicator:
        def __init__(self, *args, **kwargs): pass
        def deduplicate(self, ideas):
            return ideas
    class DummyScorer:
        def __init__(self, *args, **kwargs): pass
        def score(self, ideas, rendered_prompt):
            return {'X': {'effort_hours': 10}}
    monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
    monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
    monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)
    p = Pipeline(api_key='test')
    scores_file = tmp_path / 'scores.json'
    p.run(topic='ok', num_ideas=1, scores_output_path=str(scores_file), skip_score=False)
    assert scores_file.exists()
    data = json.loads(scores_file.read_text())
    assert 'X' in data
