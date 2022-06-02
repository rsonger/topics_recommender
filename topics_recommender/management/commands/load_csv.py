import csv
from django.core.management import BaseCommand
from django.utils import timezone
from topics_recommender.models import Topic

class Command(BaseCommand):
    help = "Load topics and their descriptions from the given CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        with open(file_path, "r") as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                Topic.objects.create(
                    id=row[0],
                    name=row[1],
                    display_name=row[2],
                    short_description=row[3],
                    description=row[4],
                    featured=row[9]
                )
            end_time = timezone.now()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Loading CSV took: {(end_time - start_time).total_seconds()} seconds."
                )
            )