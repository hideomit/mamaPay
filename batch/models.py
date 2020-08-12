from django.db import models

# Create your models here.
from users.models import Child


class CommonColumnModel(models.Model):
    """共通カラム"""

    class Meta:
        abstract = True

    create_datetime = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
    create_user = models.CharField(verbose_name='登録ユーザ', max_length=32, default='admin')
    update_datetime = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    update_user = models.CharField(verbose_name='更新ユーザ', max_length=32, default='admin')
    delete_flg = models.BooleanField(verbose_name='削除フラグ', null=False, default=False)


class MonthlySummary(CommonColumnModel):

    class Meta:
        db_table = 'monthly_summary'

    summary_ym = models.CharField(verbose_name='年月', max_length=6, unique=True)
    count = models.IntegerField(verbose_name='取引件数', default=0)
    price = models.IntegerField(verbose_name='取引金額', default=0)

    def __str__(self):
        return self.summary_ym


class MonthlyChildSummary(CommonColumnModel):

    class Meta:
        db_table = 'monthly_child_summary'
        unique_together = ['summary_ym', 'cuser']

    summary_ym = models.CharField(verbose_name='年月', max_length=6)
    cuser = models.ForeignKey(Child, verbose_name='子ユーザーID', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='取引件数', default=0)
    price = models.IntegerField(verbose_name='取引金額', default=0)

    def __str__(self):
        return self.summary_ym

