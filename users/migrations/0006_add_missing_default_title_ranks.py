from django.db import migrations


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


OLD_DEFAULT_TITLE_BY_COIN = {
    0: 'みならい',
    100: 'おてつだい名人',
    300: 'スーパー家事人',
    700: 'おうちの守護者',
    1500: 'いえぺいレジェンド',
}


def add_missing_default_title_ranks(apps, schema_editor):
    Parent = apps.get_model('users', 'Parent')
    TitleRank = apps.get_model('users', 'TitleRank')

    for parent in Parent.objects.all():
        existing_by_coin = {
            rank.required_total_coin: rank
            for rank in TitleRank.objects.filter(puser=parent)
        }
        ranks_to_create = []

        for required_total_coin, title in DEFAULT_TITLE_RANKS:
            existing_rank = existing_by_coin.get(required_total_coin)
            if existing_rank is None:
                ranks_to_create.append(TitleRank(
                    puser=parent,
                    title=title,
                    required_total_coin=required_total_coin,
                    is_active=True,
                    delete_flg=False,
                ))
                continue

            if existing_rank.delete_flg or not existing_rank.is_active:
                existing_rank.title = title
                existing_rank.is_active = True
                existing_rank.delete_flg = False
                existing_rank.save(update_fields=['title', 'is_active', 'delete_flg', 'update_datetime'])
                continue

            if existing_rank.title == OLD_DEFAULT_TITLE_BY_COIN.get(required_total_coin) and existing_rank.title != title:
                existing_rank.title = title
                existing_rank.save(update_fields=['title', 'update_datetime'])

        if ranks_to_create:
            TitleRank.objects.bulk_create(ranks_to_create)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_drop_title_rank_display_order_if_exists'),
    ]

    operations = [
        migrations.RunPython(add_missing_default_title_ranks, noop),
    ]
