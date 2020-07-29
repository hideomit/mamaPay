from django.views.generic import TemplateView
from django.urls import path

from accounts.views import ChildStatusGetView
from users.views import ChildListView, ChildRegistView, ChildDetailView, ChildInputView, ChildUpdateView

urlpatterns = [

    path('children/', ChildListView.as_view(), name='children'),
    path('children/regist/', ChildInputView.as_view(), name='children_regist'),
#    path('children/status/<int:pk>', ChildDetailView.as_view(), name='child_status'),
    path('children/status/<int:pk>', ChildStatusGetView.as_view(), name='child_status'),
 #   path('update/<int:pk>', ChildUpdateView.as_view(), name='child_update'),
    path('children/history/', TemplateView.as_view(template_name='children/child_history.html'), name='children_history'),
]
