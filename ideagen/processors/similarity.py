import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Any


def extract_text_values(data: Any) -> list:
    """Recursively extract all string values from a dict or list."""
    texts = []
    if isinstance(data, dict):
        for v in data.values():
            texts.extend(extract_text_values(v))
    elif isinstance(data, list):
        for item in data:
            texts.extend(extract_text_values(item))
    elif isinstance(data, str) and data.strip():
        texts.append(data)
    return texts


class IdeaSimilarityAnalyzer:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def compute_similarity_matrix(self, ideas):
        embeddings = self.model.encode(ideas)
        normed = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return np.dot(normed, normed.T)

    def concatenate_idea(self, name, details):
        """Extract all text from idea details for similarity comparison."""
        text_parts = extract_text_values(details)
        return f"{name}: {' '.join(text_parts)}"
