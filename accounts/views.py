from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from task.models import Task
from users.forms import ChildModelForm
from users.models import Child, Balance, Request, History, Parent
from .forms import SignupParentForm, ChildStatusModelForm


# Create your views here.


class SignupParentView(CreateView):
    form_class = SignupParentForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    ##同時に親アカウントをつくる
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_user = form.save(commit=False)
            puser = Parent.objects.create()
            login_user.puser = puser
            login_user.save()
            login(self.request, login_user)
            return redirect(reverse_lazy('home'))
        else:
            return redirect(reverse_lazy('home'))


class ChildStatusListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'status.html'
    pagenate_by = 10
#2つつくらなきゃダメなんだろうか？


class ChildStatusGetView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            balance = Balance.objects.select_related('cuser').get(cuser_id=kwargs['pk'])
        except Balance.DoesNotExist:
            balance = None
        object_list = Request.objects.filter(cuser_id=kwargs['pk'], status='1')

        return render(request, 'children\child_status.html', {'balance': balance, 'object_list': object_list})


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
        return render(request, self.template_name, {'form': form, 'data': child})


class HomeListView(LoginRequiredMixin, ListView):
    model = Balance
    template_name = 'home.html'

    def get_queryset(self):

        if self.request.user.puser:
            return self.model.objects.filter(cuser__puser=self.request.user.puser)
        else:
            return self.model.objects.filter(cuser=self.request.user.cuser)

class ApproveTaskView(LoginRequiredMixin, View):

    @transaction.atomic
    def task_data_save(self, request_id_list):

        for request_id in request_id_list:
            applyRequests = Request.objects.get(id=request_id)
            applyRequests.status = 2  ##1が未承認、2が承認
            applyRequests.save()

            request_child_id = applyRequests.cuser_id
            #        print(request_child_id)

            request_task_id = applyRequests.task_id  ## 'task'だとtask名が、'task_id'だとidが取れる・・・
            #       print(request_task_id)

            request_task = Task.objects.get(id=request_task_id)
            #      print(request_task.price)

            if Balance.objects.filter(cuser_id=request_child_id).exists():
                child_balance = Balance.objects.get(cuser_id=request_child_id)
                child_balance.balance = child_balance.balance + request_task.price
            else:
                child_balance = Balance(cuser_id=request_child_id, balance=request_task.price)
            child_balance.save()

            createHistory = History(cuser_id=request_child_id, task_id=request_task_id, amount=request_task.price, kind=1)
            createHistory.ymd = timezone.now()
            createHistory.save()

    def post(self, request, *args, **kwargs):
        request_id_list = request.POST.getlist('approve_task_list')
        self.task_data_save(request_id_list)

        return redirect(reverse('children'))
