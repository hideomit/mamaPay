from django.core.management import BaseCommand

from batch.services import SummaryService


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.service = SummaryService()
        self.service.summary_child()
