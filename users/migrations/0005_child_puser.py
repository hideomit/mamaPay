# Generated by Django 2.2 on 2020-07-08 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20200708_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='puser',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='親ユーザーID'),
            preserve_default=False,
        ),
    ]
