## NOT USED

import joblib
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from survey_tasks.dat.dat import Model

class Command(BaseCommand):
    help = "Generate the NLP model for calculating DAT scores."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("language", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        lang = options["language"]

        