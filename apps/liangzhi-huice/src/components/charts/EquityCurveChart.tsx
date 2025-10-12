// EquityCurveChart 资金曲线图组件

import React, { useMemo, useCallback, useState, useEffect } from 'react';
import { Card, Select, Button, Space, Tooltip, Switch, message } from 'antd';
import {
  ReloadOutlined,
  DownloadOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
  Legend,
  Brush,
} from 'recharts';
import { useBacktestStore } from '../../stores';
import { useUIStore } from '../../stores';
// import { BacktestResult } from '../../types/backtest';
import { ChartLoading } from '../common/Loading';
import { formatNumberWithCommas, formatTime as formatTimeCompact } from '../../utils/format';

const { Option } = Select;

// 图表配置
interface ChartConfig {
  showGrid: boolean;
  showBenchmark: boolean;
  showDrawdown: boolean;
  showReturns: boolean;
  chartType: 'line' | 'area';
  theme: 'light' | 'dark';
}

// EquityCurveChart组件属性
interface EquityCurveChartProps {
  // 回测结果ID
  backtestId?: string;
  // 图表高度
  height?: number;
  // 是否显示工具栏
  showToolbar?: boolean;
  // 是否显示对比功能
  showComparison?: boolean;
  // 自定义样式
  style?: React.CSSProperties;
  // 图表配置
  config?: Partial<ChartConfig>;
}

// 格式化数值
const formatValue = (value: number): string => {
  if (Math.abs(value) >= 1000000) {
    return `${(value / 1000000).toFixed(2)}M`;
  }
  if (Math.abs(value) >= 1000) {
    return `${(value / 1000).toFixed(2)}K`;
  }
  return value.toFixed(2);
};



// 格式化时间
const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleDateString('zh-CN');
};

// 定义资金曲线点类型
type EquityPoint = {
  timestamp: number;
  datetime: string;
  equity: number;
  drawdown: number;
};

// 计算回撤
const calculateDrawdown = (equityData: EquityPoint[]): (EquityPoint & { drawdown: number })[] => {
  let peak = 0;
  return equityData.map(point => {
    peak = Math.max(peak, point.equity);
    const drawdown = peak > 0 ? (point.equity - peak) / peak : 0;
    return {
      ...point,
      drawdown,
    };
  });
};

// 计算收益率
const calculateReturns = (equityData: EquityPoint[]): (EquityPoint & { returns: number })[] => {
  if (equityData.length === 0) return [];
  
  const initialEquity = equityData[0].equity;
  return equityData.map(point => ({
    ...point,
    returns: initialEquity > 0 ? (point.equity - initialEquity) / initialEquity : 0,
  }));
};

// 自定义工具提示
const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: any[];
  label?: string | number;
  config: ChartConfig;
}> = ({ active, payload, label, config }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: config.theme === 'dark' ? '#1f1f1f' : '#fff',
          border: '1px solid #ccc',
          borderRadius: '4px',
          padding: '12px',
          fontSize: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <p style={{ margin: 0, fontWeight: 'bold', marginBottom: '8px' }}>
          {label}
        </p>
        <p style={{ margin: 0, color: '#1890ff' }}>
          资金: {formatNumberWithCommas(data.equity, 2)}
        </p>
        {config.showReturns && (
          <p style={{ margin: 0, color: data.returns >= 0 ? '#52c41a' : '#ff4d4f' }}>
            收益率: {`${(data.returns * 100).toFixed(2)}%`}
          </p>
        )}
        {config.showDrawdown && (
          <p style={{ margin: 0, color: '#ff4d4f' }}>
            回撤: {`${(data.drawdown * 100).toFixed(2)}%`}
          </p>
        )}
        {config.showBenchmark && data.benchmark && (
          <p style={{ margin: 0, color: '#722ed1' }}>
            基准: {formatNumberWithCommas(data.benchmark, 2)}
          </p>
        )}
      </div>
    );
  }
  return null;
};

