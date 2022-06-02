import joblib
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import pandas as pd

class Command(BaseCommand):
    help = "Load the given Topics data file and calculate cosine similarity scores of topic descriptions."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        p = Path(Path.cwd(), options["file_path"])
        if not p.exists():
            self.stdout.write(
                self.style.ERROR("Data file not found. Aborting command.")
            )
            return

        start_time = timezone.now()

        df_topics = pd.read_csv(p)
        df = df_topics[['description']]

        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df['description'])
        cosine_sim_scores = linear_kernel(tfidf_matrix, tfidf_matrix)

        end_time = timezone.now()

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished calculating cosine similarity scores in {(end_time - start_time).total_seconds()} seconds."
            )
        )

        tfidf_save_file = Path(p.parent, "tfidf_description_matrix.joblib")
        joblib.dump(tfidf_matrix, tfidf_save_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"TFIDF Matrix of topic descriptions saved to {tfidf_save_file}."
            )
        )

        cosine_save_file = Path(p.parent, "cosine_sim_scores.joblib")
        joblib.dump(cosine_sim_scores, cosine_save_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"Cosine similarity scores saved to {cosine_save_file}."
            )
        )