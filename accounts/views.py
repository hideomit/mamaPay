from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from users.forms import ChildModelForm
from users.models import Child, Balance, Request
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
        context = Balance.objects.filter(cuser_id=pk)
        object_list = Request.objects.filter(cuser_id=pk, status='1')
        return render(request, 'children\child_status.html', {'context': context, 'object_list': object_list})


class ChildStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildStatusModelForm
    success_url = reverse_lazy('status')


class ChildStatusDetailView(LoginRequiredMixin, DetailView):
    template_name = 'children\children_change.html'
  #  form_class = ChildModelForm
    model = Child

    def get(self, request, *args, **kwargs):
        child = Child.objects.get(id=kwargs['pk']) ##getは1件⇒1レコード、filterは複数⇒query set
        form = ChildModelForm(initial={'name': child.name, 'photo': child.photo})
        return render(request, self.template_name, {'form': form})
