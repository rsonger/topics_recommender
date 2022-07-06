import abc

from topics_recommender.models import Topic
from Topics_RS.settings import LANGUAGES

class Ranking():
    """A ranking recommender that returns a list of 10 topics recommended based on a given topic."""

    ALGORITHM_TFIDF = "Term Frequency-Inverse Document Frequency"
    ALGORITHM_RANDOM = "Random"

    _algorithms = [ALGORITHM_TFIDF, ALGORITHM_RANDOM]

    _languages = [lang for lang, _ in LANGUAGES]

    def __init__(self, algorithm_name) -> None:
        if algorithm_name not in self._algorithms:
            raise Exception(f"Usupported algorithm: {algorithm_name}")


    @abc.abstractmethod
    def preprocess(self, keyword, id, lang_code):
        pass


    @abc.abstractmethod
    def get_ranking(self, input_data, lang_code):
        pass


    def postprocess(self, prediction, total_ranks):
        """Prepare the prediction with data to be logged in the MLRequest
        as well as ranking data for the template to render."""
        prediction["request_log"]["top_ranks"] = total_ranks
        top_ranks = {
            "all": [],
            "featured": []
        }
        top_ids = prediction["ranked_ids"]
        prediction["ranked_ids"] = []
        for id, score in top_ids:
            topic_obj = Topic.objects.get(id=id)

            prediction["ranked_ids"].append((id, score))

            top_ranks["all"].append({
                "name": topic_obj.name,
                "display_name": topic_obj.display_name,
                "featured": topic_obj.featured,
                "short_description": topic_obj.short_description,
                "description": topic_obj.description,
            })
            if topic_obj.featured:
                top_ranks["featured"].append({
                    "name": topic_obj.name,
                    "display_name": topic_obj.display_name,
                    "featured": topic_obj.featured,
                    "short_description": topic_obj.short_description,
                    "description": topic_obj.description,
                })
                # the first item will always be the searched topic,
                # so add rankings up to and including total_ranks index
                if len(top_ranks["featured"]) == total_ranks + 1:
                    top_ranks["all"] = top_ranks["all"][:total_ranks + 1]
                    break

        prediction["ranking"] = top_ranks
        return prediction


    def make_ranking(self, keyword, id, top_ranks, lang_code):
        try:
            input_data = self.preprocess(keyword, id, lang_code)
            if input_data["request_log"]["status"] != "OK":
                return input_data
            ranking = self.get_ranking(input_data, lang_code)
            result = self.postprocess(ranking, top_ranks)
        except Exception as e:
            return {
                "request_log": {
                    "status": "Error", 
                    "message": e
                }
            }
        return result