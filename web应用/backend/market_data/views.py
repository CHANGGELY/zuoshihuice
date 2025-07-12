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
import sys
import os

# 添加trading服务路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'trading'))
try:
    from services.kline_service import KlineService
    from services.backtest_service import BacktestService
except ImportError:
    KlineService = None
    BacktestService = None


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


class LocalKlineDataView(APIView):
    """本地K线数据接口（从H5文件读取）"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        if KlineService:
            self.kline_service = KlineService()
        else:
            self.kline_service = None

    def get(self, request):
        """获取本地K线数据"""
        try:
            if not self.kline_service:
                return Response({
                    'success': False,
                    'error': 'K线服务不可用'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 获取参数
            start_time = request.GET.get('start_time')
            end_time = request.GET.get('end_time')
            timeframe = request.GET.get('timeframe', '1h')
            limit = int(request.GET.get('limit', 1000))

            # 获取数据
            data = self.kline_service.get_kline_data(
                start_time=start_time,
                end_time=end_time,
                timeframe=timeframe,
                limit=limit
            )

            return Response({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataRangeView(APIView):
    """数据范围接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        if KlineService:
            self.kline_service = KlineService()
        else:
            self.kline_service = None

    def get(self, request):
        """获取数据时间范围"""
        try:
            if not self.kline_service:
                return Response({
                    'success': False,
                    'error': 'K线服务不可用'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data_range = self.kline_service.get_data_range()
            return Response({
                'success': True,
                'data': data_range,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestPriceView(APIView):
    """最新价格接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        if KlineService:
            self.kline_service = KlineService()
        else:
            self.kline_service = None

    def get(self, request):
        """获取最新价格信息"""
        try:
            if not self.kline_service:
                return Response({
                    'success': False,
                    'error': 'K线服务不可用'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            price_info = self.kline_service.get_latest_price()
            return Response({
                'success': True,
                'data': price_info,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BacktestView(APIView):
    """回测接口"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        if BacktestService:
            self.backtest_service = BacktestService()
        else:
            self.backtest_service = None

    def post(self, request):
        """运行回测"""
        try:
            if not self.backtest_service:
                return Response({
                    'success': False,
                    'error': '回测服务不可用'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 运行回测
            result = self.backtest_service.run_backtest(request.data)

            return Response({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
