from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from users.forms import ChildForm
from users.models import Child


class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'children/children.html'
    pagenate_by = 10


##3宿題

class ChildRegistView(LoginRequiredMixin, CreateView):
    template_name = "children/children_regist.html"
    model = Child
    form_class = ChildForm
    success_url = reverse_lazy('children')
