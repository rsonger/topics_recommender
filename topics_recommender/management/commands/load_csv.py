import csv

from django.core.management import BaseCommand
from django.utils import timezone

from topics_recommender.models import Topic

class Command(BaseCommand):
    help = "Load topics and their descriptions from the given CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("language", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        lang = options["language"]
        with open(file_path, "r") as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                topic, _ = Topic.objects.get_or_create(
                    id=row[0],
                )
                topic.set_current_language(lang)

                topic.name = row[1]
                topic.display_name = row[2]
                topic.short_description = row[3]
                topic.description = row[4]
                topic.featured=row[9]

                topic.save()
                
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time - start_time).total_seconds()} seconds."
            )
        )