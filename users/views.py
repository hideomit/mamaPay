from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from task.models import Task
from users.forms import ChildModelForm
from users.models import Child, History, Balance, Request


class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'children/children.html'
    pagenate_by = 10


##3宿題

class ChildRegistView(LoginRequiredMixin, CreateView):
    template_name = "children/children_regist.html"
    model = Child
    form_class = ChildModelForm
    success_url = reverse_lazy('children')

    ##外部キーを入れるのはこれでよいのか？　https://qiita.com/godan09/items/97ea3a6397bf619b6517
    def form_valid(self, form):
        form.instance.puser_id = self.request.user.id
        return super(ChildRegistView, self).form_valid(form)


class ChildInputView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {'form': ChildModelForm()}
        return render(request, 'children/children_regist.html', context)

    ##postだけだと405エラーがでてしまった。必ずgetとpostは両方かかなければならない制約でもある？

    def post(self, request, *args, **kwargs):
        form = ChildModelForm(request.POST, request.FILES)
        if not form.is_valid():  ##is_validはフォームに入った値にエラーがないかバリデートするメソッド。バリデートがエラーになった場合にエラーを返す
            return render(request, 'children/children_regist.html', {'form': form})

        child = form.save(commit=False)
        child.puser = self.request.user  ##request.userはログインユーザー
        child.save()

        return redirect(reverse('children'))


class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildModelForm
    success_url = reverse_lazy('children')


class ChildDetailView(LoginRequiredMixin, DetailView):
    template_name = 'children/child_status.html'
    model = Child


class ChildHistoryView(LoginRequiredMixin, ListView):
    model = History
    template_name = 'children/child_history.html'
    pagenate_by = 10

    def get_queryset(self):
        child_id = self.kwargs['pk']
        return self.model.objects.filter(cuser_id=child_id)


class ChildHomeView(LoginRequiredMixin, View):
    def get(self, request, pk):
        child_data = Child.objects.filter(id=pk)

        if Balance.objects.filter(cuser_id=pk).exists():  ##exists()はfilterのmethod? getだと動かなかった
            balance_data = Balance.objects.get(cuser_id=pk)
            print(balance_data.balance)
        else:
            balance_data = None

        return render(request, 'children/child_home.html', {'child_data': child_data, 'balance_data': balance_data})


class ChildApplyView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'children/apply_task.html'
    pagenate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
#        pprint(self.kwargs)
        context['child_data'] = Child.objects.get(id=self.kwargs['pk'])
        return context


class TaskApplyView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        apply_task_id = request.POST.get('apply_task', None)
        apply_child_id = request.POST.get('apply_child_id', None)
        print(apply_task_id)
        print(apply_child_id)
        childRequest = Request(cuser_id=apply_child_id, task_id=apply_task_id, status=1)
        childRequest.puser = self.request.user
        childRequest.save()

        return redirect('apply_task_complete', apply_child_id, apply_task_id)


class TaskApplyCompView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        child_data = Child.objects.get(id=self.kwargs['cpk'])
        task_data = Task.objects.get(id=self.kwargs['tpk'])

        return render(request, 'children/apply_complete.html', {'child_data':child_data, 'task_data':task_data})