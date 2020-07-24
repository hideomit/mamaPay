from django.db import models

# Create your models here.


class Ticket(models.Model):
    """チケットマスタモデル"""
    class Meta:
        #テーブル名を定義
        db_table = 'ticket'

    # テーブルのカラムに対応するフィールドを定義
    ticket_name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.ticket_name
