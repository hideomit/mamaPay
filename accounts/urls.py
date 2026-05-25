from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignupParentView.as_view(), name='signup'),
    path('signup/done/', views.SignupActivationSentView.as_view(), name='signup_activation_sent'),
    path('activate/<uidb64>/<token>/', views.AccountActivateView.as_view(), name='activate'),
    path('activate/done/', views.AccountActivateDoneView.as_view(), name='activate_done'),
    path('activate/invalid/', views.AccountActivateInvalidView.as_view(), name='activate_invalid'),

]
