"""
市场数据路由配置
"""
from django.urls import path
from . import views

app_name = 'market_data'

urlpatterns = [
    # K线数据
    path('klines/', views.KlineDataView.as_view(), name='klines'),

    # 本地K线数据（从H5文件）
    path('local-klines/', views.LocalKlineDataView.as_view(), name='local_klines'),

    # 数据范围
    path('data-range/', views.DataRangeView.as_view(), name='data_range'),

    # 最新价格
    path('latest-price/', views.LatestPriceView.as_view(), name='latest_price'),

    # 回测
    path('backtest/', views.BacktestView.as_view(), name='backtest'),

    # 市场统计
    path('stats/', views.MarketStatsView.as_view(), name='stats'),

    # 时间周期
    path('timeframes/', views.TimeframesView.as_view(), name='timeframes'),

    # 交易对
    path('symbols/', views.SymbolsView.as_view(), name='symbols'),
]
