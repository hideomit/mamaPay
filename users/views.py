import random
from pprint import pprint
from datetime import timedelta
from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

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
    chart_colors = (
        '#7cc08a',
        '#69aee7',
        '#f2b86b',
        '#d884a8',
        '#8f8bd6',
        '#6fc7c0',
    )

    def get_monthly_summary(self, child_id):
        today = timezone.now()
        if timezone.is_aware(today):
            today = timezone.localtime(today)
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        month_end = next_month - timedelta(days=1)

        monthly_history = History.objects.filter(
            cuser_id=child_id,
            ymd__gte=month_start,
            ymd__lt=next_month,
        )
        monthly_income = monthly_history.filter(kind=1).aggregate(total=Sum('amount'))['total'] or 0
        monthly_expense = monthly_history.filter(kind=2).aggregate(total=Sum('amount'))['total'] or 0
        monthly_balance = monthly_income + monthly_expense

        income_items = list(monthly_history.filter(kind=1).values('task_name').annotate(
            total=Sum('amount'),
        ).order_by('-total'))

        chart_segments = []
        income_breakdown = []
        cursor = 0
        for index, item in enumerate(income_items):
            amount = item['total'] or 0
            if amount <= 0 or monthly_income <= 0:
                continue

            color = self.chart_colors[index % len(self.chart_colors)]
            start = cursor
            percent = amount / monthly_income * 100
            cursor += percent
            chart_segments.append({
                'name': item['task_name'] or 'おてつだい',
                'amount': amount,
                'color': color,
                'percent': '{:.4f}'.format(percent),
                'rest': '{:.4f}'.format(100 - percent),
                'offset': '{:.4f}'.format(-start),
            })
            income_breakdown.append({
                'name': item['task_name'] or 'おてつだい',
                'amount': amount,
                'color': color,
            })

        if chart_segments:
            chart_title = '\n'.join(
                '{}: {}コイン'.format(item['name'], item['amount'])
                for item in income_breakdown
            )
        else:
            chart_title = '今月のおてつだいはまだありません'

        return {
            'monthly_period_label': '{}月1日〜{}月{}日'.format(
                month_start.month,
                month_end.month,
                month_end.day,
            ),
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_balance': monthly_balance,
            'monthly_income_breakdown': income_breakdown[:3],
            'monthly_chart_segments': chart_segments,
            'monthly_chart_title': chart_title,
        }

    def get_recent_status_messages(self, child):
        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        this_week_start = now - timedelta(days=now.weekday())
        this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_week_start = this_week_start - timedelta(days=7)
        today = now.date()
        three_days_ago = (now - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        this_week_counts = list(History.objects.filter(
            cuser__puser=child.puser,
            kind=1,
            ymd__gte=this_week_start,
            ymd__lt=now,
        ).values(
            'cuser_id',
            'cuser__name',
        ).annotate(
            count=Count('id'),
        ).order_by('-count'))

        this_week_task_histories = list(History.objects.filter(
            cuser__puser=child.puser,
            kind=1,
            ymd__gte=this_week_start,
            ymd__lt=now,
            task_id__isnull=False,
        ).values(
            'cuser_id',
            'cuser__name',
            'task_id',
            'task_name',
            'task__task_name',
        ).order_by('ymd'))

        messages = []

        if this_week_counts:
            top_child = this_week_counts[0]
            messages.append(
                '今週のおてつだいチャンピオンは {}！{} 回もがんばったよ！'.format(
                    top_child['cuser__name'],
                    top_child['count'],
                )
            )

        last_week_counts = History.objects.filter(
            cuser__puser=child.puser,
            kind=1,
            ymd__gte=last_week_start,
            ymd__lt=this_week_start,
        ).values(
            'cuser_id',
        ).annotate(
            count=Count('id'),
        )
        last_week_count_map = {
            item['cuser_id']: item['count']
            for item in last_week_counts
        }

        best_growth = None
        for item in this_week_counts:
            diff = item['count'] - last_week_count_map.get(item['cuser_id'], 0)
            if diff <= 0:
                continue
            if best_growth is None or diff > best_growth['diff']:
                best_growth = {
                    'name': item['cuser__name'],
                    'diff': diff,
                }

        if best_growth:
            messages.append(
                '{} は先週より {} 回多くおてつだいしてるよ！'.format(
                    best_growth['name'],
                    best_growth['diff'],
                )
            )

        task_ids = [
            item['task_id']
            for item in this_week_task_histories
        ]
        past_task_pairs = set(History.objects.filter(
            cuser__puser=child.puser,
            kind=1,
            task_id__in=task_ids,
            ymd__lt=this_week_start,
        ).values_list(
            'cuser_id',
            'task_id',
        ))

        first_achievement = None
        for item in this_week_task_histories:
            task_pair = (item['cuser_id'], item['task_id'])
            if task_pair in past_task_pairs:
                continue
            first_achievement = item
            break

        if first_achievement:
            task_name = first_achievement['task_name'] or first_achievement['task__task_name'] or 'おてつだい'
            messages.append(
                '{} が今週はじめて「{}」を達成したよ！'.format(
                    first_achievement['cuser__name'],
                    task_name,
                )
            )

        streak_days = {
            today - timedelta(days=day)
            for day in range(3)
        }
        streak_histories = History.objects.filter(
            cuser__puser=child.puser,
            kind=1,
            ymd__gte=three_days_ago,
            ymd__lt=tomorrow,
        ).values(
            'cuser_id',
            'cuser__name',
            'ymd',
        )
        child_streak_days = {}
        child_names = {}
        for item in streak_histories:
            child_streak_days.setdefault(item['cuser_id'], set()).add(item['ymd'].date())
            child_names[item['cuser_id']] = item['cuser__name']

        streak_child_ids = [
            child_id
            for child_id, days in child_streak_days.items()
            if streak_days.issubset(days)
        ]
        if streak_child_ids:
            streak_child_id = random.choice(streak_child_ids)
            messages.append(
                '{} は3日連続でおてつだいしてるよ！'.format(
                    child_names[streak_child_id],
                )
            )

        total = sum(item['count'] for item in this_week_counts)
        if total > 0:
            messages.append(
                '今週はみんなで {} 回おてつだいしたよ！'.format(total)
            )

        if not messages:
            return ['今週のおてつだいはこれからだよ！']

        return random.sample(messages, min(2, len(messages)))

    def get(self, request, *args, **kwargs):
        child_data = Child.objects.get(id=self.kwargs['pk'])

        print(child_data.id)

        if Balance.objects.filter(cuser_id=child_data.id).exists():  ##exists()はfilterのmethod? getだと動かなかった
            balance_data = Balance.objects.get(cuser_id=child_data.id)
            print(balance_data.balance)
        else:
            balance_data = None

        context = {
            'child_data': child_data,
            'balance_data': balance_data,
            'recent_status_messages': self.get_recent_status_messages(child_data),
        }
        context.update(self.get_monthly_summary(child_data.id))

        return render(request, 'children/child_home.html', context)


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

    max_apply_quantity = 10

    def get_task_summary(self, requests):
        summary_map = OrderedDict()
        for request in requests:
            task_id = request.task_id
            if task_id not in summary_map:
                summary_map[task_id] = {
                    'task': request.task,
                    'count': 0,
                    'total_price': 0,
                }
            summary_map[task_id]['count'] += 1
            summary_map[task_id]['total_price'] += request.task.price
        return list(summary_map.values())

    def get_posted_task_quantities(self, request):
        task_quantities = {}
        for key, value in request.POST.items():
            if not key.startswith('task_quantity_'):
                continue

            try:
                task_id = int(key.replace('task_quantity_', '', 1))
                quantity = int(value)
            except ValueError:
                raise PermissionDenied

            if quantity < 0 or quantity > self.max_apply_quantity:
                raise PermissionDenied
            if quantity > 0:
                task_quantities[task_id] = quantity

        if not task_quantities:
            raise PermissionDenied

        return task_quantities

    def send_apply_notification(self, request, child, applied_tasks):
        if not applied_tasks:
            return

        parent_user = LoginUsers.objects.filter(puser=child.puser).first()
        if not parent_user or not parent_user.email:
            return

        approval_url = request.build_absolute_uri(reverse('child_status', args=[child.id]))
        task_summary = OrderedDict()
        for task in applied_tasks:
            if task.id not in task_summary:
                task_summary[task.id] = {'task': task, 'count': 0, 'total_price': 0}
            task_summary[task.id]['count'] += 1
            task_summary[task.id]['total_price'] += task.price

        task_lines = '\n'.join([
            '・{} × {}（{}コイン）'.format(
                item['task'].task_name,
                item['count'],
                item['total_price'],
            )
            for item in task_summary.values()
        ])
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
        apply_child_id = request.POST.get('apply_child_id', None)
        child = get_object_or_404(Child, id=apply_child_id)
        user = self.request.user

        if user.puser_id and child.puser_id == user.puser_id:
            pass
        elif user.cuser_id and child.id == user.cuser_id:
            pass
        else:
            raise PermissionDenied

        task_quantities = self.get_posted_task_quantities(request)
        posted_task_ids = set(task_quantities.keys())

        applied_tasks = list(Task.objects.filter(
            id__in=posted_task_ids,
            puser=child.puser,
        ))
        valid_task_ids = {task.id for task in applied_tasks}

        if valid_task_ids != posted_task_ids:
            raise PermissionDenied

        applied_task_instances = []
        task_map = {task.id: task for task in applied_tasks}
        for task_id, quantity in task_quantities.items():
            for _ in range(quantity):
                childRequest = Request(cuser=child, task_id=task_id, status=1, puser=child.puser)
                childRequest.save()
                applied_task_instances.append(task_map[task_id])

        self.send_apply_notification(request, child, applied_task_instances)

        request_list = Request.objects.select_related('task').filter(cuser=child, status=1)
        child_data = child
        balance_data = Balance.objects.select_related('cuser').get(cuser=child)
        request_summary_list = self.get_task_summary(request_list)

        return render(request, 'children/apply_complete.html',
                      {
                          'child_data': child_data,
                          'request_list': request_list,
                          'request_summary_list': request_summary_list,
                          'balance_data': balance_data,
                      })


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
