from django.core.management import BaseCommand

from ml_algorithms.registry import MLRegistry
from ml_api.models import Endpoint, ABTest

class Command(BaseCommand):
    help = "Commands for managing A/B Tests."

    def add_arguments(self, parser):
        parser.add_argument("command", type=str)
        parser.add_argument("endpointname", type=str)

    def handle(self, *args, **options):
        # check the arguments first
        commands = ["begin", "end"]
        if options["command"] not in commands:
            self.stdout.write(
                self.style.ERROR(
                    f"  ERROR: command must be one of [{' | '.join(commands)}]."
                )
            )
            return
        ep = Endpoint.objects.filter(name=options["endpointname"])
        if not ep.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"  ERROR: endpoint not found: {options['endpointname']}"
                )
            )
            return

        # good to proceed
        ep = ep.first()
        registry = MLRegistry()

        if options["command"] == commands[0]:     
            # begin a new A/B Test
            registry.register_ab_testing(ep.name)
            registry.begin_ab_testing(ep.name)
        elif options["command"] == commands[1]: 
            # end the current A/B Test
            registry.end_ab_testing(ep.name)