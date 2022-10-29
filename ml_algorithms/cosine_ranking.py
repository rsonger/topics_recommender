from pathlib import Path
import joblib

from ml_algorithms.ranking import Ranking

class CosineSimilarityRecommender(Ranking):
    """A ranking recommender that uses cosine similarity scores of topic descriptions."""

    name = "TFIDF Cosine Ranking"

    cosine_scores = ()

    def __init__(self) -> None:
        """Load the artifacts """
        super().__init__()

        project_dir = Path(__file__).resolve().parent.parent
        path_to_artifacts = Path(project_dir, "data")

        self.cosine_scores = {}
        for lang_code in self._languages:
            self.cosine_scores[lang_code] = joblib.load(
                Path(path_to_artifacts, f"cosine_sim_scores_{lang_code}.joblib")
            )

    def preprocess(self, keyword, id, lang_code):
        request_data = {}
        if id < 0 or id > len(self.cosine_scores[lang_code]):
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

    def get_ranking(self, input_data, lang_code):
        ranking = list(enumerate(
            self.cosine_scores[lang_code][input_data["request_log"]["id"]]
        ))
        ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
        
        input_data["ranked_ids"] = ranking

        return input_data