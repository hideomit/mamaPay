from django.db.models import Sum

from users.models import History, TitleRank


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
)


def create_default_title_ranks(parent):
    ranks = []
    for required_total_coin, title in DEFAULT_TITLE_RANKS:
        ranks.append(TitleRank(
            puser=parent,
            title=title,
            required_total_coin=required_total_coin,
            is_active=True,
        ))
    TitleRank.objects.bulk_create(ranks)


def backfill_child_total_earned_coin(child):
    total = History.objects.filter(
        cuser=child,
        kind=1,
        amount__gt=0,
    ).aggregate(total=Sum('amount'))['total'] or 0
    child.total_earned_coin = total
    child.save(update_fields=['total_earned_coin'])
    return total


def get_child_rank_status(child):
    ranks = list(TitleRank.objects.filter(
        puser=child.puser,
        is_active=True,
        delete_flg=False,
    ).order_by('required_total_coin', 'id'))

    if not ranks:
        return {
            'current_rank': None,
            'current_title': '称号未設定',
            'total_earned_coin': child.total_earned_coin,
            'next_rank': None,
            'next_title': None,
            'remaining_coin': None,
            'is_highest': False,
        }

    current_rank = None
    next_rank = None
    for rank in ranks:
        if rank.required_total_coin <= child.total_earned_coin:
            current_rank = rank
            continue
        next_rank = rank
        break

    if current_rank is None:
        current_title = '称号未設定'
    else:
        current_title = current_rank.title

    return {
        'current_rank': current_rank,
        'current_title': current_title,
        'total_earned_coin': child.total_earned_coin,
        'next_rank': next_rank,
        'next_title': next_rank.title if next_rank else None,
        'remaining_coin': max(next_rank.required_total_coin - child.total_earned_coin, 0) if next_rank else None,
        'is_highest': next_rank is None and current_rank is not None,
    }
