"""
URL configuration for trading_platform project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('api/v1/market/', include('market_data.urls')),
    path('api/v1/backtest/', include('backtest.urls')),
]
