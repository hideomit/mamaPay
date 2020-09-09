from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from users.models import Parent, Child


class LoginUsers(AbstractUser):
    """認証用モデル"""
    class Meta(AbstractUser.Meta):
        #テーブル名を定義
        db_table = 'login_users'
    #テーブルのカラムに対応するフィールドを定義
    puser = models.OneToOneField(Parent, verbose_name='親ユーザーID', on_delete=models.CASCADE, null=True)
    cuser = models.OneToOneField(Child, verbose_name='子ユーザーID', on_delete=models.CASCADE, null=True)

