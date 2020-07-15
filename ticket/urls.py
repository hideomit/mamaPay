from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [

    path('', TemplateView.as_view(template_name='ticket/ticket.html'), name='ticket'),
    path('regist', TemplateView.as_view(template_name='ticket/ticket_regist.html'), name='ticket_regist'),
    path('change/', TemplateView.as_view(template_name='ticket/ticket_change.html'), name='ticket_change'),

]