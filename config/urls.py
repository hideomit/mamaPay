"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views

from accounts.views import ChildStatusListView, ChildStatusDetailView, ChildStatusUpdateView, HomeListView
from config import settings
from users.views import ChildDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('users/', include('users.urls')),
    path('tasks/', include('task.urls')),
    path('ticket/', include('ticket.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api_v1/', include('api_v1.urls')),
    path('', HomeListView.as_view(), name='home'),
    path('admin_home/', TemplateView.as_view(template_name='admin_home.html'), name='admin_home'),
    path('graphs/', TemplateView.as_view(template_name='graphs.html'), name='graphs'),
    path('switch/', TemplateView.as_view(template_name='switch.html'), name='switch'),
    path('status/', ChildStatusListView.as_view(), name='status'),
    path('status/change/<int:pk>/', ChildStatusDetailView.as_view(), name='status_change'),
    path('status/delete/', ChildDeleteView.as_view(), name='selected_child_delete'),
    path('status/update/<int:pk>/', ChildStatusUpdateView.as_view(), name='status_update'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/password_change/', views.PasswordChangeView.as_view(), name="password_change"),
    path('accounts/password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', views.PasswordResetCompleteView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


