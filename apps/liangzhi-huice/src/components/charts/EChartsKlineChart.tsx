// ECharts K线图组件

import React, { useMemo, useCallback, useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { Space, Switch } from 'antd';
import { KlineData, TradingSignal, TimeFrame, SignalType } from '../../types/kline';
import { useUIStore } from '../../stores';
import { formatTime as fmtTime, formatPrice as fmtPrice, formatVolume as fmtVolume } from '../../utils/format';


// 图表配置
interface ChartConfig {
  showVolume: boolean;
  showGrid: boolean;
  showMA: boolean;
  showSignals: boolean;
  autoScale: boolean;
  theme: 'light' | 'dark';
}

// ECharts K线图组件属性
interface EChartsKlineChartProps {
  // K线数据
  data: KlineData[];
  // 交易信号
  signals?: TradingSignal[];
  // 当前交易对
  symbol?: string;
  // 当前时间周期
  timeframe?: TimeFrame;
  // 图表高度
  height?: number;
  // 是否显示工具栏
  showToolbar?: boolean;
  // 自定义样式
  style?: React.CSSProperties;
  // 图表配置
  config?: Partial<ChartConfig>;
  // 配置变更回调
  onConfigChange?: (key: string, value: any) => void;
  // 全屏状态
  isFullscreen?: boolean;
  // 加载状态
  loading?: boolean;
}

// 默认配置
const defaultConfig: ChartConfig = {
  showVolume: true,
  showGrid: true,
  showMA: true,
  showSignals: true,
  autoScale: true,
  theme: 'dark',
};

// 计算移动平均线
const calculateMA = (data: KlineData[], period: number): (number | string)[] => {
  try {
    if (!Array.isArray(data) || data.length === 0 || typeof period !== 'number' || period <= 0) {
      return [];
    }
    
    const result: (number | string)[] = [];
    
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push('-');
      } else {
        try {
          const sliceData = data.slice(i - period + 1, i + 1);
          const validData = sliceData.filter(item => 
            item && 
            typeof item.close === 'number' && 
            !isNaN(item.close)
          );
          
          if (validData.length === 0) {
            result.push('-');
          } else {
            const sum = validData.reduce((acc, item) => acc + item.close, 0);
            const avg = sum / validData.length;
            result.push(isNaN(avg) ? '-' : +(avg.toFixed(4)));
          }
        } catch (error) {
          console.warn('calculateMA inner error:', error);
          result.push('-');
        }
      }
    }
    
    return result;
  } catch (error) {
    console.warn('calculateMA error:', error);
    return [];
  }
};

