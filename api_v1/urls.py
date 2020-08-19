from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from api_v1.views import MonthlySummaryApiView, MonthlyChildSummaryApiView, TaskCreateApiView, TaskDeleteApiView, \
    TaskUpdateApiView, TaskDetailApiView, TicketCreateApiView, TicketUpdateApiView, TicketDetailApiView, \
    TicketDeleteApiView, RequestGetApiView, HistoryGetApiView, TicketHoldingGetApiView, ChildBalanceGetApiView, \
    ChildCreateApiView

schema_view = get_swagger_view(title='api_list')


urlpatterns = [

    path('monthly_summary/', MonthlySummaryApiView.as_view()), ##エンドポイントとはurl
    path('monthly_child_summary/', MonthlyChildSummaryApiView.as_view()),
    path('task/', TaskCreateApiView.as_view()),
    path('task_delete/<int:pk>/', TaskDeleteApiView.as_view()),
    path('task_update/<int:pk>/', TaskUpdateApiView.as_view()),
    path('task_detail/<int:pk>/', TaskDetailApiView.as_view()),
    path('ticket/', TicketCreateApiView.as_view()),
    path('ticket_update/<int:pk>/', TicketUpdateApiView.as_view()),
    path('ticket_detail/<int:pk>/', TicketDetailApiView.as_view()),
    path('ticket_delete/<int:pk>/', TicketDeleteApiView.as_view()),
    path('child_balance/<int:child_id>/', ChildBalanceGetApiView.as_view()),
    path('request/<int:child_id>/', RequestGetApiView.as_view()),
    path('history/<int:child_id>/', HistoryGetApiView.as_view()),
    path('ticket_holding/<int:child_id>/', TicketHoldingGetApiView.as_view()),
    path('child/', ChildCreateApiView.as_view()),
    url(r'^swagger/', schema_view),

]