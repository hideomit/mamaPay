import calendar
import datetime
import logging

from django.db.models import Q, Count, Sum
from django.utils import timezone

from batch.models import MonthlySummary, MonthlyChildSummary
from users.models import History, Child

logger = logging.getLogger('batch')


class SummaryService:
    def summary(self):
        logger.info('summary_start')

        for history in History.objects.all():
            logger.info('履歴ID={}'.format(history.id))

        dt = timezone.make_aware(datetime.datetime.now())  ##現在の日本時間を取得
        summary_ym = str(dt.year) + str(dt.month).zfill(2)   ##zfillは0埋め。月の表示を01のように2桁で埋める
        last_day = calendar.monthrange(dt.year, dt.month)[1]    ##カレンダーライブラリ。その月の日数が帰ってくる。月初の曜日と日数
        next_month = (datetime.date(dt.year, dt.month, last_day) + datetime.timedelta(days=1)).month

        month_first_day = timezone.make_aware(datetime.datetime(dt.year, dt.month, 1))
        month_next_day = timezone.make_aware(datetime.datetime(dt.year, next_month, 1))

        q_this_month = Q(ymd__range=(month_first_day, month_next_day))
        monthly_amount = History.objects.filter(q_this_month).aggregate(Count('id'), Sum('amount')) ## aggregateは単純集計。

        MonthlySummary.objects.filter(summary_ym=summary_ym).delete()
        MonthlySummary.objects.create(summary_ym=summary_ym,
                                      count=monthly_amount['id__count'],
                                      price=monthly_amount['amount__sum'])


        logger.info('summary_end')

    def summary_child(self):
        logger.info('summary_child_start')

        for child in Child.objects.all():
            logger.info('履歴ID={}'.format(child.id))

        dt = timezone.make_aware(datetime.datetime.now())  ##現在の日本時間を取得
        summary_ym = str(dt.year) + str(dt.month).zfill(2)   ##zfillは0埋め。月の表示を01のように2桁で埋める
        last_day = calendar.monthrange(dt.year, dt.month)[1]    ##カレンダーライブラリ。その月の日数が帰ってくる。月初の曜日と日数
        next_month = (datetime.date(dt.year, dt.month, last_day) + datetime.timedelta(days=1)).month

        month_first_day = timezone.make_aware(datetime.datetime(dt.year, dt.month, 1))
        month_next_day = timezone.make_aware(datetime.datetime(dt.year, next_month, 1))

        q_this_month = Q(history__ymd__range=(month_first_day, month_next_day))
        monthly_amount = Child.objects.filter(q_this_month).annotate(Count('history'), Sum('history__amount'))  ##annotate

#        print(monthly_amount[0].id)

#        for child in Child.objects.filter(q_this_month).annotate(Count('history'), Sum('history__amount')):
#            print('{}:{}:{}'.format(child.id, child.history__count, child.history__amount__sum))

        for ma in monthly_amount:
            MonthlyChildSummary.objects.filter(summary_ym=summary_ym, cuser=ma.id).delete()
            MonthlyChildSummary.objects.create(summary_ym=summary_ym, cuser_id=ma.id, count=ma.history__count, price=ma.history__amount__sum)


        logger.info('summary_child_end')

