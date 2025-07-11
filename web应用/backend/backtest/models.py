"""
回测模型
"""
from django.db import models
from django.contrib.auth.models import User
import json


class BacktestConfig(models.Model):
    """回测配置模型"""
    name = models.CharField(max_length=100, verbose_name='配置名称')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基础配置
    symbol = models.CharField(max_length=20, default='ETHUSDT', verbose_name='交易对')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    initial_balance = models.DecimalField(max_digits=20, decimal_places=8, default=1000, verbose_name='初始资金')
    
    # 策略配置
    leverage = models.IntegerField(default=125, verbose_name='杠杆倍数')
    bid_spread = models.DecimalField(max_digits=10, decimal_places=6, default=0.002, verbose_name='买单价差')
    ask_spread = models.DecimalField(max_digits=10, decimal_places=6, default=0.002, verbose_name='卖单价差')
    position_size_ratio = models.DecimalField(max_digits=10, decimal_places=6, default=0.02, verbose_name='仓位比例')
    max_position_value_ratio = models.DecimalField(max_digits=10, decimal_places=6, default=0.8, verbose_name='最大仓位比例')
    
    # 其他配置
    config_json = models.TextField(blank=True, verbose_name='完整配置JSON')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '回测配置'
        verbose_name_plural = '回测配置'
        
    def __str__(self):
        return f"{self.name} - {self.symbol}"
    
    def get_config_dict(self):
        """获取配置字典"""
        config = {
            'symbol': self.symbol,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'initial_balance': float(self.initial_balance),
            'leverage': self.leverage,
            'bid_spread': float(self.bid_spread),
            'ask_spread': float(self.ask_spread),
            'position_size_ratio': float(self.position_size_ratio),
            'max_position_value_ratio': float(self.max_position_value_ratio),
        }
        
        # 合并JSON配置
        if self.config_json:
            try:
                json_config = json.loads(self.config_json)
                config.update(json_config)
            except json.JSONDecodeError:
                pass
                
        return config


class BacktestResult(models.Model):
    """回测结果模型"""
    config = models.ForeignKey(BacktestConfig, on_delete=models.CASCADE, verbose_name='回测配置')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基础信息
    status = models.CharField(max_length=20, choices=[
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ], default='running', verbose_name='状态')
    
    # 回测结果
    total_return = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, verbose_name='总收益率')
    final_equity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, verbose_name='最终权益')
    total_trades = models.IntegerField(null=True, blank=True, verbose_name='总交易次数')
    win_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='胜率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name='最大回撤')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name='夏普比率')
    
    # 详细结果
    result_json = models.TextField(blank=True, verbose_name='详细结果JSON')
    trades_json = models.TextField(blank=True, verbose_name='交易记录JSON')
    equity_curve_json = models.TextField(blank=True, verbose_name='权益曲线JSON')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 时间戳
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '回测结果'
        verbose_name_plural = '回测结果'
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.config.name} - {self.status}"
    
    def get_result_dict(self):
        """获取结果字典"""
        result = {
            'id': self.id,
            'status': self.status,
            'total_return': float(self.total_return) if self.total_return else None,
            'final_equity': float(self.final_equity) if self.final_equity else None,
            'total_trades': self.total_trades,
            'win_rate': float(self.win_rate) if self.win_rate else None,
            'max_drawdown': float(self.max_drawdown) if self.max_drawdown else None,
            'sharpe_ratio': float(self.sharpe_ratio) if self.sharpe_ratio else None,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
        
        # 添加详细结果
        if self.result_json:
            try:
                result['details'] = json.loads(self.result_json)
            except json.JSONDecodeError:
                pass
                
        # 添加交易记录
        if self.trades_json:
            try:
                result['trades'] = json.loads(self.trades_json)
            except json.JSONDecodeError:
                pass
                
        # 添加权益曲线
        if self.equity_curve_json:
            try:
                result['equity_curve'] = json.loads(self.equity_curve_json)
            except json.JSONDecodeError:
                pass
                
        return result


class Trade(models.Model):
    """交易记录模型"""
    backtest_result = models.ForeignKey(BacktestResult, on_delete=models.CASCADE, verbose_name='回测结果')
    
    # 交易信息
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    action = models.CharField(max_length=50, verbose_name='交易动作')
    side = models.CharField(max_length=10, choices=[
        ('buy', '买入'),
        ('sell', '卖出'),
    ], verbose_name='方向')
    amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='数量')
    price = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='价格')
    leverage = models.IntegerField(verbose_name='杠杆')
    fee = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='手续费')
    
    # 仓位信息
    long_position = models.DecimalField(max_digits=20, decimal_places=8, default=0, verbose_name='多头仓位')
    short_position = models.DecimalField(max_digits=20, decimal_places=8, default=0, verbose_name='空头仓位')
    net_position = models.DecimalField(max_digits=20, decimal_places=8, default=0, verbose_name='净仓位')
    equity = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='权益')
    
    class Meta:
        verbose_name = '交易记录'
        verbose_name_plural = '交易记录'
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.action} {self.amount} @ {self.price}"
