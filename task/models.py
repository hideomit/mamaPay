from django.db import models

# Create your models here.


class CommonColumnModel(models.Model):
    """共通カラム"""

    class Meta:
        abstract = True

    create_datetime = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
    create_user = models.CharField(verbose_name='登録ユーザ', max_length=32, default='admin')
    update_datetime = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    update_user = models.CharField(verbose_name='更新ユーザ', max_length=32, default='admin')
    delete_flg = models.BooleanField(verbose_name='削除フラグ', null=False, default=False)


class Task(CommonColumnModel):
    """タスクモデル"""
    class Meta:
        #テーブル名を定義
        db_table = 'task'

    #テーブルのカラムに対応するフィールドを定義 appを超えたFKははれない？
    task_name = models.CharField(verbose_name='タスク名', max_length=255)
    price = models.IntegerField(verbose_name='価格', default=0)

    def __str__(self):
        return self.task_name