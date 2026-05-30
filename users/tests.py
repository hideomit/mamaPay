from django.test import TestCase
from django.utils import timezone

from ticket.models import Ticket
from users.models import Child, History, Parent, TitleRank
from users.services import DEFAULT_TITLE_RANKS, backfill_child_total_earned_coin, create_default_title_ranks, get_child_rank_status


class TitleRankServiceTests(TestCase):
    def setUp(self):
        self.parent = Parent.objects.create()
        self.other_parent = Parent.objects.create()
        self.child = Child.objects.create(puser=self.parent, name='たろう', total_earned_coin=0)

    def create_rank(self, parent, title, required_total_coin, is_active=True):
        return TitleRank.objects.create(
            puser=parent,
            title=title,
            required_total_coin=required_total_coin,
            is_active=is_active,
        )

    def test_rank_is_decided_by_total_earned_coin(self):
        self.create_rank(self.parent, 'みならい', 0)
        self.create_rank(self.parent, '名人', 100)
        self.create_rank(self.parent, 'レジェンド', 300)
        self.child.total_earned_coin = 250
        self.child.save(update_fields=['total_earned_coin'])

        status = get_child_rank_status(self.child)

        self.assertEqual(status['current_title'], '名人')
        self.assertEqual(status['next_title'], 'レジェンド')
        self.assertEqual(status['remaining_coin'], 50)

    def test_spending_does_not_decrease_total_earned_coin_or_rank(self):
        self.create_rank(self.parent, 'みならい', 0)
        self.create_rank(self.parent, '名人', 100)
        ticket = Ticket.objects.create(puser=self.parent, ticket_name='ゲーム', price=50)
        self.child.total_earned_coin = 120
        self.child.save(update_fields=['total_earned_coin'])
        History.objects.create(cuser=self.child, ticket=ticket, ticket_name=ticket.ticket_name, amount=-50, kind=2, ymd=timezone.now())

        status = get_child_rank_status(self.child)
        self.child.refresh_from_db()

        self.assertEqual(self.child.total_earned_coin, 120)
        self.assertEqual(status['current_title'], '名人')

    def test_ranks_are_separated_by_family(self):
        self.create_rank(self.parent, '家族Aランク', 0)
        self.create_rank(self.other_parent, '家族Bランク', 0)

        status = get_child_rank_status(self.child)

        self.assertEqual(status['current_title'], '家族Aランク')

    def test_remaining_coin_to_next_rank(self):
        self.create_rank(self.parent, 'みならい', 0)
        self.create_rank(self.parent, 'スーパー', 300)
        self.child.total_earned_coin = 220
        self.child.save(update_fields=['total_earned_coin'])

        status = get_child_rank_status(self.child)

        self.assertEqual(status['remaining_coin'], 80)

    def test_no_rank_setting_does_not_break(self):
        status = get_child_rank_status(self.child)

        self.assertEqual(status['current_title'], '称号未設定')
        self.assertIsNone(status['next_rank'])
        self.assertIsNone(status['remaining_coin'])

    def test_backfill_total_earned_coin_uses_only_earned_history(self):
        ticket = Ticket.objects.create(puser=self.parent, ticket_name='ゲーム', price=50)
        History.objects.create(cuser=self.child, task_name='そうじ', amount=100, kind=1, ymd=timezone.now())
        History.objects.create(cuser=self.child, task_name='せんたく', amount=80, kind=1, ymd=timezone.now())
        History.objects.create(cuser=self.child, ticket=ticket, ticket_name=ticket.ticket_name, amount=-50, kind=2, ymd=timezone.now())

        total = backfill_child_total_earned_coin(self.child)
        self.child.refresh_from_db()

        self.assertEqual(total, 180)
        self.assertEqual(self.child.total_earned_coin, 180)

    def test_default_ranks_are_created(self):
        create_default_title_ranks(self.parent)

        self.assertEqual(TitleRank.objects.filter(puser=self.parent).count(), len(DEFAULT_TITLE_RANKS))
        self.assertTrue(TitleRank.objects.filter(puser=self.parent, required_total_coin=0, title='みならい').exists())
        self.assertTrue(TitleRank.objects.filter(puser=self.parent, required_total_coin=100000, title='いえぺい殿堂入り').exists())
