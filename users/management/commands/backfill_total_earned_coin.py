from django.core.management.base import BaseCommand

from users.models import Child
from users.services import backfill_child_total_earned_coin


class Command(BaseCommand):
    help = '履歴テーブルからこどもの累計獲得コインを再集計します。'

    def handle(self, *args, **options):
        count = 0
        for child in Child.objects.all():
            total = backfill_child_total_earned_coin(child)
            count += 1
            self.stdout.write('{}: {}コイン'.format(child.name, total))

        self.stdout.write(self.style.SUCCESS('{}人の累計獲得コインを再集計しました。'.format(count)))
