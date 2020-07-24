from django.views.generic import TemplateView
from django.urls import path

from task.views import TaskListView, TaskRegistView, TaskDeleteView, TaskUpdateView, TaskDetailView

# TaskInputView,

urlpatterns = [

    path('', TaskListView.as_view(), name='tasks'),
    path('regist/', TaskRegistView.as_view(), name='task_regist'),
    path('delete/<int:pk>', TaskDeleteView.as_view(), name='task_delete'), ##DeleteViewはインスタンスいらない。単体消す用。
    path('update/<int:pk>', TaskUpdateView.as_view(), name='task_update'),
    path('detail/<int:pk>', TaskDetailView.as_view(), name='task_detail'),

]