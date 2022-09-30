import json
import warnings

from survey_tasks.dat.dat import Model as Base


class Model(Base):
    """Create model to compute DAT score from Japanese"""

    def __init__(self, model="dat_model_ja.json", dictionary=None, pattern=None):
        """Load a precomputed model of Japanese noun divergence distances"""

        if dictionary is not None or pattern is not None:
            warnings.warn("Use of a dictionary is not supported for Japanese.")

        # load a dictionary of noun distances from the model
        vectors = {}
        with open(model, "r", encoding="utf8") as f:
            vectors = json.load(f)
        self.vectors = vectors


    def validate(self, word):
        """Clean up word and find best candidate to use"""

        # Strip unwanted characters
        clean = word.strip().replace(" ","").replace("　","")
        if len(clean) == 0:
            return None # Word too short

        if clean not in self.vectors:
            return None # Could not find valid word

        return clean