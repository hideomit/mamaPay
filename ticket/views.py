from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from accounts.models import LoginUsers
from users.models import Ticket_holding, Child, Balance, History
from .forms import TicketModelForm
from .models import Ticket


TICKET_TEMPLATE_GROUPS = {
    'preschool': {
        'label': '幼児テンプレート',
        'description': '小さな楽しみと生活リズムに合うチケットです。',
        'items': [
            {'ticket_name': '好きなおやつ', 'price': 50},
            {'ticket_name': '絵本を1冊よんでもらう', 'price': 40},
            {'ticket_name': '公園であそぶ', 'price': 80},
            {'ticket_name': 'シールを1枚えらぶ', 'price': 30},
            {'ticket_name': '好きな動画を10分みる', 'price': 60},
        ],
    },
    'elementary': {
        'label': '小学生テンプレート',
        'description': '遊び・おやつ・家族時間を組み合わせたチケットです。',
        'items': [
            {'ticket_name': 'ゲーム30分', 'price': 120},
            {'ticket_name': '好きなおやつ', 'price': 80},
            {'ticket_name': 'ガチャ1回', 'price': 150},
            {'ticket_name': '夜ごはんリクエスト', 'price': 200},
            {'ticket_name': '家族でボードゲーム', 'price': 100},
        ],
    },
    'junior_high': {
        'label': '中学生テンプレート',
        'description': '自分時間や少し大きめのごほうび向けチケットです。',
        'items': [
            {'ticket_name': 'スマホ30分', 'price': 150},
            {'ticket_name': 'コンビニスイーツ', 'price': 180},
            {'ticket_name': '好きな動画を30分みる', 'price': 140},
            {'ticket_name': '休日の外食リクエスト', 'price': 400},
            {'ticket_name': '本・文具を買う', 'price': 300},
        ],
    },
}


def get_permitted_child(user, child_id):
    child = get_object_or_404(Child, id=child_id)

    if user.puser_id and child.puser_id == user.puser_id:
        return child
    if user.cuser_id and child.id == user.cuser_id:
        return child

    raise PermissionDenied


class TicketListView(LoginRequiredMixin, ListView):
    template_name = 'ticket/ticket.html'
    pagenate_by = 10

    def get_queryset(self):
        queryset = Ticket.objects.all()
        if hasattr(self.request.user, 'puser') and self.request.user.puser:
            queryset = queryset.filter(puser=self.request.user.puser)
        return queryset


class TicketRegistView(LoginRequiredMixin, CreateView):
    template_name = 'ticket/ticket_regist.html'

    model = Ticket
    form_class = TicketModelForm
    success_url = reverse_lazy('ticket')

    def form_valid(self, form):
        form.instance.puser = self.request.user.puser
        return super().form_valid(form)


class TicketTemplateView(LoginRequiredMixin, View):
    template_name = 'ticket/ticket_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'template_groups': TICKET_TEMPLATE_GROUPS})

    def post(self, request, *args, **kwargs):
        if not request.user.puser_id:
            raise PermissionDenied

        template_key = request.POST.get('template_key')
        template_group = TICKET_TEMPLATE_GROUPS.get(template_key)
        if not template_group:
            raise PermissionDenied

        existing_names = set(Ticket.objects.filter(
            puser=request.user.puser,
            ticket_name__in=[item['ticket_name'] for item in template_group['items']],
        ).values_list('ticket_name', flat=True))

        created_count = 0
        skipped_count = 0
        for item in template_group['items']:
            if item['ticket_name'] in existing_names:
                skipped_count += 1
                continue
            Ticket.objects.create(
                puser=request.user.puser,
                ticket_name=item['ticket_name'],
                price=item['price'],
            )
            created_count += 1

        return render(request, self.template_name, {
            'template_groups': TICKET_TEMPLATE_GROUPS,
            'selected_template': template_group,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'back_url': reverse('ticket'),
        })


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketModelForm
    success_url = reverse_lazy('ticket')

    def get_queryset(self):
        return Ticket.objects.filter(puser=self.request.user.puser)


