"""
回测序列化器
"""
from rest_framework import serializers
from .models import BacktestConfig, BacktestResult, Trade


class BacktestConfigSerializer(serializers.ModelSerializer):
    """回测配置序列化器"""
    
    class Meta:
        model = BacktestConfig
        fields = [
            'id', 'name', 'symbol', 'start_date', 'end_date',
            'initial_balance', 'leverage', 'bid_spread', 'ask_spread',
            'position_size_ratio', 'max_position_value_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BacktestResultSerializer(serializers.ModelSerializer):
    """回测结果序列化器"""
    config_name = serializers.CharField(source='config.name', read_only=True)
    
    class Meta:
        model = BacktestResult
        fields = [
            'id', 'config_name', 'status', 'total_return', 'final_equity',
            'total_trades', 'win_rate', 'max_drawdown', 'sharpe_ratio',
            'started_at', 'completed_at', 'error_message'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class TradeSerializer(serializers.ModelSerializer):
    """交易记录序列化器"""
    
    class Meta:
        model = Trade
        fields = [
            'id', 'timestamp', 'action', 'side', 'amount', 'price',
            'leverage', 'fee', 'long_position', 'short_position',
            'net_position', 'equity'
        ]
        read_only_fields = ['id']


class BacktestRunRequestSerializer(serializers.Serializer):
    """回测运行请求序列化器"""
    name = serializers.CharField(max_length=100, required=False)
    symbol = serializers.CharField(max_length=20, default='ETHUSDT')
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    initial_balance = serializers.DecimalField(max_digits=20, decimal_places=8, default=1000)
    leverage = serializers.IntegerField(default=125, min_value=1, max_value=125)
    bid_spread = serializers.DecimalField(max_digits=10, decimal_places=6, default=0.002)
    ask_spread = serializers.DecimalField(max_digits=10, decimal_places=6, default=0.002)
    position_size_ratio = serializers.DecimalField(max_digits=10, decimal_places=6, default=0.02)
    max_position_value_ratio = serializers.DecimalField(max_digits=10, decimal_places=6, default=0.8)
    advanced_config = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        """验证数据"""
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("开始日期必须早于结束日期")
        
        if data['initial_balance'] <= 0:
            raise serializers.ValidationError("初始资金必须大于0")
        
        if data['leverage'] < 1 or data['leverage'] > 125:
            raise serializers.ValidationError("杠杆倍数必须在1-125之间")
        
        return data
