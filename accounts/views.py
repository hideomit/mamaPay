from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from task.models import Task
from users.forms import ChildModelForm
from users.models import Child, Balance, Request, History, Parent
from .forms import SignupParentForm, ChildStatusModelForm, ContactForm, EmailChangeForm


# Create your views here.


class ContactView(View):
    template_name = 'contact.html'

    def get_initial(self, request):
        if request.user.is_authenticated:
            return {
                'name': request.user.username,
                'email': request.user.email,
            }
        return {}

    def get(self, request, *args, **kwargs):
        form = ContactForm(initial=self.get_initial(request))
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        contact_to_email = settings.CONTACT_TO_EMAIL
        data = form.cleaned_data
        username = request.user.username if request.user.is_authenticated else '未ログイン'

        message = (
            'お問い合わせが届きました。\n\n'
            'お名前: {name}\n'
            'メールアドレス: {email}\n'
            'ログインユーザー: {username}\n'
            '件名: {subject}\n\n'
            '本文:\n'
            '{message}'
        ).format(
            name=data['name'],
            email=data['email'],
            username=username,
            subject=data['subject'],
            message=data['message'],
        )

        send_mail(
            subject='[いえぺい] {}'.format(data['subject']),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_to_email],
            fail_silently=False,
        )

        return redirect(reverse('contact_done'))


class ContactDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact_done.html')


class EmailChangeView(LoginRequiredMixin, View):
    template_name = 'registration/email_change_form.html'

    def get(self, request, *args, **kwargs):
        form = EmailChangeForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = EmailChangeForm(request.user, request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        request.user.email = form.cleaned_data['email']
        request.user.save(update_fields=['email'])
        return redirect(reverse('email_change_done'))


class EmailChangeDoneView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/email_change_done.html')


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
    model = Balance
    template_name = 'status.html'
    pagenate_by = 10
#2つつくらなきゃダメなんだろうか？

    def get_queryset(self):

        if self.request.user.puser:
            return self.model.objects.filter(cuser__puser=self.request.user.puser)
        else:
            return self.model.objects.filter(cuser=self.request.user.cuser)


class ChildStatusGetView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            balance = Balance.objects.select_related('cuser').get(cuser_id=kwargs['pk'])
        except Balance.DoesNotExist:
            balance = None
        object_list = Request.objects.filter(cuser_id=kwargs['pk'], status='1')

        return render(request, 'children/child_status.html', {'balance': balance, 'object_list': object_list})


class ChildStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildStatusModelForm
    success_url = reverse_lazy('status')


class ChildStatusDetailView(LoginRequiredMixin, DetailView):
    template_name = 'children/children_change.html'
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

            createHistory = History(cuser_id=request_child_id, task_id=request_task_id, task_name=request_task.task_name, amount=request_task.price, kind=1)
            createHistory.ymd = timezone.now()
            createHistory.save()

    def post(self, request, *args, **kwargs):
        request_id_list = request.POST.getlist('approve_task_list')
        self.task_data_save(request_id_list)

        return redirect(reverse('children'))


class ApproveTaskDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('approve_task_list') #単品はrequest.POST.get 複数はrequest.POST.getlist
        Request.objects.filter(id__in=delete_list).delete() #複数の場合は__in=

        approve_child_id = request.POST.get('approve_child_id', None)
        print(approve_child_id)

        return redirect(reverse_lazy('child_status', args=approve_child_id)) #reverseに動的なパラメータを渡す