class TicketDetailView(LoginRequiredMixin, DetailView):
    template_name = 'ticket/ticket_change.html'
    model = Ticket

    def get_queryset(self):
        return Ticket.objects.filter(puser=self.request.user.puser)


class TicketDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('delete_list')
        Ticket.objects.filter(id__in=delete_list, puser=self.request.user.puser).delete()
        return redirect(reverse_lazy('ticket'))


class ChildTicketShopView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'ticket/ticket_shop.html'

    def get_child(self):
        return get_permitted_child(self.request.user, self.kwargs['pk'])

    def get_queryset(self):
        child = self.get_child()
        return Ticket.objects.filter(puser=child.puser)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        child = self.get_child()
        pprint(child.id)
        context['child_data'] = child
        if Balance.objects.filter(cuser=child).exists():
            context['balance_data'] = Balance.objects.get(cuser=child)
        else:
            context['balance_data'] = None

        return context

# 以下、動いたけどListのobject_listが上書きされた
 #   def get(self, request, *args, **kwargs):
 #       child_id = self.kwargs['pk']
 #       pprint(child_id)
 #       child_data = Child.objects.get(id=child_id)
#
#        if Balance.objects.filter(cuser_id=child_id).exists():
#            balance_data = Balance.objects.get(cuser_id=child_id)
#        else:
#            balance_data = None
#
#        return render(request, 'ticket/ticket_shop.html', {'child_data': child_data, 'balance_data': balance_data})


class TicketBuyView(LoginRequiredMixin, View):
    max_buy_quantity = 10

    def get_ticket_quantities(self, request):
        ticket_quantities = {}
        for key, value in request.POST.items():
            if not key.startswith('ticket_quantity_'):
                continue

            try:
                ticket_id = int(key.replace('ticket_quantity_', '', 1))
                quantity = int(value)
            except ValueError:
                raise PermissionDenied

            if quantity < 0 or quantity > self.max_buy_quantity:
                raise PermissionDenied
            if quantity > 0:
                ticket_quantities[ticket_id] = quantity

        if not ticket_quantities:
            raise PermissionDenied

        return ticket_quantities

    def get_ticket_summary(self, tickets, ticket_quantities):
        summary_list = []
        for ticket in tickets:
            count = ticket_quantities.get(ticket.id, 0)
            if count <= 0:
                continue
            summary_list.append({
                'ticket': ticket,
                'count': count,
                'total_price': ticket.price * count,
            })
        return summary_list

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        child_id = request.POST.get('child_id')
        child = get_permitted_child(self.request.user, child_id)

        print('child_id:{}'.format(child.id))

        if Balance.objects.filter(cuser=child).exists():
            childBalance = Balance.objects.get(cuser=child).balance
        else:
            childBalance = 0

        print('childBalance:{}'.format(childBalance))

        ticket_quantities = self.get_ticket_quantities(request)
        posted_ticket_ids = set(ticket_quantities.keys())

        object_list = list(Ticket.objects.filter(id__in=posted_ticket_ids, puser=child.puser))
        valid_ticket_ids = {ticket.id for ticket in object_list}

        if valid_ticket_ids != posted_ticket_ids:
            raise PermissionDenied

        ticket_map = {ticket.id: ticket for ticket in object_list}
        totalAmount = sum(ticket_map[ticket_id].price * quantity for ticket_id, quantity in ticket_quantities.items())
        ticket_summary_list = self.get_ticket_summary(object_list, ticket_quantities)

        print('totalAmount:{}'.format(totalAmount))

        ##返却値を作成
        child_data = Balance.objects.select_related('cuser').get(cuser=child)

        if totalAmount > childBalance:
            return render(request, 'ticket/ticket_shop_incomplete.html', {
                'object_list': object_list,
                'ticket_summary_list': ticket_summary_list,
                'child_data': child_data,
            })
        else:
            ##チケット保持リストを更新
            for ticket_id, quantity in ticket_quantities.items():
                for _ in range(quantity):
                    ticket_holding = Ticket_holding(ticket_id=ticket_id, cuser=child)
                    ticket_holding.save()

            ##残高を更新
            balance = Balance.objects.get(cuser=child)
            balance.balance = childBalance - totalAmount
            balance.save()

            ##履歴を更新
            for ticket_id, quantity in ticket_quantities.items():
                ticket_obj = ticket_map[ticket_id]
                ticket_price = ticket_obj.price
                for _ in range(quantity):
                    history = History(cuser=child, ticket_id=ticket_id, ticket_name=ticket_obj.ticket_name, amount=-ticket_price, kind=2)
                    history.ymd = timezone.now()
                    history.save()

            ##返却値を更新
            child_data = Balance.objects.select_related('cuser').get(cuser=child)

            return render(request, 'ticket/ticket_shop_complete.html', {
                'object_list': object_list,
                'ticket_summary_list': ticket_summary_list,
                'child_data': child_data,
            })


