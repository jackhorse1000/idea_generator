import logging
from ideagen.models.ideas import IdeaResponse
from .similarity import IdeaSimilarityAnalyzer

logger = logging.getLogger(__name__)


class IdeaDeduplicator:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.analyzer = IdeaSimilarityAnalyzer()

    def deduplicate(self, idea_response: IdeaResponse) -> IdeaResponse:
        ideas = [self.analyzer.concatenate_idea(list(idea.keys())[0], list(idea.values())[0]) for idea in idea_response.ideas]
        similarity_matrix = self.analyzer.compute_similarity_matrix(ideas)
        filtered_indices = set()
        dedup_ideas = []
        for i in range(len(ideas)):
            if i not in filtered_indices:
                dedup_ideas.append(idea_response.ideas[i])
                for j in range(i + 1, len(ideas)):
                    if j not in filtered_indices and similarity_matrix[i][j] > self.similarity_threshold:
                        filtered_indices.add(j)
        logger.info(f"Deduplicated from {len(ideas)} to {len(dedup_ideas)} ideas")
        return IdeaResponse(ideas=dedup_ideas)
