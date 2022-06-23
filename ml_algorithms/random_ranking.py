# import random
from numpy import random

from ml_algorithms.cosine_ranking import CosineSimilarityRecommender

class RandomRecommender(CosineSimilarityRecommender):
    """An algorithm for randomly ranking topics and their cosine similarity scores."""

    def __init__(self, algorithm_name) -> None:
        super().__init__(algorithm_name)

    def get_ranking(self, input_data):
        """Returns a random ranking of topics and their scores relative to the searched topic.
        The searched topic will always be in the first position of the ranking."""
        request_id = input_data["request_log"]["id"]
        search = (request_id, self.cosine_scores[request_id][request_id])
        ranking = [
            (id, score)
            for id,score in enumerate(self.cosine_scores[request_id])
            if score > 0 and id != request_id 
        ]
        random.shuffle(ranking)
        ranking.insert(0, search)

        input_data["ranked_ids"] = ranking

        return input_data