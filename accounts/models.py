from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Parent(AbstractUser):
    """親モデル"""
    class Meta(AbstractUser.Meta):
        #テーブル名を定義
        db_table = 'puser'
    #テーブルのカラムに対応するフィールドを定義
    photo = models.ImageField(verbose_name='写真', max_length=255)