"""
API视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
import os
from datetime import datetime


class HealthCheckView(APIView):
    """健康检查接口"""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })


class SystemStatusView(APIView):
    """系统状态接口"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            return Response({
                'status': 'ok',
                'system': {
                    'cpu_usage': 'N/A',
                    'memory_usage': 'N/A',
                    'memory_available': 'N/A',
                    'disk_usage': 'N/A',
                    'disk_free': 'N/A'
                },
                'services': {
                    'django': True,
                    'database': True,
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemInfoView(APIView):
    """系统信息接口"""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'platform': {
                'name': '永续合约做市策略回测平台',
                'version': '1.0.0',
                'description': '基于Django + Vue.js的专业交易策略回测平台',
                'features': [
                    '实时K线图表显示',
                    '多时间周期支持',
                    '交易信号可视化',
                    '策略参数调优',
                    '回测结果分析',
                    '风险指标计算'
                ]
            },
            'supported_symbols': ['ETH/USDC', 'BTC/USDT'],
            'timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
            'data_range': {
                'start': '2019-11-01',
                'end': '2025-06-15'
            },
            'timestamp': datetime.now().isoformat()
        })
