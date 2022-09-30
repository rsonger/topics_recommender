import joblib
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from sudachipy import dictionary

from nltk.tokenize import wordpunct_tokenize 

import pandas as pd

class Command(BaseCommand):
    help = "Load the given Topics data file and calculate cosine similarity scores of topic descriptions."

    _SUPPORTED_LANGUAGES = ["en","ja"]

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("language", type=str)

    def handle(self, *args, **options):
        p = Path(Path.cwd(), options["file_path"])
        if not p.exists():
            self.stdout.write(
                self.style.ERROR("Data file not found. Aborting command.")
            )
            return
        lang = options["language"]
        if lang.lower() not in self._SUPPORTED_LANGUAGES:
            self.stdout.write(
                self.style.ERROR(f"Language must be one of {self._SUPPORTED_LANGUAGES}")
            )
            return

        start_time = timezone.now()

        df_topics = pd.read_csv(p, index_col=0)
        descriptions = pd.Series(df_topics.description)

        if lang == 'en':
            descriptions = descriptions.str.lower()
            tokenizer = wordpunct_tokenize
            stop_words = []
            with open("data/stopwords_en.txt") as f:
                stop_words = [w.strip() for w in f]

        if lang == 'ja':
            tokenizer_ja = dictionary.Dictionary(dict_type="full").create()
            def sudachi_tokenize(text):
                morphs = tokenizer_ja.tokenize(text)
                return [m.surface() for m in morphs]

            tokenizer = sudachi_tokenize
            stop_words = []
            with open("data/stopwords_ja.txt") as f:
                stop_words = [w.strip() for w in f]

        tfidf = TfidfVectorizer(tokenizer=tokenizer, stop_words=stop_words)
        tfidf_matrix = tfidf.fit_transform(descriptions)
        cosine_sim_scores = linear_kernel(tfidf_matrix, tfidf_matrix)

        end_time = timezone.now()

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished calculating cosine similarity scores in {(end_time - start_time).total_seconds()} seconds."
            )
        )

        tfidf_save_file = Path(p.parent, f"tfidf_description_matrix_{lang}.joblib")
        joblib.dump(tfidf_matrix, tfidf_save_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"TFIDF Matrix of topic descriptions saved to {tfidf_save_file}."
            )
        )

        cosine_save_file = Path(p.parent, f"cosine_sim_scores_{lang}.joblib")
        joblib.dump(cosine_sim_scores, cosine_save_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"Cosine similarity scores saved to {cosine_save_file}."
            )
        )