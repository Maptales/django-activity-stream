from django.core.management.base import NoArgsCommand
from actstream.models import Action

class Command(NoArgsCommand):
    help = "Removes Actions that don't have a target anymore"

    def handle_noargs(self, **options):
        for action in Action.objects.all():
            if not action.target:
                action.delete()