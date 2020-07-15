from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [

    path('', TemplateView.as_view(template_name='task/tasks.html'), name='tasks'),
    path('regist/', TemplateView.as_view(template_name='task/task_regist.html'), name='task_regist'),
    path('change/', TemplateView.as_view(template_name='task/task_change.html'), name='task_change'),

]