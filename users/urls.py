from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [

    path('children/', TemplateView.as_view(template_name='children/children.html'), name='children'),
    path('children/regist/', TemplateView.as_view(template_name='children/children_regist.html'), name='children_regist'),
    path('children/status/', TemplateView.as_view(template_name='children/child_status.html'), name='child_status'),
    path('children/history/', TemplateView.as_view(template_name='children/child_history.html'), name='children_history'),

]