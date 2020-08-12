from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect

# Create your views here.
from users.models import Ticket_holding, Child, Balance, History
from .forms import TicketModelForm
from .models import Ticket


class TicketListView(LoginRequiredMixin, ListView):
    template_name = 'ticket/ticket.html'
    pagenate_by = 10

    def get_queryset(self):
        return Ticket.objects.all()


class TicketRegistView(LoginRequiredMixin, CreateView):
    template_name = 'ticket/ticket_regist.html'

    model = Ticket
    form_class = TicketModelForm
    success_url = reverse_lazy('ticket')


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketModelForm
    success_url = reverse_lazy('ticket')


class TicketDetailView(LoginRequiredMixin, DetailView):
    template_name = 'ticket/ticket_change.html'
    model = Ticket


class TicketDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('delete_list')
        Ticket.objects.filter(id__in=delete_list).delete()
        return redirect(reverse_lazy('ticket'))


class ChildTicketShopView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'ticket/ticket_shop.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs['pk']
        pprint(child_id)
        context['child_data'] = Child.objects.get(id=child_id)
        if Balance.objects.filter(cuser_id=child_id).exists():
            context['balance_data'] = Balance.objects.get(cuser_id=child_id)
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

    def post(self, request, *args, **kwargs):
        buy_list = request.POST.getlist('buy_list')
        child_id = request.POST.get('child_id')

        print('buy_list:{}'.format(buy_list))
        print('child_id:{}'.format(child_id))

        if Balance.objects.filter(cuser_id=child_id).exists():
            childBalance = Balance.objects.get(cuser_id=child_id).balance
        else:
            childBalance = 0

        print('childBalance:{}'.format(childBalance))

        totalAmount = 0
        for buy_ticket in buy_list:
            totalAmount = totalAmount + Ticket.objects.get(id=buy_ticket).price

        print('totalAmount:{}'.format(totalAmount))

        ##返却値を作成
        object_list = Ticket.objects.filter(id__in=buy_list)
        child_data = Balance.objects.select_related('cuser').get(cuser_id=child_id)

        if totalAmount > childBalance:
            return render(request, 'ticket/ticket_shop_incomplete.html', {'object_list': object_list, 'child_data': child_data})
        else:
            ##チケット保持リストを更新
            for buy_ticket in buy_list:
                ticket_holding = Ticket_holding(ticket_id=buy_ticket, cuser_id=child_id)
                ticket_holding.save()

            ##残高を更新
            balance = Balance.objects.get(cuser_id=child_id)
            balance.balance = childBalance - totalAmount
            balance.save()

            ##履歴を更新
            for buy_ticket in buy_list:
                ticket_price = Ticket.objects.get(id=buy_ticket).price
                history = History(cuser_id=child_id, ticket_id=buy_ticket, amount=-ticket_price, kind=2)
                history.ymd = timezone.now()
                history.save()

            ##返却値を更新
            child_data = Balance.objects.select_related('cuser').get(cuser_id=child_id)

            return render(request, 'ticket/ticket_shop_complete.html', {'object_list': object_list, 'child_data': child_data})


class ChildHoldingTicketView(LoginRequiredMixin, ListView):
    model = Ticket_holding
    template_name = 'ticket/use_ticket.html'

    def get_queryset(self):
        return Ticket_holding.objects.filter(cuser_id=self.kwargs['pk'], used_flg=0)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs['pk']
        pprint(child_id)
        context['child_data'] = Child.objects.get(id=child_id)

        return context


class TicketUseView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        use_list = request.POST.getlist('use_list')
        child_id = request.POST.get('child_id')

        for ticket in use_list:
            ##チケット保有リストの更新  ##履歴の更新
            ticket_holding = Ticket_holding.objects.filter(ticket_id=ticket, cuser_id=child_id, used_flg=0).first()
            ticket_holding.used_flg = '1'  ##使用済み
            print(ticket_holding.used_flg)
            ticket_holding.save()

            history = History(cuser_id=child_id, ticket_id=ticket, kind=3, ticket_holding_id=ticket_holding.id)
            history.ymd = timezone.now()
            history.save()

        ##返却値を作成
        object_list = Ticket.objects.filter(id__in=use_list)
        child_data = Balance.objects.select_related('cuser').get(cuser_id=child_id)

        return render(request, 'ticket/use_ticket_complete.html', {'object_list': object_list, 'child_data': child_data})