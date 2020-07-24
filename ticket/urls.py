from django.views.generic import TemplateView
from django.urls import path

from ticket.views import TicketListView, TicketRegistView, TicketDetailView, TicketUpdateView

urlpatterns = [

    path('', TicketListView.as_view(), name='ticket'),
    path('regist/', TicketRegistView.as_view(), name='ticket_regist'),
    path('update/<int:pk>', TicketUpdateView.as_view(), name='ticket_update'),
    path('detail/<int:pk>', TicketDetailView.as_view(), name='ticket_detail'),

]
