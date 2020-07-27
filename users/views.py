from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from users.forms import ChildModelForm
from users.models import Child, History


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
        if not form.is_valid():
            return render(request, 'children/children_regist.html', {'form': form})

        child = form.save(commit=False)
        child.submitter = self.request.user
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


