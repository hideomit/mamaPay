import random
from collections import OrderedDict

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from task.models import Task
from users.forms import ChildModelForm
from users.models import Child, Balance, Request, History, Parent
from .forms import SignupParentForm, ChildStatusModelForm, ContactForm, EmailChangeForm, ChildPasswordChangeForm
from .models import LoginUsers
from .tokens import account_activation_token


# Create your views here.


def build_child_status_context(child, selection_error=None):
    try:
        balance = Balance.objects.select_related('cuser').get(cuser=child)
    except Balance.DoesNotExist:
        balance = None

    object_list = Request.objects.select_related('task').filter(cuser=child, puser=child.puser, status=1)
    request_group_map = OrderedDict()
    for apply_request in object_list:
        task_id = apply_request.task_id
        if task_id not in request_group_map:
            request_group_map[task_id] = {
                'task': apply_request.task,
                'request_ids': [],
                'count': 0,
                'total_price': 0,
            }
        request_group_map[task_id]['request_ids'].append(str(apply_request.id))
        request_group_map[task_id]['count'] += 1
        request_group_map[task_id]['total_price'] += apply_request.task.price

    return {
        'balance': balance,
        'object_list': object_list,
        'request_group_list': list(request_group_map.values()),
        'selection_error': selection_error,
    }


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


class AccountDeactivateView(LoginRequiredMixin, View):
    template_name = 'registration/account_deactivate.html'

    def get(self, request, *args, **kwargs):
        if not request.user.puser_id:
            raise PermissionDenied
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if not request.user.puser_id:
            raise PermissionDenied

        if request.POST.get('confirm_deactivate') != '1':
            return render(request, self.template_name, {'confirm_error': '退会するには確認チェックを入れてください。'})

        LoginUsers.objects.filter(cuser__puser=request.user.puser).update(is_active=False)
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])
        logout(request)
        return redirect(reverse('account_deactivate_done'))


class AccountDeactivateDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/account_deactivate_done.html')


class ChildPasswordChangeView(LoginRequiredMixin, View):
    template_name = 'children/child_password_change.html'

    def get_child(self):
        child = get_object_or_404(Child, id=self.kwargs['pk'])

        if self.request.user.puser_id and child.puser_id == self.request.user.puser_id:
            return child

        raise PermissionDenied

    def get_login_user(self, child):
        return get_object_or_404(LoginUsers, cuser=child)

    def get(self, request, *args, **kwargs):
        child = self.get_child()
        login_user = self.get_login_user(child)
        form = ChildPasswordChangeForm(login_user)
        return render(request, self.template_name, {'form': form, 'child': child, 'login_user': login_user})

    def post(self, request, *args, **kwargs):
        child = self.get_child()
        login_user = self.get_login_user(child)
        form = ChildPasswordChangeForm(login_user, request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'child': child, 'login_user': login_user})

        login_user.set_password(form.cleaned_data['password1'])
        login_user.save(update_fields=['password'])
        return redirect(reverse('child_password_change_done', args=[child.id]))


class ChildPasswordChangeDoneView(LoginRequiredMixin, View):
    template_name = 'children/child_password_change_done.html'

    def get_child(self):
        child = get_object_or_404(Child, id=self.kwargs['pk'])

        if self.request.user.puser_id and child.puser_id == self.request.user.puser_id:
            return child

        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        child = self.get_child()
        return render(request, self.template_name, {'child': child})


