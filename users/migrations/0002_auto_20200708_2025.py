# Generated by Django 2.2 on 2020-07-08 11:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='create_datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='登録日時'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='child',
            name='create_user',
            field=models.CharField(default='admin', max_length=32, verbose_name='登録ユーザ'),
        ),
        migrations.AddField(
            model_name='child',
            name='delete_flg',
            field=models.BooleanField(default=False, verbose_name='削除フラグ'),
        ),
        migrations.AddField(
            model_name='child',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='更新日時'),
        ),
        migrations.AddField(
            model_name='child',
            name='update_user',
            field=models.CharField(default='admin', max_length=32, verbose_name='更新ユーザ'),
        ),
    ]
