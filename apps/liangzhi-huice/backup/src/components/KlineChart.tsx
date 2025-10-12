import React, { useState, useEffect, useRef } from 'react';
import { Card, Select, DatePicker, Button, Spin, message } from 'antd';
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';
import dayjs, { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface KlineData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradeSignal {
  timestamp: string;
  type: 'open_long' | 'close_long' | 'open_short' | 'close_short';
  price: number;
  amount: number;
  pnl?: number;
}

interface KlineChartProps {
  symbol?: string;
  height?: number;
  tradeSignals?: TradeSignal[];
  showTradeSignals?: boolean;
  dateRange?: [Dayjs, Dayjs];
  timeframe?: string;
}

const KlineChart: React.FC<KlineChartProps> = ({
  symbol = 'ETHUSDT',
  height = 500,
  tradeSignals = [],
  showTradeSignals = false,
  dateRange: propDateRange,
  timeframe: propTimeframe
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeframe, setTimeframe] = useState(propTimeframe || '1m');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>(
    propDateRange || [dayjs().subtract(7, 'day'), dayjs()]
  );
  const [klineData, setKlineData] = useState<KlineData[]>([]);
  
  const DATA_START_DATE = dayjs('2019-11-01');
  const DATA_END_DATE = dayjs('2025-06-15');

  useEffect(() => {
    if (propDateRange) {
      setDateRange(propDateRange);
    }
  }, [propDateRange]);

  useEffect(() => {
    if (propTimeframe) {
      setTimeframe(propTimeframe);
    }
  }, [propTimeframe]);

  const timeframeOptions = [
    { value: '1m', label: '1分钟' },
    { value: '5m', label: '5分钟' },
    { value: '15m', label: '15分钟' },
    { value: '30m', label: '30分钟' },
    { value: '1h', label: '1小时' },
    { value: '4h', label: '4小时' },
    { value: '1d', label: '1天' }
  ];

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);
      const handleResize = () => {
        chartInstance.current?.resize();
      };
      window.addEventListener('resize', handleResize);
      return () => {
        window.removeEventListener('resize', handleResize);
        chartInstance.current?.dispose();
      };
    }
  }, []);

  const validateAndAdjustDateRange = (dates: [Dayjs, Dayjs]): [Dayjs, Dayjs] => {
    let [start, end] = dates;
    if (start.isBefore(DATA_START_DATE)) {
      start = DATA_START_DATE;
      message.warning(`开始日期已调整为数据起始日期: ${DATA_START_DATE.format('YYYY-MM-DD')}`);
    }
    if (end.isAfter(DATA_END_DATE)) {
      end = DATA_END_DATE;
      message.warning(`结束日期已调整为数据结束日期: ${DATA_END_DATE.format('YYYY-MM-DD')}`);
    }
    return [start, end];
  };

  const fetchKlineData = async () => {
    if (!dateRange || dateRange.length !== 2) {
      message.warning('请选择时间范围');
      return;
    }

    const adjustedDateRange = validateAndAdjustDateRange(dateRange);
    const [startDate, endDate] = adjustedDateRange;

    if (adjustedDateRange[0] !== dateRange[0] || adjustedDateRange[1] !== dateRange[1]) {
      setDateRange(adjustedDateRange);
    }

    setLoading(true);
    try {
      const h5Params = new URLSearchParams({
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
        sample_rate: timeframe === '1m' ? '1' : '5'
      });

      const h5Response = await fetch(`/api/v1/kline/range?${h5Params}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (h5Response.ok) {
        const h5Data = await h5Response.json();
        const formattedData = h5Data.data.map((item: any) => ({
          timestamp: item[0],
          open: item[1],
          close: item[2],
          low: item[3],
          high: item[4],
          volume: h5Data.volumes.find((v: any) => v[0] === item[0])?.[1] || 0
        }));
        setKlineData(formattedData);
        message.success(`从真实历史数据加载了 ${formattedData.length} 条K线数据`);
        return;
      }

      throw new Error('无法从真实数据源获取K线数据');
    } catch (error) {
      console.error('获取K线数据失败:', error);
      message.error(`获取K线数据失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (chartInstance.current && klineData.length > 0) {
      updateChart();
    }
  }, [klineData, tradeSignals, showTradeSignals]);

  const updateChart = () => {
    if (!chartInstance.current || klineData.length === 0) return;

    const candlestickData = klineData.map(item => [item.open, item.close, item.low, item.high]);
    const volumeData = klineData.map(item => item.volume);
    const timeData = klineData.map(item => dayjs(item.timestamp).format('MM-DD HH:mm'));

    const prepareTradeSignalData = () => {
      if (!showTradeSignals || !tradeSignals.length) return {};
      
      const openLongData: any[] = [];
      const closeLongData: any[] = [];
      const openShortData: any[] = [];
      const closeShortData: any[] = [];

      tradeSignals.forEach(signal => {
        const timeIndex = klineData.findIndex(item => 
          Math.abs(new Date(item.timestamp).getTime() - new Date(signal.timestamp).getTime()) < 60000
        );
        
        if (timeIndex >= 0) {
          const signalData = {
            name: signal.type,
            value: [timeIndex, signal.price],
            symbolSize: 12,
            itemStyle: {
              borderWidth: 2,
              borderColor: '#fff'
            },
            label: {
              show: true,
              position: 'top',
              formatter: () => {
                const typeMap = {
                  'open_long': '开多',
                  'close_long': '平多',
                  'open_short': '开空',
                  'close_short': '平空'
                };
                return typeMap[signal.type] || signal.type;
              },
              fontSize: 10,
              color: '#333'
            }
          };

          switch (signal.type) {
            case 'open_long':
              openLongData.push({
                ...signalData,
                itemStyle: { ...signalData.itemStyle, color: '#00ff00' }
              });
              break;
            case 'close_long':
              closeLongData.push({
                ...signalData,
                itemStyle: { ...signalData.itemStyle, color: '#90EE90' }
              });
              break;
            case 'open_short':
              openShortData.push({
                ...signalData,
                itemStyle: { ...signalData.itemStyle, color: '#ff0000' }
              });
              break;
            case 'close_short':
              closeShortData.push({
                ...signalData,
                itemStyle: { ...signalData.itemStyle, color: '#FFB6C1' }
              });
              break;
          }
        }
      });

      return { openLongData, closeLongData, openShortData, closeShortData };
    };

    const tradeSignalData = prepareTradeSignalData();

    const option = {
      title: {
        text: `${symbol} K线图 (${timeframe})`,
        left: 'center',
        textStyle: {
          color: '#333',
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function(params: any) {
          const dataIndex = params[0].dataIndex;
          const data = klineData[dataIndex];
          return `<div style="padding: 8px;">
            <div><strong>时间:</strong> ${dayjs(data.timestamp).format('YYYY-MM-DD HH:mm')}</div>
            <div><strong>开盘:</strong> ${data.open}</div>
            <div><strong>最高:</strong> ${data.high}</div>
            <div><strong>最低:</strong> ${data.low}</div>
            <div><strong>收盘:</strong> ${data.close}</div>
            <div><strong>成交量:</strong> ${data.volume.toFixed(2)}</div>
          </div>`;
        }
      },
      legend: {
        data: showTradeSignals 
          ? ['K线', '成交量', '开多', '平多', '开空', '平空']
          : ['K线', '成交量'],
        top: 30
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          height: '60%'
        },
        {
          left: '10%',
          right: '8%',
          top: '75%',
          height: '16%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: timeData,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          splitNumber: 20,
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: timeData,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          splitNumber: 20,
          min: 'dataMin',
          max: 'dataMax'
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: { show: true }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 80,
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: '85%',
          start: 80,
          end: 100
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: candlestickData,
          itemStyle: {
            color: '#ef232a',
            color0: '#14b143',
            borderColor: '#ef232a',
            borderColor0: '#14b143'
          }
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeData,
          itemStyle: {
            color: '#7fbe9e'
          }
        },
        ...(showTradeSignals ? [
          {
            name: '开多',
            type: 'scatter',
            data: tradeSignalData.openLongData || [],
            symbol: 'triangle',
            symbolRotate: 0,
            symbolSize: 12,
            itemStyle: {
              color: '#00ff00',
              borderColor: '#fff',
              borderWidth: 2
            },
            tooltip: {
              formatter: function(params: any) {
                const signal = tradeSignals.find(s => 
                  s.type === 'open_long' && 
                  Math.abs(new Date(s.timestamp).getTime() - new Date(klineData[params.value[0]]?.timestamp).getTime()) < 60000
                );
                return `<div style="padding: 8px;">
                  <div><strong>开多信号</strong></div>
                  <div>价格: ${params.value[1]}</div>
                  <div>数量: ${signal?.amount || 'N/A'}</div>
                  <div>时间: ${dayjs(klineData[params.value[0]]?.timestamp).format('YYYY-MM-DD HH:mm')}</div>
                </div>`;
              }
            }
          },
          {
            name: '平多',
            type: 'scatter',
            data: tradeSignalData.closeLongData || [],
            symbol: 'triangle',
            symbolRotate: 180,
            symbolSize: 12,
            itemStyle: {
              color: '#90EE90',
              borderColor: '#fff',
              borderWidth: 2
            },
            tooltip: {
              formatter: function(params: any) {
                const signal = tradeSignals.find(s => 
                  s.type === 'close_long' && 
                  Math.abs(new Date(s.timestamp).getTime() - new Date(klineData[params.value[0]]?.timestamp).getTime()) < 60000
                );
                return `<div style="padding: 8px;">
                  <div><strong>平多信号</strong></div>
                  <div>价格: ${params.value[1]}</div>
                  <div>数量: ${signal?.amount || 'N/A'}</div>
                  <div>盈亏: ${signal?.pnl ? (signal.pnl > 0 ? '+' : '') + signal.pnl.toFixed(2) : 'N/A'}</div>
                  <div>时间: ${dayjs(klineData[params.value[0]]?.timestamp).format('YYYY-MM-DD HH:mm')}</div>
                </div>`;
              }
            }
          },
          {
            name: '开空',
            type: 'scatter',
            data: tradeSignalData.openShortData || [],
            symbol: 'triangle',
            symbolRotate: 180,
            symbolSize: 12,
            itemStyle: {
              color: '#ff0000',
              borderColor: '#fff',
              borderWidth: 2
            },
            tooltip: {
              formatter: function(params: any) {
                const signal = tradeSignals.find(s => 
                  s.type === 'open_short' && 
                  Math.abs(new Date(s.timestamp).getTime() - new Date(klineData[params.value[0]]?.timestamp).getTime()) < 60000
                );
                return `<div style="padding: 8px;">
                  <div><strong>开空信号</strong></div>
                  <div>价格: ${params.value[1]}</div>
                  <div>数量: ${signal?.amount || 'N/A'}</div>
                  <div>时间: ${dayjs(klineData[params.value[0]]?.timestamp).format('YYYY-MM-DD HH:mm')}</div>
                </div>`;
              }
            }
          },
          {
            name: '平空',
            type: 'scatter',
            data: tradeSignalData.closeShortData || [],
            symbol: 'triangle',
            symbolRotate: 0,
            symbolSize: 12,
            itemStyle: {
              color: '#FFB6C1',
              borderColor: '#fff',
              borderWidth: 2
            },
            tooltip: {
              formatter: function(params: any) {
                const signal = tradeSignals.find(s => 
                  s.type === 'close_short' && 
                  Math.abs(new Date(s.timestamp).getTime() - new Date(klineData[params.value[0]]?.timestamp).getTime()) < 60000
                );
                return `<div style="padding: 8px;">
                  <div><strong>平空信号</strong></div>
                  <div>价格: ${params.value[1]}</div>
                  <div>数量: ${signal?.amount || 'N/A'}</div>
                  <div>盈亏: ${signal?.pnl ? (signal.pnl > 0 ? '+' : '') + signal.pnl.toFixed(2) : 'N/A'}</div>
                  <div>时间: ${dayjs(klineData[params.value[0]]?.timestamp).format('YYYY-MM-DD HH:mm')}</div>
                </div>`;
              }
            }
          }
        ] : [])
      ]
    };

    chartInstance.current.setOption(option, true);
  };

  useEffect(() => {
    fetchKlineData();
  }, [symbol, timeframe, dateRange]);

  return (
    <Card
      title="历史K线数据"
      extra={
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <Select
            value={timeframe}
            onChange={setTimeframe}
            style={{ width: 100 }}
            size="small"
          >
            {timeframeOptions.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
          <RangePicker
            value={dateRange}
            onChange={(dates) => {
              if (dates) {
                const adjustedDates = validateAndAdjustDateRange(dates as [Dayjs, Dayjs]);
                setDateRange(adjustedDates);
              }
            }}
            showTime
            size="small"
            style={{ width: 300 }}
            disabledDate={(current) => {
              return current && (
                current.isBefore(DATA_START_DATE) || 
                current.isAfter(DATA_END_DATE)
              );
            }}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchKlineData}
            loading={loading}
            size="small"
            type="primary"
          >
            刷新
          </Button>
          <Button
            icon={<DownloadOutlined />}
            size="small"
            onClick={() => {
              const dataStr = JSON.stringify(klineData, null, 2);
              const blob = new Blob([dataStr], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `${symbol}_${timeframe}_kline_data.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            导出
          </Button>
        </div>
      }
    >
      <Spin spinning={loading} tip="加载K线数据中...">
        <div
          ref={chartRef}
          style={{
            width: '100%',
            height: `${height}px`,
            minHeight: '400px'
          }}
        />
      </Spin>
      {klineData.length > 0 && (
        <div
          style={{
            marginTop: '16px',
            padding: '8px',
            background: '#f5f5f5',
            borderRadius: '4px',
            fontSize: '12px',
            color: '#666'
          }}
        >
          <span>数据统计: </span>
          <span>总数据量: {klineData.length} 条 | </span>
          <span>
            时间范围: {dayjs(klineData[0]?.timestamp).format('YYYY-MM-DD HH:mm')} ~ {dayjs(klineData[klineData.length - 1]?.timestamp).format('YYYY-MM-DD HH:mm')} | 
          </span>
          <span>当前价格: {klineData[klineData.length - 1]?.close}</span>
        </div>
      )}
    </Card>
  );
};

export default KlineChart;