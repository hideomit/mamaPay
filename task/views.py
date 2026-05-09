from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, DeleteView, UpdateView, DetailView

from .forms import TaskForm, Task2Form
from .models import Task


TASK_TEMPLATE_GROUPS = {
    'preschool': {
        'label': '幼児テンプレート',
        'description': '身の回りのことを楽しく習慣にするおてつだいです。',
        'items': [
            {'task_name': 'おもちゃをかたづける', 'price': 10},
            {'task_name': 'はみがきをする', 'price': 10},
            {'task_name': 'パジャマにきがえる', 'price': 10},
            {'task_name': 'くつをそろえる', 'price': 10},
            {'task_name': 'ごはんをさいごまでたべる', 'price': 15},
        ],
    },
    'elementary': {
        'label': '小学生テンプレート',
        'description': '学校生活と家庭のお手伝いをバランスよく入れたおてつだいです。',
        'items': [
            {'task_name': '宿題をする', 'price': 30},
            {'task_name': '明日の準備をする', 'price': 20},
            {'task_name': 'ランドセルを片づける', 'price': 10},
            {'task_name': 'おふろそうじをする', 'price': 40},
            {'task_name': '洗濯物をたたむ', 'price': 30},
        ],
    },
    'junior_high': {
        'label': '中学生テンプレート',
        'description': '学習や生活管理を自分で進めるためのおてつだいです。',
        'items': [
            {'task_name': '英単語を10個覚える', 'price': 40},
            {'task_name': '30分勉強する', 'price': 50},
            {'task_name': '部屋を片づける', 'price': 30},
            {'task_name': '翌日の予定を確認する', 'price': 20},
            {'task_name': '洗い物をする', 'price': 40},
        ],
    },
}


# Create your views here.
##LoginRequiredMixin 継承しておくと未ログイン時にホームに遷移
##pagenate_by: pagenation 10まで表示
##事由につくりたいときはget_query_set　というメソッドをつくる
##templateview使い勝手のいいメソッドがそろっている

class TaskListView(LoginRequiredMixin, ListView):
#    model = Task ##ここのテーブルのデータがくる　object_listという名前
    template_name = 'task/tasks.html'
#    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.all()
        if hasattr(self.request.user, 'puser') and self.request.user.puser:
            queryset = queryset.filter(puser=self.request.user.puser)
        return queryset

"""
class TaskInputView(LoginRequiredMixin, TemplateView):
    template_name = 'task/task_regist.html'

    def get_context_data(self, **kwargs): #contextはHTMLに渡すデータ #super 親クラスのmethodを使うとき
        context = super().get_context_data()
        context.update({'form': TaskForm()}) ##TaskModelFormだとうまくいかない？
        return context
"""
"""
class TaskCreateView(LoginRequiredMixin, View):
    template_name = 'task/task_regist.html'

    def post(self, request):
        form = TaskForm(request.POST)
        form.
"""


class TaskRegistView(LoginRequiredMixin, CreateView):
    template_name = 'task/task_regist.html'

    model = Task
    form_class = Task2Form
    success_url = reverse_lazy('tasks') ##reverse_lazy　name=に逆びきする。アプリ名左側

    def form_valid(self, form):
        form.instance.puser = self.request.user.puser
        return super().form_valid(form)


class TaskTemplateView(LoginRequiredMixin, View):
    template_name = 'task/task_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'template_groups': TASK_TEMPLATE_GROUPS})

    def post(self, request, *args, **kwargs):
        if not request.user.puser_id:
            raise PermissionDenied

        template_key = request.POST.get('template_key')
        template_group = TASK_TEMPLATE_GROUPS.get(template_key)
        if not template_group:
            raise PermissionDenied

        existing_names = set(Task.objects.filter(
            puser=request.user.puser,
            task_name__in=[item['task_name'] for item in template_group['items']],
        ).values_list('task_name', flat=True))

        created_count = 0
        skipped_count = 0
        for item in template_group['items']:
            if item['task_name'] in existing_names:
                skipped_count += 1
                continue
            Task.objects.create(
                puser=request.user.puser,
                task_name=item['task_name'],
                price=item['price'],
            )
            created_count += 1

        return render(request, self.template_name, {
            'template_groups': TASK_TEMPLATE_GROUPS,
            'selected_template': template_group,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'back_url': reverse('tasks'),
        })


class TaskDeleteView(LoginRequiredMixin, View):##deleteviewはtemplatenameいらない

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('delete_list') #単品はrequest.POST.get 複数はrequest.POST.getlist
        Task.objects.filter(id__in=delete_list, puser=self.request.user.puser).delete() #複数の場合は__in=
        return redirect(reverse_lazy('tasks'))


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = Task2Form
    success_url = reverse_lazy('tasks') ##reverse_lazy 逆引き用の関数

    def get_queryset(self):
        return Task.objects.filter(puser=self.request.user.puser)


class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'task/task_change.html'
    model = Task

    def get_queryset(self):
        return Task.objects.filter(puser=self.request.user.puser)
