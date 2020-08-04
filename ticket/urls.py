from django.views.generic import TemplateView
from django.urls import path

from ticket.views import TicketListView, TicketRegistView, TicketDetailView, TicketUpdateView, TicketDeleteView, \
    TicketBuyView, ChildTicketShopView

urlpatterns = [

    path('', TicketListView.as_view(), name='ticket'),
    path('regist/', TicketRegistView.as_view(), name='ticket_regist'),
    path('update/<int:pk>', TicketUpdateView.as_view(), name='ticket_update'),
    path('detail/<int:pk>', TicketDetailView.as_view(), name='ticket_detail'),
    path('delete/', TicketDeleteView.as_view(), name='selected_ticket_delete'),
    path('ticket_shop/<int:pk>', ChildTicketShopView.as_view(), name='ticket_shop'),
    path('buy/', TicketBuyView.as_view(), name='selected_ticket_buy'),

]
