import pytest
from ideagen import Pipeline
from ideagen.generators.scorer import EffortRevenueScorer


class TestIterationsValidation:
    def test_iterations_zero_raises(self, monkeypatch):
        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', 
                          lambda *a, **k: type('G', (), {'generate': lambda s, **kw: type('R', (), {'ideas': []})()})())
        pipeline = Pipeline(api_key='test')
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            pipeline.run(topic='Test', num_ideas=5, iterations=0)

    def test_iterations_negative_raises(self, monkeypatch):
        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator',
                          lambda *a, **k: type('G', (), {'generate': lambda s, **kw: type('R', (), {'ideas': []})()})())
        pipeline = Pipeline(api_key='test')
        with pytest.raises(ValueError, match="iterations must be a positive integer"):
            pipeline.run(topic='Test', num_ideas=5, iterations=-1)


class TestIterationField:
    def test_iteration_field_added(self, monkeypatch):
        class DummyGenerator:
            def __init__(self, *args, **kwargs): pass
            def generate(self, rendered_prompt):
                return type('R', (), {'ideas': [{'TestIdea': {'desc': 'test'}}]})()

        class DummyDeduplicator:
            def __init__(self, *args, **kwargs): pass
            def deduplicate(self, ideas):
                return ideas

        class DummyScorer:
            def __init__(self, *args, **kwargs): pass
            def score(self, ideas, rendered_prompt):
                return {'TestIdea': {'score': 5}}

        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
        monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
        monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)

        pipeline = Pipeline(api_key='test')
        results = pipeline.run(topic='Test', num_ideas=1, iterations=1)
        
        assert len(results.ideas) == 1
        idea = results.ideas[0]
        name = list(idea.keys())[0]
        assert idea[name].get('_iteration') == 1


class TestFeedbackLoop:
    def test_multiple_iterations_accumulate_ideas(self, monkeypatch):
        call_count = [0]

        class DummyGenerator:
            def __init__(self, *args, **kwargs): pass
            def generate(self, rendered_prompt):
                call_count[0] += 1
                return type('R', (), {'ideas': [{f'Idea{call_count[0]}': {'desc': f'desc{call_count[0]}'}}]})()

        class DummyDeduplicator:
            def __init__(self, *args, **kwargs): pass
            def deduplicate(self, ideas):
                return ideas

        class DummyScorer:
            def __init__(self, *args, **kwargs): pass
            def score(self, ideas, rendered_prompt):
                if ideas is None:
                    return {}
                return {list(i.keys())[0]: {'score': 5} for i in ideas.ideas}
            
            def score_with_feedback(self, ideas, rendered_prompt):
                return {}, "Generate more innovative ideas"

        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
        monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
        monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)

        pipeline = Pipeline(api_key='test')
        results = pipeline.run(topic='Test', num_ideas=1, iterations=2)

        assert len(results.ideas) == 2
        names = [list(i.keys())[0] for i in results.ideas]
        assert 'Idea1' in names
        assert 'Idea2' in names

    def test_iteration_field_reflects_source_iteration(self, monkeypatch):
        call_count = [0]

        class DummyGenerator:
            def __init__(self, *args, **kwargs): pass
            def generate(self, rendered_prompt):
                call_count[0] += 1
                return type('R', (), {'ideas': [{f'Idea{call_count[0]}': {'desc': 'test'}}]})()

        class DummyDeduplicator:
            def __init__(self, *args, **kwargs): pass
            def deduplicate(self, ideas):
                return ideas

        class DummyScorer:
            def __init__(self, *args, **kwargs): pass
            def score(self, ideas, rendered_prompt):
                return {}
            
            def score_with_feedback(self, ideas, rendered_prompt):
                return {}, "More ideas please"

        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
        monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
        monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)

        pipeline = Pipeline(api_key='test')
        results = pipeline.run(topic='Test', num_ideas=1, iterations=3, skip_score=True)

        iterations_found = {}
        for idea in results.ideas:
            name = list(idea.keys())[0]
            iteration = idea[name].get('_iteration')
            iterations_found[name] = iteration

        assert iterations_found['Idea1'] == 1
        assert iterations_found['Idea2'] == 2
        assert iterations_found['Idea3'] == 3

    def test_feedback_injected_into_next_generation_prompt(self, monkeypatch):
        captured_prompts = []

        class DummyGenerator:
            def __init__(self, *args, **kwargs): pass
            def generate(self, rendered_prompt):
                captured_prompts.append(rendered_prompt)
                return type('R', (), {'ideas': [{'TestIdea': {'desc': 'test'}}]})()

        class DummyDeduplicator:
            def __init__(self, *args, **kwargs): pass
            def deduplicate(self, ideas):
                return ideas

        class DummyScorer:
            def __init__(self, *args, **kwargs): pass
            def score(self, ideas, rendered_prompt):
                return {}
            
            def score_with_feedback(self, ideas, rendered_prompt):
                return {}, "Focus on B2B SaaS ideas with recurring revenue"

        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
        monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
        monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)

        generation_prompt = "Generate {ideas_n} ideas for {topic}. Feedback: {feedback}"
        pipeline = Pipeline(api_key='test')
        pipeline.run(topic='Test', num_ideas=1, iterations=2, generation_prompt=generation_prompt, skip_score=True)

        assert len(captured_prompts) == 2
        assert "Focus on B2B SaaS ideas with recurring revenue" in captured_prompts[1]


