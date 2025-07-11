"""
市场数据视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .services import MarketDataService
from .serializers import KlineChartSerializer, TimeframeSerializer
from datetime import datetime, timedelta


class KlineDataView(APIView):
    """K线数据接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.market_service = MarketDataService()
    
    @method_decorator(cache_page(60))  # 缓存1分钟
    def get(self, request):
        """获取K线数据"""
        try:
            # 获取参数
            symbol = request.GET.get('symbol', 'ETHUSDT')
            timeframe = request.GET.get('timeframe', '1m')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            limit = int(request.GET.get('limit', 1000))
            
            # 设置默认时间范围（最近7天）
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_dt = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)
                start_date = start_dt.strftime('%Y-%m-%d')
            
            # 获取数据
            kline_data = self.market_service.get_kline_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            return Response({
                'success': True,
                'data': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'start_date': start_date,
                    'end_date': end_date,
                    'count': len(kline_data),
                    'klines': kline_data
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarketStatsView(APIView):
    """市场统计接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.market_service = MarketDataService()
    
    @method_decorator(cache_page(30))  # 缓存30秒
    def get(self, request):
        """获取市场统计数据"""
        try:
            symbol = request.GET.get('symbol', 'ETHUSDT')
            
            stats = self.market_service.get_market_stats(symbol)
            
            return Response({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimeframesView(APIView):
    """时间周期接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.market_service = MarketDataService()
    
    def get(self, request):
        """获取支持的时间周期"""
        try:
            timeframes = self.market_service.get_supported_timeframes()
            
            return Response({
                'success': True,
                'data': timeframes,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SymbolsView(APIView):
    """交易对接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.market_service = MarketDataService()
    
    def get(self, request):
        """获取支持的交易对"""
        try:
            symbols = self.market_service.get_supported_symbols()
            
            return Response({
                'success': True,
                'data': symbols,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
