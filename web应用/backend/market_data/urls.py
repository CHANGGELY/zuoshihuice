"""
市场数据路由配置
"""
from django.urls import path
from . import views

app_name = 'market_data'

urlpatterns = [
    # K线数据
    path('klines/', views.KlineDataView.as_view(), name='klines'),
    
    # 市场统计
    path('stats/', views.MarketStatsView.as_view(), name='stats'),
    
    # 时间周期
    path('timeframes/', views.TimeframesView.as_view(), name='timeframes'),
    
    # 交易对
    path('symbols/', views.SymbolsView.as_view(), name='symbols'),
]
