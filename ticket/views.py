from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect

# Create your views here.
from users.models import Ticket_holding, Child, Balance
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

    def get(self, request, *args, **kwargs):
        child_id = self.kwargs['pk']
        pprint(child_id)
        child_data = Child.objects.get(id=child_id)

        if Balance.objects.filter(cuser_id=child_id).exists():
            balance_data = Balance.objects.get(cuser_id=child_id)
        else:
            balance_data = None

        return render(request, 'ticket/ticket_shop.html', {'child_data': child_data, 'balance_data': balance_data})


class TicketBuyView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        buy_list = request.POST.getlist('buy_list')
        pprint(buy_list)

        for buy_ticket in buy_list:
            createTicket_holding = Ticket_holding(ticket_id=buy_ticket, cuser_id=1)

        createTicket_holding.save()

        return redirect(reverse('children'))