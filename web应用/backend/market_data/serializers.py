"""
市场数据序列化器
"""
from rest_framework import serializers
from .models import Symbol, KlineData, MarketStats


class SymbolSerializer(serializers.ModelSerializer):
    """交易对序列化器"""
    
    class Meta:
        model = Symbol
        fields = ['id', 'symbol', 'base_asset', 'quote_asset', 'is_active']


class KlineDataSerializer(serializers.ModelSerializer):
    """K线数据序列化器"""
    symbol_name = serializers.CharField(source='symbol.symbol', read_only=True)
    
    class Meta:
        model = KlineData
        fields = [
            'id', 'symbol_name', 'timeframe', 'timestamp',
            'open_price', 'high_price', 'low_price', 'close_price',
            'volume', 'quote_volume'
        ]


class KlineChartSerializer(serializers.Serializer):
    """K线图表数据序列化器（用于前端图表）"""
    time = serializers.CharField()
    open = serializers.DecimalField(max_digits=20, decimal_places=8)
    high = serializers.DecimalField(max_digits=20, decimal_places=8)
    low = serializers.DecimalField(max_digits=20, decimal_places=8)
    close = serializers.DecimalField(max_digits=20, decimal_places=8)
    volume = serializers.DecimalField(max_digits=20, decimal_places=8)


class MarketStatsSerializer(serializers.ModelSerializer):
    """市场统计序列化器"""
    symbol_name = serializers.CharField(source='symbol.symbol', read_only=True)
    
    class Meta:
        model = MarketStats
        fields = [
            'id', 'symbol_name', 'price_24h_change', 'volume_24h',
            'high_24h', 'low_24h', 'last_price', 'updated_at'
        ]


class TimeframeSerializer(serializers.Serializer):
    """时间周期序列化器"""
    value = serializers.CharField()
    label = serializers.CharField()
    description = serializers.CharField()
