from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('deposit/', views.deposit, name='deposit'),
    path('balance/', views.account_balance, name='balance'),
    path('reset-account/', views.reset_account, name='reset_account'),
]