// ECharts K线图主组件
export const EChartsKlineChart: React.FC<EChartsKlineChartProps> = ({
  data,
  signals = [],
  // symbol = 'ETHUSDT', // unused
  // timeframe = TimeFrame.M1, // unused
  height = 500,
  showToolbar = false,
  style,
  config: propConfig,
  onConfigChange,
  // isFullscreen = false,
  loading = false,
}) => {
  const [chartConfig, setChartConfig] = useState<ChartConfig>({
    ...defaultConfig,
    ...propConfig,
  });

  const { theme } = useUIStore();

  // 同步主题
  useEffect(() => {
    setChartConfig(prev => ({ ...prev, theme: theme as 'light' | 'dark' }));
  }, [theme]);

  // 处理配置变更
  const handleConfigChange = useCallback((key: string, value: any) => {
    setChartConfig(prev => ({ ...prev, [key]: value }));
    onConfigChange?.(key, value);
  }, [onConfigChange]);

  // 准备K线数据
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        categoryData: [],
        klineData: [],
        volumeData: [],
        ma5Data: [],
        ma10Data: [],
        ma20Data: [],
        ma30Data: [],
      };
    }

    // 按时间排序
    const sortedData = [...data].sort((a, b) => a.timestamp - b.timestamp);

    const categoryData = sortedData.map(item => fmtTime(item.timestamp));
    const klineData = sortedData.map(item => [item.open, item.close, item.low, item.high]);
    const volumeData = sortedData.map(item => item.volume);

    // 计算移动平均线
    const ma5Data = chartConfig.showMA ? calculateMA(sortedData, 5) : [];
    const ma10Data = chartConfig.showMA ? calculateMA(sortedData, 10) : [];
    const ma20Data = chartConfig.showMA ? calculateMA(sortedData, 20) : [];
    const ma30Data = chartConfig.showMA ? calculateMA(sortedData, 30) : [];

    return {
      categoryData,
      klineData,
      volumeData,
      ma5Data,
      ma10Data,
      ma20Data,
      ma30Data,
    };
  }, [data, chartConfig.showMA]);

  // ECharts 配置选项
  const option = useMemo(() => {
    const isDark = chartConfig.theme === 'dark';
    const textColor = isDark ? '#c9cdd4' : '#666';
    const backgroundColor = isDark ? '#161b22' : '#fff';
    const gridColor = isDark ? '#30363d' : '#f0f0f0';

    const baseOption: any = {
      backgroundColor,
      animation: false,
      legend: {
        data: ['K线', ...(chartConfig.showMA ? ['MA5', 'MA10', 'MA20', 'MA30'] : [])],
        textStyle: {
          color: textColor,
        },
        top: 10,
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        backgroundColor: isDark ? '#1f1f1f' : '#fff',
        borderColor: isDark ? '#404040' : '#ccc',
        textStyle: {
          color: textColor,
        },
        formatter: function (params: any) {
          const dataIndex = params[0].dataIndex;
          const klineParams = params.find((p: any) => p.seriesName === 'K线');
          
          if (!klineParams || !data[dataIndex]) {
            return '';
          }

          const klineData = data[dataIndex];
          const [open, close, low, high] = klineParams.data;
          const change = close - open;
          const changePercent = ((change / open) * 100).toFixed(2);

          let html = `<div style="margin: 0 0 7px">${klineParams.name}</div>`;
          html += `<div style="margin: 4px 0"><span style="color: #666">开盘：</span><span style="color: ${textColor}">${fmtPrice(open)}</span>`;
          html += `<span style="margin-left: 15px; color: #666">收盘：</span><span style="color: ${close >= open ? '#0ecb81' : '#f6465d'}">${fmtPrice(close)}</span></div>`;
          html += `<div style="margin: 4px 0"><span style="color: #666">最低：</span><span style="color: ${textColor}">${fmtPrice(low)}</span>`;
          html += `<span style="margin-left: 15px; color: #666">最高：</span><span style="color: ${textColor}">${fmtPrice(high)}</span></div>`;
          html += `<div style="margin: 4px 0"><span style="color: #666">涨跌：</span><span style="color: ${change >= 0 ? '#0ecb81' : '#f6465d'}">${change >= 0 ? '+' : ''}${fmtPrice(change)} (${changePercent}%)</span></div>`;
          html += `<div style="margin: 4px 0"><span style="color: #666">成交量：</span><span style="color: ${textColor}">${fmtVolume(klineData.volume)}</span></div>`;

          return html;
        },
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }],
        label: {
          backgroundColor: gridColor,
        },
      },
      grid: [
        { left: '3%', right: '3%', top: 50, height: chartConfig.showVolume ? '60%' : '80%' },
        { left: '3%', right: '3%', top: chartConfig.showVolume ? '70%' : '0%', height: chartConfig.showVolume ? '20%' : '0%' },
      ],
      xAxis: [
        {
          type: 'category',
          data: chartData.categoryData,
          boundaryGap: false,
          axisLine: { lineStyle: { color: gridColor } },
          axisLabel: { color: textColor },
          axisPointer: { label: { show: false } },
        },
        {
          type: 'category',
          gridIndex: 1,
          data: chartData.categoryData,
          boundaryGap: false,
          axisLine: { lineStyle: { color: gridColor } },
          axisLabel: { color: textColor },
          axisPointer: { label: { show: false } },
        },
      ],
      yAxis: [
        {
          scale: chartConfig.autoScale,
          axisLine: { lineStyle: { color: gridColor } },
          splitLine: { lineStyle: { color: gridColor } },
          axisLabel: { color: textColor },
        },
        {
          gridIndex: 1,
          splitNumber: 3,
          axisLine: { lineStyle: { color: gridColor } },
          splitLine: { lineStyle: { color: gridColor } },
          axisLabel: { color: textColor },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 50,
          end: 100,
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: chartConfig.showVolume ? '88%' : '85%',
          start: 50,
          end: 100,
        },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: chartData.klineData,
          itemStyle: {
            color: '#0ecb81',
            color0: '#f6465d',
            borderColor: '#0ecb81',
            borderColor0: '#f6465d',
          },
        },
        ...(chartConfig.showMA
          ? [
              { name: 'MA5', type: 'line', data: chartData.ma5Data, smooth: true, showSymbol: false },
              { name: 'MA10', type: 'line', data: chartData.ma10Data, smooth: true, showSymbol: false },
              { name: 'MA20', type: 'line', data: chartData.ma20Data, smooth: true, showSymbol: false },
              { name: 'MA30', type: 'line', data: chartData.ma30Data, smooth: true, showSymbol: false },
            ]
          : []),
        ...(chartConfig.showVolume
          ? [
              {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: chartData.volumeData,
                itemStyle: { color: '#6e7079' },
              },
            ]
          : []),
      ],
    };

    // 添加交易信号标记
    if (chartConfig.showSignals && Array.isArray(signals) && signals.length > 0) {
      const markPointData = signals
        .filter(signal => typeof signal.timestamp === 'number')
        .map(signal => ({
          name: signal.type,
          // 这里沿用 x 轴为类目轴, 使用 name 定位
          coord: [fmtTime(signal.timestamp), (typeof signal.price === 'number' && !isNaN(signal.price)) ? signal.price : undefined],
          value: signal.price,
          itemStyle: {
            color: signal.type === SignalType.BUY ? '#0ecb81' : signal.type === SignalType.SELL ? '#f6465d' : '#1890ff',
          },
        }));

      baseOption.series[0].markPoint = {
        symbol: 'pin',
        symbolSize: 35,
        label: {
          formatter: (param: any) => `${param.data.name}\n${fmtPrice(param.data.value)}`,
        },
        data: markPointData,
      };
    }

    return baseOption;
  }, [chartData, chartConfig, signals, data]);

  if (loading) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', ...style }}>
        <div>加载中...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', ...style }}>
        <div>暂无数据</div>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: `${height}px`, position: 'relative', ...style }}>
      {/* 工具栏 */}
      {showToolbar && (
        <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 1000 }}>
          <Space>
            <span style={{ color: chartConfig.theme === 'dark' ? '#c9cdd4' : '#666' }}>网格</span>
            <Switch size="small" checked={chartConfig.showGrid} onChange={(checked) => handleConfigChange('showGrid', checked)} />
            <span style={{ color: chartConfig.theme === 'dark' ? '#c9cdd4' : '#666' }}>MA</span>
            <Switch size="small" checked={chartConfig.showMA} onChange={(checked) => handleConfigChange('showMA', checked)} />
            <span style={{ color: chartConfig.theme === 'dark' ? '#c9cdd4' : '#666' }}>信号</span>
            <Switch size="small" checked={chartConfig.showSignals} onChange={(checked) => handleConfigChange('showSignals', checked)} />
            <span style={{ color: chartConfig.theme === 'dark' ? '#c9cdd4' : '#666' }}>自适应</span>
            <Switch size="small" checked={chartConfig.autoScale} onChange={(checked) => handleConfigChange('autoScale', checked)} />
          </Space>
        </div>
      )}

      <ReactECharts
        style={{ width: '100%', height: '100%' }}
        option={option}
        notMerge={true}
        lazyUpdate={true}
        theme={chartConfig.theme}
      />
    </div>
  );
};

export default EChartsKlineChart;