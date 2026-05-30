from django.db import migrations, models
import django.db.models.deletion


DEFAULT_TITLE_RANKS = (
    (0, 'みならい'),
    (50, 'はじめの一歩'),
    (100, 'おてつだいルーキー'),
    (200, 'おうちサポーター'),
    (300, 'おてつだい名人'),
    (500, '家事チャレンジャー'),
    (700, 'スーパー家事人'),
    (1000, 'おうちヒーロー'),
    (1500, 'おうちの守護者'),
    (2200, '家事マスター'),
    (3000, 'おてつだい隊長'),
    (4000, 'いえぺい達人'),
    (5500, '家族のエース'),
    (7000, 'おうち博士'),
    (9000, 'くらしの名人'),
    (12000, 'おうちの司令塔'),
    (16000, 'いえぺいスター'),
    (21000, '家族の守り神'),
    (27000, 'おうちの大賢者'),
    (35000, 'いえぺいキング'),
    (45000, 'いえぺいレジェンド'),
    (60000, 'おうちの伝説'),
    (75000, 'いえぺいグランドマスター'),
    (90000, 'いえぺいチャンピオン'),
    (100000, 'いえぺい殿堂入り'),
    (200000, 'いえ神様'),
)


def create_default_ranks_and_backfill(apps, schema_editor):
    Parent = apps.get_model('users', 'Parent')
    Child = apps.get_model('users', 'Child')
    History = apps.get_model('users', 'History')
    TitleRank = apps.get_model('users', 'TitleRank')

    for parent in Parent.objects.all():
        existing_required_coins = set(TitleRank.objects.filter(
            puser=parent,
        ).values_list('required_total_coin', flat=True))
        ranks = []
        for required_total_coin, title in DEFAULT_TITLE_RANKS:
            if required_total_coin in existing_required_coins:
                continue
            ranks.append(TitleRank(
                puser=parent,
                title=title,
                required_total_coin=required_total_coin,
                is_active=True,
            ))
        if ranks:
            TitleRank.objects.bulk_create(ranks)

    for child in Child.objects.all():
        total = 0
        histories = History.objects.filter(cuser=child, kind=1, amount__gt=0)
        for history in histories:
            total += history.amount or 0
        child.total_earned_coin = total
        child.save(update_fields=['total_earned_coin'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20260504_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='total_earned_coin',
            field=models.PositiveIntegerField(default=0, verbose_name='累計獲得コイン'),
        ),
        migrations.CreateModel(
            name='TitleRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('create_user', models.CharField(default='admin', max_length=32, verbose_name='登録ユーザ')),
                ('update_datetime', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('update_user', models.CharField(default='admin', max_length=32, verbose_name='更新ユーザ')),
                ('delete_flg', models.BooleanField(default=False, verbose_name='削除フラグ')),
                ('title', models.CharField(max_length=100, verbose_name='称号名')),
                ('required_total_coin', models.PositiveIntegerField(verbose_name='必要累計コイン数')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('puser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Parent', verbose_name='親ユーザーID')),
            ],
            options={
                'db_table': 'title_rank',
                'ordering': ('required_total_coin', 'id'),
                'unique_together': {('puser', 'required_total_coin')},
            },
        ),
        migrations.RunPython(create_default_ranks_and_backfill, noop),
    ]