class SignupParentView(CreateView):
    form_class = SignupParentForm
    success_url = reverse_lazy('accounts:signup_activation_sent')
    template_name = 'registration/signup.html'

    ##同時に親アカウントをつくる
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_user = form.save(commit=False)
            puser = Parent.objects.create()
            login_user.puser = puser
            login_user.is_active = False
            login_user.save()
            self.send_activation_mail(request, login_user)
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})

    def send_activation_mail(self, request, user):
        activation_url = request.build_absolute_uri(reverse('accounts:activate', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }))
        message = (
            'いえぺいへのご登録ありがとうございます。\n\n'
            '以下のURLをクリックして、登録を完了してください。\n\n'
            '{activation_url}\n\n'
            'このURLに心当たりがない場合は、このメールを破棄してください。'
        ).format(activation_url=activation_url)

        send_mail(
            subject='【いえぺい】登録を完了してください',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class SignupActivationSentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/signup_activation_sent.html')


class AccountActivateView(View):
    def get_user(self, uidb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            return LoginUsers.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, LoginUsers.DoesNotExist):
            return None

    def get(self, request, *args, **kwargs):
        user = self.get_user(kwargs['uidb64'])
        token = kwargs['token']

        if user is None or not account_activation_token.check_token(user, token):
            return redirect(reverse('accounts:activate_invalid'))

        if LoginUsers.objects.exclude(pk=user.pk).filter(email=user.email, is_active=True).exists():
            return redirect(reverse('accounts:activate_invalid'))

        user.is_active = True
        user.save(update_fields=['is_active'])
        return redirect(reverse('accounts:activate_done'))


class AccountActivateDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/signup_activate_done.html')


class AccountActivateInvalidView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/signup_activate_invalid.html')


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

    def get_child(self, child_id):
        child = get_object_or_404(Child, id=child_id)

        if self.request.user.puser_id and child.puser_id == self.request.user.puser_id:
            return child

        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        child = self.get_child(kwargs['pk'])
        return render(request, 'children/child_status.html', build_child_status_context(child))


class ChildStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildStatusModelForm
    success_url = reverse_lazy('status')


class ChildStatusDetailView(LoginRequiredMixin, DetailView):
    template_name = 'children/children_change.html'
    default_child_photos = tuple('child_default{}.png'.format(index) for index in range(1, 12))
  #  form_class = ChildModelForm
    model = Child

    def get(self, request, *args, **kwargs):
        child = Child.objects.get(id=kwargs['pk']) ##getは1件⇒1レコード、filterは複数⇒query set
        form = ChildModelForm(initial={'name': child.name, 'photo': child.photo})
        return render(request, self.template_name, {
            'form': form,
            'data': child,
            'default_child_photo': random.choice(self.default_child_photos),
        })


class HomeListView(ListView):
    model = Balance
    template_name = 'home.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model.objects.none()

        if self.request.user.puser:
            return self.model.objects.filter(cuser__puser=self.request.user.puser)
        else:
            return self.model.objects.filter(cuser=self.request.user.cuser)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if not self.request.user.is_authenticated:
            return context
        if not self.request.user.puser_id:
            return context

        balances = list(context['object_list'])
        pending_counts = Request.objects.filter(
            cuser__puser=self.request.user.puser,
            status=1,
        ).values('cuser_id').annotate(count=Count('id'))
        pending_count_map = {
            item['cuser_id']: item['count']
            for item in pending_counts
        }

        for balance in balances:
            balance.pending_request_count = pending_count_map.get(balance.cuser_id, 0)

        context['object_list'] = balances
        return context


class ApproveTaskView(LoginRequiredMixin, View):

    def get_child(self, child_id):
        child = get_object_or_404(Child, id=child_id)

        if self.request.user.puser_id and child.puser_id == self.request.user.puser_id:
            return child

        raise PermissionDenied

    def get_posted_request_ids(self, request):
        posted_values = request.POST.getlist('approve_request_group') or request.POST.getlist('approve_task_list')
        posted_request_ids = set()
        try:
            for posted_value in posted_values:
                for request_id in posted_value.split(','):
                    if request_id:
                        posted_request_ids.add(int(request_id))
        except ValueError:
            raise PermissionDenied
        return posted_request_ids

    def get_owned_requests(self, request_id_list):
        if not self.request.user.puser_id:
            raise PermissionDenied

        try:
            posted_request_ids = set(request_id_list)
        except ValueError:
            raise PermissionDenied

        if not posted_request_ids:
            raise PermissionDenied

        apply_requests = list(Request.objects.select_related('task', 'cuser').filter(
            id__in=posted_request_ids,
            puser=self.request.user.puser,
            status=1,
        ))

        if {apply_request.id for apply_request in apply_requests} != posted_request_ids:
            raise PermissionDenied

        return apply_requests

    @transaction.atomic
    def task_data_save(self, apply_requests):

        for applyRequests in apply_requests:
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
        approve_child_id = request.POST.get('approve_child_id', None)
        child = self.get_child(approve_child_id)
        request_id_list = self.get_posted_request_ids(request)
        if not request_id_list:
            return render(request, 'children/child_status.html', build_child_status_context(
                child,
                '承認するおてつだいを選んでください。',
            ))
        apply_requests = self.get_owned_requests(request_id_list)
        self.task_data_save(apply_requests)

        return redirect(reverse('children'))


class ApproveTaskDeleteView(LoginRequiredMixin, View):

    def get_child(self, child_id):
        child = get_object_or_404(Child, id=child_id)

        if self.request.user.puser_id and child.puser_id == self.request.user.puser_id:
            return child

        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        delete_values = request.POST.getlist('approve_request_group') or request.POST.getlist('approve_task_list')
        approve_child_id = request.POST.get('approve_child_id', None)
        child = self.get_child(approve_child_id)

        try:
            posted_request_ids = set()
            for posted_value in delete_values:
                for request_id in posted_value.split(','):
                    if request_id:
                        posted_request_ids.add(int(request_id))
        except ValueError:
            raise PermissionDenied

        if not posted_request_ids:
            return render(request, 'children/child_status.html', build_child_status_context(
                child,
                '却下するおてつだいを選んでください。',
            ))

        apply_requests = Request.objects.filter(
            id__in=posted_request_ids,
            cuser=child,
            puser=self.request.user.puser,
            status=1,
        )

        if set(apply_requests.values_list('id', flat=True)) != posted_request_ids:
            raise PermissionDenied

        apply_requests.delete() #複数の場合は__in=

        return redirect(reverse_lazy('child_status', args=[child.id])) #reverseに動的なパラメータを渡す

