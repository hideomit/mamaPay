import random
from pprint import pprint

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from accounts.forms import SignupChildForm
from accounts.models import LoginUsers
from task.models import Task
from users.forms import ChildModelForm
from users.models import Child, History, Balance, Request


class ChildListView(LoginRequiredMixin, ListView):
    model = Balance
    template_name = 'children/children.html'

    def get_queryset(self):
       return self.model.objects.filter(cuser__puser=self.request.user.puser)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
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


##3宿題

class ChildRegistView(LoginRequiredMixin, CreateView):
    template_name = "children/children_regist.html"
    model = Child
    form_class = ChildModelForm
    success_url = reverse_lazy('status')

    ##外部キーを入れるのはこれでよいのか？　https://qiita.com/godan09/items/97ea3a6397bf619b6517
    def form_valid(self, form):
        form.instance.puser_id = self.request.user.id
        return super(ChildRegistView, self).form_valid(form)


class ChildUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "children/children_regist.html"
    model = Child
    form_class = ChildModelForm
    success_url = reverse_lazy('status')

    def form_valid(self, form):
        form.instance.puser_id = self.request.user.id
        return super(ChildUpdateView, self).form_valid(form)


class ChildInputView(LoginRequiredMixin, View):
    default_child_photos = tuple('child_default{}.png'.format(index) for index in range(1, 12))

    def get_default_child_photo(self, request):
        default_photo = request.POST.get('default_child_photo')
        if default_photo in self.default_child_photos:
            return default_photo
        return random.choice(self.default_child_photos)

    def add_default_photo(self, child, default_photo):
        default_photo_path = finders.find(default_photo)
        if not default_photo_path:
            return

        with open(default_photo_path, 'rb') as photo_file:
            child.photo.save(default_photo, File(photo_file), save=False)

    def get(self, request, *args, **kwargs):
        context = {
            'c_form': ChildModelForm(),
            's_form': SignupChildForm(),
            'default_child_photo': self.get_default_child_photo(request),
        }
        return render(request, 'children/children_regist.html', context)

    ##postだけだと405エラーがでてしまった。必ずgetとpostは両方かかなければならない制約でもある？

    def post(self, request, *args, **kwargs):
        c_form = ChildModelForm(request.POST, request.FILES)
        s_form = SignupChildForm(request.POST)
        default_child_photo = self.get_default_child_photo(request)

        if self.kwargs.get('pk') is not None:  # 更新動作
            if not c_form.is_valid():  ##is_validはフォームに入った値にエラーがないかバリデートするメソッド。バリデートがエラーになった場合にエラーを返す
                context = {'c_form': c_form}
                return render(request, 'children/children_regist.html', context)
        else:
            if not c_form.is_valid() or not s_form.is_valid():  ##is_validはフォームに入った値にエラーがないかバリデートするメソッド。バリデートがエラーになった場合にエラーを返す
                context = {'c_form': c_form, 's_form': s_form, 'default_child_photo': default_child_photo}
                return render(request, 'children/children_regist.html', context)

        child = c_form.save(commit=False)
        child.puser = self.request.user.puser  ##request.userはログインユーザー
        use_default_child_photo = request.POST.get('use_default_child_photo') == '1'

        if self.kwargs.get('pk') is not None: #更新動作
            child.id = self.kwargs.get('pk')
            child_data = Child.objects.get(pk=child.id)
            # child.create_datetime = form.cleaned_data['create_datetime']##create_datetimeエラー回避
            child.create_datetime = child_data.create_datetime
            if use_default_child_photo and not request.FILES.get('photo'):
                self.add_default_photo(child, default_child_photo)
            elif not request.FILES.get('photo'):
                child.photo = child_data.photo
            #
           ##saveはidがないとcreateになる。idがあれば更新になる

        if self.kwargs.get('pk') is None and not request.FILES.get('photo'):
            self.add_default_photo(child, default_child_photo)

        child.save()  ##childはmodelではなくForm。これでDB登録してる？<< fome.saveで一度インスタンスに保存している

        if self.kwargs.get('pk') is None: #新規のみ
            balance = Balance(cuser_id=child.id, balance=0)
            balance.save()

            login_user = s_form.save(commit=False)
            login_user.cuser = child
            login_user.save()

        return redirect(reverse('status'))




class ChildDetailView(LoginRequiredMixin, DetailView):
    template_name = 'children/child_status.html'
    model = Child


class ChildHistoryView(LoginRequiredMixin, ListView):
    model = History
    template_name = 'children/child_history.html'
    pagenate_by = 10

    def get_queryset(self):
        child_id = self.kwargs['pk']
        return self.model.objects.filter(cuser_id=child_id).order_by('-ymd')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs['pk']
        context['child_data'] = Child.objects.get(id=child_id)
        return context


class ChildHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        child_data = Child.objects.get(id=self.kwargs['pk'])

        print(child_data.id)

        if Balance.objects.filter(cuser_id=child_data.id).exists():  ##exists()はfilterのmethod? getだと動かなかった
            balance_data = Balance.objects.get(cuser_id=child_data.id)
            print(balance_data.balance)
        else:
            balance_data = None

        top_task = History.objects.filter(cuser_id=kwargs['pk'], kind=1).values('task_id', 'cuser_id',
                                                                        'task__task_name').annotate(
            count=Count('task_id')).order_by('-count').first()

        top_ticket = History.objects.filter(cuser_id=kwargs['pk'], kind=3).values('ticket_id', 'cuser_id',
                                                                        'ticket__ticket_name').annotate(
            count=Count('ticket_id')).order_by('-count').first()

        return render(request, 'children/child_home.html', {'child_data': child_data, 'balance_data': balance_data, 'top_task': top_task, 'top_ticket': top_ticket})


class ChildApplyView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'children/apply_task.html'
    pagenate_by = 10

    def get_child(self):
        child = get_object_or_404(Child, id=self.kwargs['pk'])
        user = self.request.user

        if user.puser_id and child.puser_id == user.puser_id:
            return child
        if user.cuser_id and child.id == user.cuser_id:
            return child

        raise PermissionDenied

    def get_queryset(self):
        child = self.get_child()
        return Task.objects.filter(puser=child.puser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
#        pprint(self.kwargs)
        child = self.get_child()
        context['child_data'] = child
        context['balance_data'] = Balance.objects.select_related('cuser').get(cuser=child)
        return context


class TaskApplyView(LoginRequiredMixin, View):

    def send_apply_notification(self, request, child, applied_tasks):
        if not applied_tasks:
            return

        parent_user = LoginUsers.objects.filter(puser=child.puser).first()
        if not parent_user or not parent_user.email:
            return

        approval_url = request.build_absolute_uri(reverse('child_status', args=[child.id]))
        task_lines = '\n'.join(
            ['・{}（{}コイン）'.format(task.task_name, task.price) for task in applied_tasks]
        )
        total_coin = sum(task.price for task in applied_tasks)

        message = (
            '{child_name}さんからおてつだい完了申請が届きました。\n\n'
            'おてつだい名:\n{task_lines}\n\n'
            '獲得予定コイン: {total_coin}コイン\n\n'
            '承認リンク:\n{approval_url}\n'
        ).format(
            child_name=child.name,
            task_lines=task_lines,
            total_coin=total_coin,
            approval_url=approval_url,
        )

        send_mail(
            subject='【いえペイ】{}さんがおてつだい完了申請'.format(child.name),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_user.email],
        )

    def post(self, request, *args, **kwargs):
        apply_task_list = request.POST.getlist('apply_task_list')
        apply_child_id = request.POST.get('apply_child_id', None)
        child = get_object_or_404(Child, id=apply_child_id)
        user = self.request.user

        if user.puser_id and child.puser_id == user.puser_id:
            pass
        elif user.cuser_id and child.id == user.cuser_id:
            pass
        else:
            raise PermissionDenied

        try:
            posted_task_ids = {int(task_id) for task_id in apply_task_list}
        except ValueError:
            raise PermissionDenied

        applied_tasks = list(Task.objects.filter(
            id__in=posted_task_ids,
            puser=child.puser,
        ))
        valid_task_ids = {task.id for task in applied_tasks}

        if valid_task_ids != posted_task_ids:
            raise PermissionDenied

        for apply_task in apply_task_list:
            ##申請リストの更新
            childRequest = Request(cuser=child, task_id=apply_task, status=1, puser=child.puser)
            childRequest.save()

        self.send_apply_notification(request, child, applied_tasks)

        request_list = Request.objects.select_related('task').filter(cuser=child, status=1)
        child_data = child
        balance_data = Balance.objects.select_related('cuser').get(cuser=child)

        return render(request, 'children/apply_complete.html',
                      {'child_data': child_data, 'request_list': request_list, 'balance_data': balance_data})


class TaskApplyCompView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        child_data = Child.objects.get(id=self.kwargs['cpk'])
        task_data = Task.objects.get(id=self.kwargs['tpk'])

        return render(request, 'children/apply_complete.html', {'child_data': child_data, 'task_data': task_data})


class ChildDeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('delete_list')
        Child.objects.filter(id__in=delete_list).delete()

        return redirect(reverse_lazy('status'))
