from django.views.generic import TemplateView
from django.urls import path

from accounts.views import ChildStatusGetView, ApproveTaskView, ApproveTaskDeleteView
from users.views import ChildListView, ChildInputView, ChildUpdateView, ChildHomeView, ChildApplyView, TaskApplyView, TaskApplyCompView, ChildHistoryView, ChildDeleteView

urlpatterns = [

    path('children/', ChildListView.as_view(), name='children'),
    path('children/regist/', ChildInputView.as_view(), name='children_regist'),
    path('children/regist/<int:pk>', ChildInputView.as_view(), name='children_regist'),
    #    path('children/status/<int:pk>', ChildDetailView.as_view(), name='child_status'),
    path('children/status/<int:pk>', ChildStatusGetView.as_view(), name='child_status'),
    path('children/status/child_approve', ApproveTaskView.as_view(), name='child_approve'),
    path('children/status/child_approve_delete', ApproveTaskDeleteView.as_view(), name='child_approve_delete'),
    path('children/update/<int:pk>', ChildUpdateView.as_view(), name='child_update'),
    path('children/history/<int:pk>', ChildHistoryView.as_view(), name='children_history'),
    path('child/home/<int:pk>', ChildHomeView.as_view(), name='child_home'),
    path('child/home/apply_task/<int:pk>', ChildApplyView.as_view(), name='apply_task'),
    path('child/home/apply_task/task_apply_update', TaskApplyView.as_view(), name='task_apply_update'),
    path('child/home/apply_complete', TaskApplyCompView.as_view(), name='apply_task_complete'),
]
