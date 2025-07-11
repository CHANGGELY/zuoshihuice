"""
API路由配置
"""
from django.urls import path
from . import views, auth_views

app_name = 'api'

urlpatterns = [
    # 系统状态
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('status/', views.SystemStatusView.as_view(), name='status'),

    # 基础信息
    path('info/', views.SystemInfoView.as_view(), name='info'),

    # 用户认证
    path('auth/register/', auth_views.RegisterView.as_view(), name='register'),
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', auth_views.UserProfileView.as_view(), name='profile'),
]
