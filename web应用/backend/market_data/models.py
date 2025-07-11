"""
市场数据模型
"""
from django.db import models


class Symbol(models.Model):
    """交易对模型"""
    symbol = models.CharField(max_length=20, unique=True, verbose_name='交易对')
    base_asset = models.CharField(max_length=10, verbose_name='基础资产')
    quote_asset = models.CharField(max_length=10, verbose_name='计价资产')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '交易对'
        verbose_name_plural = '交易对'
        
    def __str__(self):
        return self.symbol


class KlineData(models.Model):
    """K线数据模型"""
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, verbose_name='交易对')
    timeframe = models.CharField(max_length=10, verbose_name='时间周期')
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    open_price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='开盘价')
    high_price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='最高价')
    low_price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='最低价')
    close_price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='收盘价')
    volume = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='成交量')
    quote_volume = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='成交额')
    
    class Meta:
        verbose_name = 'K线数据'
        verbose_name_plural = 'K线数据'
        unique_together = ['symbol', 'timeframe', 'timestamp']
        indexes = [
            models.Index(fields=['symbol', 'timeframe', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        
    def __str__(self):
        return f"{self.symbol.symbol} {self.timeframe} {self.timestamp}"


class MarketStats(models.Model):
    """市场统计数据"""
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, verbose_name='交易对')
    price_24h_change = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='24小时涨跌幅')
    volume_24h = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='24小时成交量')
    high_24h = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='24小时最高价')
    low_24h = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='24小时最低价')
    last_price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='最新价格')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '市场统计'
        verbose_name_plural = '市场统计'
        
    def __str__(self):
        return f"{self.symbol.symbol} 统计数据"
