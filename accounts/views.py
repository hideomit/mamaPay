from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from users.models import Child
from .forms import SignupForm, ChildStatusModelForm


# Create your views here.


class SignupView(CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ChildStatusListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'status.html'
    pagenate_by = 10
#2つつくらなきゃダメなんだろうか？


class ChildStatusGetView(LoginRequiredMixin, View):

 #   def get(self, request, *args, **kwargs):
    def get(self, request, pk):
        context = Child.objects.filter(id=pk)
        return render(request, 'children\child_status.html', {'context': context})


class ChildStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildStatusModelForm
    success_url = reverse_lazy('status')


class ChildStatusDetailView(LoginRequiredMixin, DetailView):
    template_name = 'status_change.html'
    model = Child

