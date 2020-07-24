from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render

# Create your views here.
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
