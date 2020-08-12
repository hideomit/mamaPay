from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, DeleteView, UpdateView, DetailView

from .forms import TaskForm, Task2Form
from .models import Task


# Create your views here.
##LoginRequiredMixin 継承しておくと未ログイン時にホームに遷移
##pagenate_by: pagenation 10まで表示
##事由につくりたいときはget_query_set　というメソッドをつくる
##templateview使い勝手のいいメソッドがそろっている

class TaskListView(LoginRequiredMixin, ListView):
#    model = Task ##ここのテーブルのデータがくる　object_listという名前
    template_name = 'task/tasks.html'
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.all()

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


class TaskDeleteView(LoginRequiredMixin, View):##deleteviewはtemplatenameいらない

    def post(self, request, *args, **kwargs):
        delete_list = request.POST.getlist('delete_list') #単品はrequest.POST.get 複数はrequest.POST.getlist
        Task.objects.filter(id__in=delete_list).delete() #複数の場合は__in=
        return redirect(reverse_lazy('tasks'))


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = Task2Form
    success_url = reverse_lazy('tasks') ##reverse_lazy 逆引き用の関数


class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'task/task_change.html'
    model = Task
