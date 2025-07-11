"""
回测路由配置
"""
from django.urls import path
from . import views

app_name = 'backtest'

urlpatterns = [
    # 运行回测
    path('run/', views.BacktestRunView.as_view(), name='run'),
    
    # 回测结果
    path('results/', views.BacktestResultView.as_view(), name='results'),
    path('results/<int:result_id>/', views.BacktestResultView.as_view(), name='result_detail'),
    
    # 回测状态
    path('status/<int:result_id>/', views.BacktestStatusView.as_view(), name='status'),
    
    # 回测配置
    path('configs/', views.BacktestConfigView.as_view(), name='configs'),
]