class ChildHoldingTicketView(LoginRequiredMixin, ListView):
    model = Ticket_holding
    template_name = 'ticket/use_ticket.html'

    def get_child(self):
        return get_permitted_child(self.request.user, self.kwargs['pk'])

    def get_queryset(self):
        child = self.get_child()
        return Ticket_holding.objects.select_related('ticket').filter(
            cuser=child,
            used_flg=0,
            ticket__puser=child.puser,
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        child = self.get_child()
        pprint(child.id)
        context['child_data'] = child
        context['balance_data'] = Balance.objects.select_related('cuser').get(cuser=child)

        return context


class TicketUseView(LoginRequiredMixin, View):

    def send_use_notification(self, request, child, used_tickets):
        if not used_tickets:
            return

        parent_user = LoginUsers.objects.filter(puser=child.puser).first()
        if not parent_user or not parent_user.email:
            return

        ticket_lines = '\n'.join(
            ['・{}（{}コイン）'.format(ticket.ticket_name, ticket.price) for ticket in used_tickets]
        )
        total_coin = sum(ticket.price for ticket in used_tickets)
        confirm_url = request.build_absolute_uri(reverse('child_home', args=[child.id]))

        message = (
            '{child_name}さんがチケットを利用しました。\n\n'
            'チケット名:\n{ticket_lines}\n\n'
            '利用チケットのコイン合計: {total_coin}コイン\n\n'
            '確認リンク:\n{confirm_url}\n'
        ).format(
            child_name=child.name,
            ticket_lines=ticket_lines,
            total_coin=total_coin,
            confirm_url=confirm_url,
        )

        send_mail(
            subject='【いえペイ】{}さんがチケットを利用しました'.format(child.name),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_user.email],
        )

    def post(self, request, *args, **kwargs):
        use_list = request.POST.getlist('use_list')
        child_id = request.POST.get('child_id')
        child = get_permitted_child(self.request.user, child_id)

        try:
            posted_ticket_ids = [int(ticket_id) for ticket_id in use_list]
        except ValueError:
            raise PermissionDenied

        valid_ticket_ids = set(Ticket.objects.filter(
            id__in=posted_ticket_ids,
            puser=child.puser,
        ).values_list('id', flat=True))

        if valid_ticket_ids != set(posted_ticket_ids):
            raise PermissionDenied

        used_tickets = []

        for ticket in posted_ticket_ids:
            ##チケット保有リストの更新  ##履歴の更新
            ticket_holding = Ticket_holding.objects.select_related('ticket').filter(
                ticket_id=ticket,
                cuser=child,
                ticket__puser=child.puser,
                used_flg=0,
            ).first()
            if not ticket_holding:
                raise PermissionDenied
            ticket_holding.used_flg = '1'  ##使用済み
            print(ticket_holding.used_flg)
            ticket_holding.save()

            ticket_obj = ticket_holding.ticket
            used_tickets.append(ticket_obj)
            history = History(cuser=child, ticket_id=ticket, ticket_name=ticket_obj.ticket_name, kind=3, ticket_holding_id=ticket_holding.id)
            history.ymd = timezone.now()
            history.save()

        ##返却値を作成
        self.send_use_notification(request, child, used_tickets)

        object_list = used_tickets
        child_data = Balance.objects.select_related('cuser').get(cuser=child)

        return render(request, 'ticket/use_ticket_complete.html', {'object_list': object_list, 'child_data': child_data})
