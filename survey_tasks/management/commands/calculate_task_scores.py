from pathlib import Path
import joblib

from django.core.management import BaseCommand
from django.utils import timezone

from survey_tasks.models import RecommenderResponse

class Command(BaseCommand):
    help = "Find the cosine similarity scores between the topics chosen for each recommender task response."

    def add_arguments(self, parser):
        parser.add_argument("--scores", type=str, default="data/cosine_sim_scores_en.joblib")

    def handle(self, *args, **options):
        # load the cosine scores from file
        cosine_scores = joblib.load(
            Path(Path.cwd(), options["scores"])
        )

        start_time = timezone.now()

        # get all the recommender task responses
        for response in RecommenderResponse.objects.all():
            # for each response, get the IDs of the chosen topics
            t1 = response.topic1.id
            t2 = response.topic2.id
            t3 = response.topic3.id

            # look up the cosine scores of each topic pair
            score_1_2 = cosine_scores[t1][t2]
            score_2_3 = cosine_scores[t2][t3]
            score_3_1 = cosine_scores[t3][t1]

            # save the cosine scores to the RecommenderResponse object
            response.sim_score_1_2 = score_1_2
            response.sim_score_2_3 = score_2_3
            response.sim_score_3_1 = score_3_1

            response.save()

        end_time = timezone.now()

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished calculating cosine scores in {(end_time - start_time).total_seconds()} seconds."
            )
        )