// EquityCurveChart主组件
export const EquityCurveChart: React.FC<EquityCurveChartProps> = ({
  backtestId,
  height = 400,
  showToolbar = true,
  showComparison = false,
  style,
  config: propConfig,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartConfig, setChartConfig] = useState<ChartConfig>({
    showGrid: true,
    showBenchmark: false,
    showDrawdown: false,
    showReturns: true,
    chartType: 'line',
    theme: 'light',
    ...propConfig,
  });

  const {
    currentBacktest,
    backtestHistory,
    selectedBacktests,
    loadingState,
    error,
    getBacktestResult,
  } = useBacktestStore();

  const { theme } = useUIStore();

  // 同步主题
  useEffect(() => {
    const chartTheme = theme === 'auto' ? 'light' : theme as 'light' | 'dark';
    setChartConfig(prev => ({ ...prev, theme: chartTheme }));
  }, [theme]);

  // 获取当前显示的回测结果
  const displayBacktest = useMemo(() => {
    if (backtestId) {
      const items = backtestHistory && 'items' in backtestHistory ? backtestHistory.items : [];
      return items.find((bt: any) => bt.id === backtestId) || currentBacktest;
    }
    return currentBacktest;
  }, [backtestId, backtestHistory, currentBacktest]);

  // 检查是否为BacktestResult类型（有result属性）
  const hasResult = displayBacktest && 'result' in displayBacktest && displayBacktest.result;
  
  // 处理资金曲线数据
  const chartData = useMemo(() => {
    const equityCurve = hasResult && displayBacktest.result ? displayBacktest.result.equity_curve : null;
    
    if (!equityCurve) return [];
    
    let data = equityCurve.map((point: any) => ({
      ...point,
      time: formatTimeCompact(point.timestamp, 'date'),
    }));

    // 计算回撤
    if (chartConfig.showDrawdown) {
      data = calculateDrawdown(data) as any;
    }

    // 计算收益率
    if (chartConfig.showReturns) {
      data = calculateReturns(data) as any;
    }

    return data;
  }, [displayBacktest, chartConfig.showDrawdown, chartConfig.showReturns]);

  // 处理对比数据
  const comparisonData = useMemo(() => {
    if (!showComparison || !selectedBacktests || selectedBacktests.length === 0) return [];
    
    return selectedBacktests.map((backtest: any) => {
      if (!backtest.result?.equity_curve) return null;
      
      let data = backtest.result.equity_curve.map((point: any) => ({
        ...point,
        time: formatTime(point.timestamp),
      }));

      if (chartConfig.showReturns) {
        data = calculateReturns(data) as any;
      }

      return {
        id: backtest.id,
        name: `回测${String(backtest.id).slice(-6)}`,
        data,
        color: `hsl(${Math.random() * 360}, 70%, 50%)`,
      };
    }).filter((item): item is NonNullable<typeof item> => item !== null);
  }, [selectedBacktests, showComparison, chartConfig.showReturns]);

  // 处理全屏切换
  const handleFullscreenToggle = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // 处理刷新
  const handleRefresh = useCallback(() => {
    if (displayBacktest?.id) {
      getBacktestResult(String(displayBacktest.id));
      message.success('数据已刷新');
    }
  }, [displayBacktest?.id, getBacktestResult]);

  // 处理下载
  const handleDownload = useCallback(() => {
    if (chartData.length === 0) {
      message.warning('暂无数据可下载');
      return;
    }

    const csvContent = [
      'timestamp,equity,returns,drawdown',
      ...chartData.map((item: any) => 
        `${item.timestamp},${item.equity},${item.returns || 0},${item.drawdown || 0}`
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `equity_curve_${displayBacktest?.id || Date.now()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    message.success('数据下载成功');
  }, [chartData, displayBacktest?.id]);

  // 处理配置变化
  const handleConfigChange = useCallback((key: keyof ChartConfig, value: any) => {
    setChartConfig(prev => ({ ...prev, [key]: value }));
  }, []);

  if (error) {
    return (
      <Card style={style}>
        <div style={{ textAlign: 'center', padding: '50px', color: '#ff4d4f' }}>
          <p>资金曲线加载失败: {error.message}</p>
          <Button onClick={handleRefresh}>重试</Button>
        </div>
      </Card>
    );
  }

  const ChartComponent = chartConfig.chartType === 'area' ? AreaChart : LineChart;

  return (
    <Card
      title="资金曲线"
      extra={
        showToolbar && (
          <Space>
            <Select
              value={chartConfig.chartType}
              onChange={(value) => handleConfigChange('chartType', value)}
              style={{ width: 80 }}
              size="small"
            >
              <Option value="line">线图</Option>
              <Option value="area">面积图</Option>
            </Select>
            
            <Tooltip title="显示/隐藏收益率">
              <Switch
                checked={chartConfig.showReturns}
                onChange={(checked) => handleConfigChange('showReturns', checked)}
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="显示/隐藏回撤">
              <Switch
                checked={chartConfig.showDrawdown}
                onChange={(checked) => handleConfigChange('showDrawdown', checked)}
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="显示/隐藏基准">
              <Switch
                checked={chartConfig.showBenchmark}
                onChange={(checked) => handleConfigChange('showBenchmark', checked)}
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="刷新数据">
              <Button
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loadingState.isLoading}
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="下载数据">
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownload}
                size="small"
              />
            </Tooltip>
            
            <Tooltip title={isFullscreen ? '退出全屏' : '全屏显示'}>
              <Button
                icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                onClick={handleFullscreenToggle}
                size="small"
              />
            </Tooltip>
          </Space>
        )
      }
      styles={{ body: { padding: 0 } }}
      style={{
        ...style,
        height: isFullscreen ? '100vh' : undefined,
      }}
    >
      {loadingState.isLoading ? (
        <ChartLoading height={height} />
      ) : (
        <ResponsiveContainer width="100%" height={isFullscreen ? window.innerHeight - 100 : height}>
          <ChartComponent
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            {chartConfig.showGrid && (
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={chartConfig.theme === 'dark' ? '#404040' : '#f0f0f0'}
              />
            )}
            
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: chartConfig.theme === 'dark' ? '#fff' : '#666' }}
            />
            
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: chartConfig.theme === 'dark' ? '#fff' : '#666' }}
              tickFormatter={formatValue}
            />
            
            <RechartsTooltip content={<CustomTooltip config={chartConfig} />} />
            
            <Legend />
            
            {/* 主要资金曲线 */}
            {chartConfig.chartType === 'area' ? (
              <Area
                type="monotone"
                dataKey="equity"
                stroke="#1890ff"
                fill="#1890ff"
                fillOpacity={0.3}
                strokeWidth={2}
                name="资金"
              />
            ) : (
              <Line
                type="monotone"
                dataKey="equity"
                stroke="#1890ff"
                strokeWidth={2}
                dot={false}
                name="资金"
                activeDot={{ r: 4, stroke: '#1890ff', strokeWidth: 2 }}
              />
            )}
            
            {/* 回撤曲线 */}
            {chartConfig.showDrawdown && (
              <Line
                type="monotone"
                dataKey="drawdown"
                stroke="#ff4d4f"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="回撤"
              />
            )}
            
            {/* 对比曲线 */}
            {showComparison &&
              comparisonData.map((comparison, index) => (
                <Line
                  key={comparison.id}
                  type="monotone"
                  dataKey={`comparison_${index}`}
                  stroke={comparison.color}
                  strokeWidth={1}
                  dot={false}
                  name={comparison.name}
                />
              ))}
            
            {/* 基准线 */}
            {chartConfig.showBenchmark && (
              <ReferenceLine
                y={hasResult && displayBacktest.result ? displayBacktest.result.params?.initial_capital || 100000 : 100000}
                stroke="#722ed1"
                strokeDasharray="3 3"
                label={{ value: '基准', position: 'left' }}
              />
            )}
            
            {/* 时间范围选择器 */}
            <Brush
              dataKey="time"
              height={30}
              stroke={chartConfig.theme === 'dark' ? '#404040' : '#d9d9d9'}
              fill={chartConfig.theme === 'dark' ? '#262626' : '#fafafa'}
            />
          </ChartComponent>
        </ResponsiveContainer>
      )}
    </Card>
  );
};

export default EquityCurveChart;