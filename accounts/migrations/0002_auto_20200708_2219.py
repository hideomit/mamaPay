# Generated by Django 2.2 on 2020-07-08 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parent',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterField(
            model_name='parent',
            name='photo',
            field=models.ImageField(max_length=255, upload_to='', verbose_name='写真'),
        ),
    ]