class TestIterationFieldPreservation:
    def test_iteration_field_survives_clean_dict(self):
        from ideagen.models.ideas import IdeaResponse, clean_dict
        
        ideas = [{'TestIdea': {'desc': 'test', '_iteration': 1}}]
        cleaned = clean_dict(ideas)
        
        assert cleaned[0]['TestIdea']['_iteration'] == 1

    def test_iteration_field_in_to_clean_dict(self):
        from ideagen.models.ideas import IdeaResponse
        
        ideas = IdeaResponse(ideas=[{'TestIdea': {'desc': 'test', '_iteration': 2}}])
        result = ideas.to_clean_dict()
        
        assert result['ideas'][0]['TestIdea']['_iteration'] == 2


class TestScorerFeedback:
    def test_parse_response_with_feedback(self):
        class MockScorer(EffortRevenueScorer):
            def __init__(self):
                pass

        scorer = MockScorer()
        data = scorer._parse('{"idea_scores": {"Test": {"score": 8}}, "feedback": "Try more B2B ideas"}')
        
        assert data.get('idea_scores') == {"Test": {"score": 8}}
        assert data.get('feedback') == "Try more B2B ideas"

    def test_parse_response_without_feedback(self):
        class MockScorer(EffortRevenueScorer):
            def __init__(self):
                pass

        scorer = MockScorer()
        data = scorer._parse('{"idea_scores": {"Test": {"score": 8}}}')
        
        assert data.get('idea_scores') == {"Test": {"score": 8}}
        assert data.get('feedback') is None

    def test_parse_response_strips_code_fences(self):
        class MockScorer(EffortRevenueScorer):
            def __init__(self):
                pass

        scorer = MockScorer()
        data = scorer._parse('```json\n{"idea_scores": {"Test": {"score": 8}}}\n```')
        
        assert data.get('idea_scores') == {"Test": {"score": 8}}


class TestSortByScore:
    def test_ideas_sorted_by_score_descending(self, monkeypatch):
        class DummyGenerator:
            def __init__(self, *args, **kwargs): pass
            def generate(self, rendered_prompt):
                return type('R', (), {'ideas': [
                    {'LowIdea': {'desc': 'low'}},
                    {'HighIdea': {'desc': 'high'}},
                    {'MidIdea': {'desc': 'mid'}}
                ]})()

        class DummyDeduplicator:
            def __init__(self, *args, **kwargs): pass
            def deduplicate(self, ideas):
                return ideas

        class DummyScorer:
            def __init__(self, *args, **kwargs): pass
            def score(self, ideas, rendered_prompt):
                return {
                    'LowIdea': {'revenue_potential': 2},
                    'HighIdea': {'revenue_potential': 9},
                    'MidIdea': {'revenue_potential': 5}
                }

        monkeypatch.setattr('ideagen.pipeline.IdeaGenerator', DummyGenerator)
        monkeypatch.setattr('ideagen.pipeline.IdeaDeduplicator', DummyDeduplicator)
        monkeypatch.setattr('ideagen.pipeline.EffortRevenueScorer', DummyScorer)

        pipeline = Pipeline(api_key='test')
        results = pipeline.run(topic='Test', num_ideas=3, iterations=1)

        names = [list(i.keys())[0] for i in results.ideas]
        assert names == ['HighIdea', 'MidIdea', 'LowIdea']
