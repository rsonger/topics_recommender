from pathlib import Path

from survey_tasks.dat.dat import Model as Model_EN
from survey_tasks.dat.dat_ja import Model as Model_JA

class DATModels:
    _instance = None # singleton

    _SUPPORTED_MODELS = ("en", "ja")
    
    _models = {}

    def __init__(self):
        # this logic has been moved inside __new__
        pass

    def __new__(cls):
        self = cls._instance
        if self is None:
            print("Initializing DAT models...")

            self = super(DATModels, cls).__new__(cls)

            # load the English model
            mod = Path(__file__).resolve().parent / 'dat' / 'glove.840B.300d.txt'
            dict = Path(__file__).resolve().parent / 'dat' / 'words.txt'
            self._models["en"] = Model_EN(model=mod, dictionary=dict)

            # load the Japanese model
            mod = Path(__file__).resolve().parent / 'dat' / 'dat_model_ja.json'
            self._models["ja"] = Model_JA(model=mod)

            cls._instance = self

            print("Models loaded successfully.\n")
        return self

    def get_model(self, lang_code="en"):
        if lang_code.lower() not in self._SUPPORTED_MODELS:
            raise ValueError(f"Language code {lang_code} is not currently supported.")

        return self._models[lang_code]        
