from django.core.management import BaseCommand

from batch.services import SummaryService


class Command(BaseCommand):
    def handle(self, *args, **options):    ##handleは定義。バッチ処理ごとにpythonファイルを増やす
        self.service = SummaryService()
        self.service.summary_child()
