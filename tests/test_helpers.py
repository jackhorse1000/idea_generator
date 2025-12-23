"""Unit tests for helper functions: clean_dict and extract_text_values."""

from ideagen.models.ideas import clean_dict
from ideagen.processors.similarity import extract_text_values


class TestCleanDict:
    """Tests for clean_dict helper function."""

    def test_removes_none_values(self):
        data = {"a": 1, "b": None, "c": "hello"}
        result = clean_dict(data)
        assert result == {"a": 1, "c": "hello"}

    def test_removes_empty_strings(self):
        data = {"a": "value", "b": "", "c": "other"}
        result = clean_dict(data)
        assert result == {"a": "value", "c": "other"}

    def test_preserves_zero(self):
        data = {"a": 0, "b": None, "c": 1}
        result = clean_dict(data)
        assert result == {"a": 0, "c": 1}

    def test_preserves_false(self):
        data = {"a": False, "b": True, "c": None}
        result = clean_dict(data)
        assert result == {"a": False, "b": True}

    def test_preserves_empty_list(self):
        data = {"a": [], "b": None}
        result = clean_dict(data)
        assert result == {"a": []}

    def test_preserves_empty_dict(self):
        data = {"a": {}, "b": None}
        result = clean_dict(data)
        assert result == {"a": {}}

    def test_cleans_nested_dicts(self):
        data = {
            "outer": {
                "inner": "value",
                "empty": "",
                "null": None
            },
            "top": "level"
        }
        result = clean_dict(data)
        assert result == {
            "outer": {"inner": "value"},
            "top": "level"
        }

    def test_cleans_lists_of_dicts(self):
        data = [
            {"a": 1, "b": None},
            {"c": "", "d": "keep"}
        ]
        result = clean_dict(data)
        assert result == [{"a": 1}, {"d": "keep"}]

    def test_deeply_nested(self):
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "keep": "value",
                        "remove": None
                    }
                }
            }
        }
        result = clean_dict(data)
        assert result == {
            "level1": {
                "level2": {
                    "level3": {"keep": "value"}
                }
            }
        }


class TestExtractTextValues:
    """Tests for extract_text_values helper function."""

    def test_extracts_from_flat_dict(self):
        data = {"a": "hello", "b": "world"}
        result = extract_text_values(data)
        assert set(result) == {"hello", "world"}

    def test_extracts_from_nested_dict(self):
        data = {"outer": {"inner": "nested value"}}
        result = extract_text_values(data)
        assert result == ["nested value"]

    def test_extracts_from_list_of_strings(self):
        data = ["one", "two", "three"]
        result = extract_text_values(data)
        assert result == ["one", "two", "three"]

    def test_extracts_from_mixed_content(self):
        data = {
            "name": "Test Idea",
            "details": {
                "description": "A description",
                "count": 5  # non-string, should be ignored
            },
            "tags": ["tag1", "tag2"]
        }
        result = extract_text_values(data)
        assert set(result) == {"Test Idea", "A description", "tag1", "tag2"}

    def test_ignores_empty_strings(self):
        data = {"a": "value", "b": "", "c": "   "}
        result = extract_text_values(data)
        assert result == ["value"]

    def test_ignores_non_string_types(self):
        data = {"a": 123, "b": True, "c": None, "d": 3.14}
        result = extract_text_values(data)
        assert result == []

    def test_handles_empty_dict(self):
        result = extract_text_values({})
        assert result == []

    def test_handles_empty_list(self):
        result = extract_text_values([])
        assert result == []

    def test_deeply_nested_mixed(self):
        data = {
            "level1": {
                "level2": ["a", "b"],
                "text": "c"
            },
            "another": "d"
        }
        result = extract_text_values(data)
        assert set(result) == {"a", "b", "c", "d"}
