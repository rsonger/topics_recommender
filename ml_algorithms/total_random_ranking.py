# import random
from numpy import random

from ml_algorithms.cosine_ranking import CosineSimilarityRecommender

class TotalRandomRecommender(CosineSimilarityRecommender):
    """An algorithm for recommending topics with some similarity, but ranked randomly."""

    name = "Total Random Ranking"

    def __init__(self) -> None:
        super().__init__()

    def get_ranking(self, input_data, lang_code):
        """Returns a random ranking of topics and their scores relative to the searched topic.
        The searched topic will always be in the first position of the ranking."""
        request_id = input_data["request_log"]["id"]
        search = (
            request_id, 
            self.cosine_scores[lang_code][request_id][request_id]
        )
        ranking = [
            (id, score)
            for id,score in enumerate(self.cosine_scores[lang_code][request_id])
            # use all topics with a non-zero similarity score
            if score > 0 and id != request_id 
        ]
        random.shuffle(ranking)
        ranking.insert(0, search)

        input_data["ranked_ids"] = ranking

        return input_data