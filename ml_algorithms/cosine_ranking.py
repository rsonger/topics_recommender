from pathlib import Path
import joblib

from ml_algorithms.ranking import Ranking

class CosineSimilarityRecommender(Ranking):
    """A ranking recommender that uses cosine similarity scores of topic descriptions."""

    cosine_scores = ()

    def __init__(self, algorithm_name) -> None:
        """Load the artifacts """
        super().__init__(algorithm_name)

        project_dir = Path(__file__).resolve().parent.parent
        path_to_artifacts = Path(project_dir, "data")

        if algorithm_name in self._algorithms_:
            self.tfidf_matrix = joblib.load(
                Path(path_to_artifacts, "tfidf_description_matrix.joblib")
            )
            self.cosine_scores = joblib.load(
                Path(path_to_artifacts, "cosine_sim_scores.joblib")
            )

    def preprocess(self, keyword, id):
        request_data = {}
        if id < 0 or id > len(self.cosine_scores):
            request_data["request_log"] =  {
                "status": "Error", 
                "message": f"Unable to rank topics for {keyword}"
            }
        else:
            request_data["request_log"] = {
                "status": "OK", 
                "topic": keyword, 
                "id": id
            }
        return request_data

    def get_ranking(self, input_data):
        ranking = list(enumerate(self.cosine_scores[input_data["request_log"]["id"]]))
        ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
        
        input_data["ranked_ids"] = ranking

        return input_data