

from django.db import models

# Create your models here.
# 共通カラムを定義（appを超えるのは不可？）
from accounts.models import Parent
from task.models import Task
from ticket.models import Ticket


class CommonColumnModel(models.Model):
    """共通カラム"""

    class Meta:
        abstract = True

    create_datetime = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
    create_user = models.CharField(verbose_name='登録ユーザ', max_length=32, default='admin')
    update_datetime = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    update_user = models.CharField(verbose_name='更新ユーザ', max_length=32, default='admin')
    delete_flg = models.BooleanField(verbose_name='削除フラグ', null=False, default=False)


class Child(CommonColumnModel):
    """子供モデル"""
    class Meta:
        #テーブル名を定義
        db_table = 'cuser'

    #テーブルのカラムに対応するフィールドを定義 appを超えたFKははれない？⇒　importすればよい
    puser = models.ForeignKey(Parent, verbose_name='親ユーザーID', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='名前', max_length=255)
    photo = models.ImageField(verbose_name='写真', null=True, max_length=255, upload_to='Child/')

    def __str__(self):
        return str(self.name)


class Balance(CommonColumnModel):
    """残高"""
    class Meta:
        #テーブル名を定義
        db_table = 'balance'

    cuser = models.ForeignKey(Child, verbose_name='子ユーザーID', on_delete=models.CASCADE)
    balance = models.IntegerField(verbose_name='残高', default=0)

    def __str__(self):
        return str(self.cuser)

class Ticket_holding(CommonColumnModel):
    """保有チケット"""
    class Meta:
        #テーブル名を定義
        db_table = 'ticket_holding'

    cuser = models.ForeignKey(Child, verbose_name='子ユーザーid', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, verbose_name='チケットID', on_delete=models.CASCADE)
    used_flg = models.IntegerField(verbose_name='利用フラグ', default=0)

    def __str__(self):
        return str(self.balance)

class Request(CommonColumnModel):
    """リクエスト・承認"""
    class Meta:
        #テーブル名を定義
        db_table = 'request'

    cuser = models.ForeignKey(Child, verbose_name='子ユーザーID', on_delete=models.CASCADE)
    puser = models.ForeignKey(Parent, verbose_name='親ユーザーID', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, verbose_name='タスクID', on_delete=models.CASCADE)
    status = models.IntegerField(verbose_name='ステータス', default=1)

    def __str__(self):
        return str(self.cuser)

class History(CommonColumnModel):
    class Meta:
        #テーブル名を定義
        db_table = 'history'
    ymd = models.DateTimeField(verbose_name='入出金日時')
    cuser = models.ForeignKey(Child, verbose_name='子ユーザーID', on_delete=models.PROTECT)
    task = models.ForeignKey(Task, verbose_name='タスクID', on_delete=models.PROTECT, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, verbose_name='チケットID', on_delete=models.PROTECT, null=True, blank=True)
    amount = models.IntegerField(verbose_name='金額', default=0)

    def __str__(self):
        return str(self.ymd)


class History_ticket(CommonColumnModel):
    class Meta:
        #テーブル名を定義
        db_table = 'history_ticket'

    ymd = models.DateTimeField(verbose_name='入出金日時')
    ticket_holding = models.ForeignKey(Ticket_holding, verbose_name='チケット保有ID', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.ymd)
