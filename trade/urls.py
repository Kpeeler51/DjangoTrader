from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('buy/', views.buy_stock, name='buy_stock'),
    path('sell/', views.sell_stock, name='sell_stock'),
    path('portfolio/', views.portfolio, name='portfolio'),
]