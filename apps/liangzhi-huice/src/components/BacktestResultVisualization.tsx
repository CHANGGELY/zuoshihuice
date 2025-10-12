import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
// import { Separator } from './ui/separator';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUpIcon,
  TrendingDownIcon,
  DollarSignIcon,
  ActivityIcon,
  TargetIcon,
  ClockIcon,
  AlertTriangleIcon,
  CheckCircleIcon
} from 'lucide-react';
import { BacktestResult } from '../types/backtest';

interface BacktestResultVisualizationProps {
  result: BacktestResult;
}

export const BacktestResultVisualization: React.FC<BacktestResultVisualizationProps> = ({
  result
}) => {
  // 格式化数字
  const formatNumber = (num: number, decimals: number = 2): string => {
    return num.toLocaleString('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  // 格式化百分比
  const formatPercentage = (num: number): string => {
    return `${(num * 100).toFixed(2)}%`;
  };

  // 格式化货币
  const formatCurrency = (num: number): string => {
    return `$${formatNumber(num)}`;
  };

  // 准备权益曲线数据
  const equityChartData = result.equity_curve.map(({ timestamp, equity }) => ({
    time: new Date(timestamp * 1000).toLocaleDateString('zh-CN'),
    equity: equity,
    return: ((equity - result.params.initial_capital) / result.params.initial_capital) * 100
  }));

  // 准备交易分布数据
  const tradeDistribution = result.trades.reduce((acc, trade) => {
    const action = trade.side;
    acc[action] = (acc[action] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const tradeDistributionData = Object.entries(tradeDistribution).map(([action, count]) => ({
    action,
    count
  }));

  // 准备月度收益数据
  const monthlyReturns = equityChartData.reduce((acc, item, index) => {
    if (index === 0) return acc;
    
    const month = item.time.substring(0, 7); // YYYY-MM
    const prevEquity = equityChartData[index - 1].equity;
    const monthlyReturn = ((item.equity - prevEquity) / prevEquity) * 100;
    
    acc[month] = (acc[month] || 0) + monthlyReturn;
    return acc;
  }, {} as Record<string, number>);

  const monthlyReturnsData = Object.entries(monthlyReturns).map(([month, returnPct]) => ({
    month,
    return: returnPct
  }));

  // 颜色配置
  const colors = {
    primary: '#3b82f6',
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#6366f1'
  };

  const pieColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="space-y-6">
      {/* 概览指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">总收益率</p>
                <p className={`text-2xl font-bold ${
                  result.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercentage(result.total_return)}
                </p>
              </div>
              {result.total_return >= 0 ? (
                <TrendingUpIcon className="h-8 w-8 text-green-600" />
              ) : (
                <TrendingDownIcon className="h-8 w-8 text-red-600" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">最终权益</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(result.params.initial_capital + (result.params.initial_capital * result.total_return))}
                </p>
              </div>
              <DollarSignIcon className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">胜率</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatPercentage(result.win_rate)}
                </p>
              </div>
              <TargetIcon className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">最大回撤</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatPercentage(result.max_drawdown)}
                </p>
              </div>
              <AlertTriangleIcon className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 详细指标 */}
      <Card>
        <CardHeader>
          <CardTitle>详细指标</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ActivityIcon className="h-4 w-4" />
                <span className="text-sm font-medium">交易次数</span>
              </div>
              <p className="text-lg font-semibold">{result.total_trades}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUpIcon className="h-4 w-4" />
                <span className="text-sm font-medium">夏普比率</span>
              </div>
              <p className="text-lg font-semibold">{formatNumber(result.sharpe_ratio)}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ClockIcon className="h-4 w-4" />
                <span className="text-sm font-medium">平均持仓时间</span>
              </div>
              <p className="text-lg font-semibold">{formatNumber(result.avg_trade_return)} 小时</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <DollarSignIcon className="h-4 w-4" />
                <span className="text-sm font-medium">初始资金</span>
              </div>
              <p className="text-lg font-semibold">{formatCurrency(result.params.initial_capital)}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-4 w-4" />
                <span className="text-sm font-medium">状态</span>
              </div>
              <Badge variant={result.status === 'failed' ? 'destructive' : 'default'}>
                {result.status === 'failed' ? '失败' : result.status === 'completed' ? '完成' : '运行中'}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ActivityIcon className="h-4 w-4" />
                <span className="text-sm font-medium">交易对</span>
              </div>
              <p className="text-lg font-semibold">{result.params.strategy.symbol}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 权益曲线图 */}
      <Card>
        <CardHeader>
          <CardTitle>权益曲线</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={equityChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12 }}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  domain={['dataMin - 1000', 'dataMax + 1000']}
                />
                <Tooltip 
                  formatter={(value: number, name: string) => [
                    name === 'equity' ? formatCurrency(value) : `${formatNumber(value)}%`,
                    name === 'equity' ? '权益' : '收益率'
                  ]}
                  labelFormatter={(label) => `时间: ${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="equity" 
                  stroke={colors.primary} 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* 图表网格 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 月度收益 */}
        <Card>
          <CardHeader>
            <CardTitle>月度收益</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyReturnsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number) => [`${formatNumber(value)}%`, '收益率']}
                    labelFormatter={(label) => `月份: ${label}`}
                  />
                  <Bar 
                    dataKey="return" 
                    fill={colors.success}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* 交易分布 */}
        <Card>
          <CardHeader>
            <CardTitle>交易分布</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={tradeDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ action, percent }) => `${action} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {tradeDistributionData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [value, '交易次数']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 交易记录表格 */}
      <Card>
        <CardHeader>
          <CardTitle>最近交易记录</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">时间</th>
                  <th className="text-left p-2">操作</th>
                  <th className="text-left p-2">数量</th>
                  <th className="text-left p-2">价格</th>
                  <th className="text-left p-2">手续费</th>
                  <th className="text-left p-2">盈亏</th>
                </tr>
              </thead>
              <tbody>
                {result.trades.slice(-10).map((trade, index) => (
                  <tr key={index} className="border-b hover:bg-muted/50">
                    <td className="p-2">
                      {new Date(trade.timestamp * 1000).toLocaleString('zh-CN')}
                    </td>
                    <td className="p-2">
                      <Badge 
                        variant={trade.side === 'buy' ? 'default' : 'secondary'}
                      >
                        {trade.side.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="p-2">{formatNumber(trade.quantity, 4)}</td>
                    <td className="p-2">{formatCurrency(trade.price)}</td>
                    <td className="p-2">{formatNumber(trade.commission, 4)}</td>
                    <td className="p-2">{trade.pnl ? formatCurrency(trade.pnl) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BacktestResultVisualization;