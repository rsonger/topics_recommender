from django.core.management import BaseCommand
from django.utils import timezone

from survey_tasks.dat_models import DATModels
from survey_tasks.models import DATResponse

class Command(BaseCommand):
    help = "Generate the NLP model for calculating DAT scores."

    _SUPPORTED_LANGUAGES = ["en","ja"]

    def add_arguments(self, parser):
        parser.add_argument("language", type=str, default="en")

    def handle(self, *args, **options):
        lang = options["language"]

        if lang.lower() not in self._SUPPORTED_LANGUAGES:
            self.stdout.write(
                self.style.ERROR(f"Language must be one of {self._SUPPORTED_LANGUAGES}")
            )
            return

        self.stdout.write("Calculating DAT scores for every task response...")

        start_time = timezone.now()
        
        dat_model = DATModels().get_model(lang)
        responses = DATResponse.objects.filter(words__language_code=lang).distinct()

        for resp in responses:
            words = list(resp.words.all().values_list('value', flat=True))
            score = dat_model.dat(words)
            self.stdout.write(str(score))

            resp.dat_score = score
            resp.save()

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished calculating DAT scores in {(end_time - start_time).total_seconds()} seconds."
            )
        )
