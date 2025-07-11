"""
回测API视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json
import threading
import uuid

from .models import BacktestConfig, BacktestResult, Trade
from .engine import run_backtest_sync
from .serializers import BacktestConfigSerializer, BacktestResultSerializer


class BacktestRunView(APIView):
    """运行回测接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """启动新的回测"""
        try:
            # 获取参数
            data = request.data
            
            # 创建回测配置
            config_data = {
                'name': data.get('name', f"回测_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                'user': request.user,
                'symbol': data.get('symbol', 'ETHUSDT'),
                'start_date': data.get('start_date', '2024-06-15'),
                'end_date': data.get('end_date', '2024-07-15'),
                'initial_balance': data.get('initial_balance', 1000),
                'leverage': data.get('leverage', 125),
                'bid_spread': data.get('bid_spread', 0.002),
                'ask_spread': data.get('ask_spread', 0.002),
                'position_size_ratio': data.get('position_size_ratio', 0.02),
                'max_position_value_ratio': data.get('max_position_value_ratio', 0.8),
                'config_json': json.dumps(data.get('advanced_config', {}))
            }
            
            # 保存配置
            config = BacktestConfig.objects.create(**config_data)
            
            # 创建回测结果记录
            result = BacktestResult.objects.create(
                config=config,
                user=request.user,
                status='running'
            )
            
            # 异步运行回测
            def run_backtest_thread():
                try:
                    # 运行回测
                    backtest_config = config.get_config_dict()
                    results = run_backtest_sync(backtest_config)
                    
                    # 保存结果
                    result.status = 'completed'
                    result.total_return = results['total_return']
                    result.final_equity = results['final_equity']
                    result.total_trades = results['total_trades']
                    result.win_rate = results['win_rate']
                    result.max_drawdown = results['max_drawdown']
                    result.sharpe_ratio = results['sharpe_ratio']
                    result.result_json = json.dumps(results)
                    result.trades_json = json.dumps(results['trades'])
                    result.equity_curve_json = json.dumps(results['equity_curve'])
                    result.completed_at = datetime.now()
                    result.save()
                    
                    # 保存交易记录
                    for trade_data in results['trades']:
                        Trade.objects.create(
                            backtest_result=result,
                            timestamp=trade_data['timestamp'],
                            action=trade_data['action'],
                            side=trade_data['side'],
                            amount=trade_data['amount'],
                            price=trade_data['price'],
                            leverage=trade_data['leverage'],
                            fee=trade_data['fee'],
                            long_position=trade_data['long_position'],
                            short_position=trade_data['short_position'],
                            net_position=trade_data['net_position'],
                            equity=trade_data['equity']
                        )
                    
                except Exception as e:
                    # 保存错误信息
                    result.status = 'failed'
                    result.error_message = str(e)
                    result.completed_at = datetime.now()
                    result.save()
            
            # 启动后台线程
            thread = threading.Thread(target=run_backtest_thread)
            thread.daemon = True
            thread.start()
            
            return Response({
                'success': True,
                'data': {
                    'result_id': result.id,
                    'config_id': config.id,
                    'status': 'running',
                    'message': '回测已启动，请稍后查看结果'
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BacktestResultView(APIView):
    """回测结果接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, result_id=None):
        """获取回测结果"""
        try:
            if result_id:
                # 获取特定结果
                try:
                    result = BacktestResult.objects.get(
                        id=result_id, 
                        user=request.user
                    )
                    return Response({
                        'success': True,
                        'data': result.get_result_dict(),
                        'timestamp': datetime.now().isoformat()
                    })
                except BacktestResult.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': '回测结果不存在',
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # 获取用户的所有结果
                results = BacktestResult.objects.filter(
                    user=request.user
                ).order_by('-started_at')[:20]  # 最近20个
                
                results_data = [result.get_result_dict() for result in results]
                
                return Response({
                    'success': True,
                    'data': {
                        'results': results_data,
                        'count': len(results_data)
                    },
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BacktestConfigView(APIView):
    """回测配置接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户的回测配置"""
        try:
            configs = BacktestConfig.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]  # 最近10个配置
            
            serializer = BacktestConfigSerializer(configs, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """保存回测配置"""
        try:
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = BacktestConfigSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors,
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BacktestStatusView(APIView):
    """回测状态接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, result_id):
        """获取回测状态"""
        try:
            result = BacktestResult.objects.get(
                id=result_id,
                user=request.user
            )
            
            return Response({
                'success': True,
                'data': {
                    'id': result.id,
                    'status': result.status,
                    'started_at': result.started_at.isoformat(),
                    'completed_at': result.completed_at.isoformat() if result.completed_at else None,
                    'error_message': result.error_message if result.error_message else None
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except BacktestResult.DoesNotExist:
            return Response({
                'success': False,
                'error': '回测结果不存在',
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
