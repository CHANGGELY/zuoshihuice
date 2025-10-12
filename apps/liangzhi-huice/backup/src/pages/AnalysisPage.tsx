import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Select,
  DatePicker,
  Button,
  Table,
  Tabs,
  Statistic,
  Progress,
  Tag,
  Space,
  Alert,
  Divider,
} from 'antd';
import {
  DownloadOutlined,
  PrinterOutlined,
  ShareAltOutlined,
  ReloadOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface AnalysisData {
  strategy: string;
  period: string;
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number;
  calmarRatio: number;
  winRate: number;
  profitFactor: number;
  avgWin: number;
  avgLoss: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  largestWin: number;
  largestLoss: number;
  avgTradeDuration: string;
  recoveryFactor: number;
}

interface MonthlyReturn {
  month: string;
  return: number;
  trades: number;
}

interface DrawdownPeriod {
  start: string;
  end: string;
  duration: number;
  maxDrawdown: number;
  recovery: string;
}

const AnalysisPage: React.FC = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('atr_grid');
  const [selectedPeriod, setSelectedPeriod] = useState('1year');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // 模拟分析数据
  const analysisData: AnalysisData = {
    strategy: 'ATR网格策略',
    period: '2023-01-01 至 2024-01-01',
    totalReturn: 24.67,
    annualizedReturn: 18.45,
    volatility: 12.34,
    sharpeRatio: 1.85,
    sortinoRatio: 2.41,
    maxDrawdown: -12.34,
    calmarRatio: 1.49,
    winRate: 65.8,
    profitFactor: 1.42,
    avgWin: 2.34,
    avgLoss: -1.65,
    totalTrades: 156,
    winningTrades: 103,
    losingTrades: 53,
    largestWin: 8.92,
    largestLoss: -4.56,
    avgTradeDuration: '2.5天',
    recoveryFactor: 2.0,
  };

  const monthlyReturns: MonthlyReturn[] = [
    { month: '2023-01', return: 3.45, trades: 12 },
    { month: '2023-02', return: -1.23, trades: 8 },
    { month: '2023-03', return: 5.67, trades: 15 },
    { month: '2023-04', return: 2.34, trades: 10 },
    { month: '2023-05', return: -2.11, trades: 9 },
    { month: '2023-06', return: 4.56, trades: 13 },
    { month: '2023-07', return: 1.89, trades: 11 },
    { month: '2023-08', return: -3.45, trades: 7 },
    { month: '2023-09', return: 6.78, trades: 16 },
    { month: '2023-10', return: 3.21, trades: 14 },
    { month: '2023-11', return: 2.67, trades: 12 },
    { month: '2023-12', return: 1.89, trades: 9 },
  ];

  const drawdownPeriods: DrawdownPeriod[] = [
    {
      start: '2023-02-15',
      end: '2023-03-10',
      duration: 23,
      maxDrawdown: -12.34,
      recovery: '2023-04-05',
    },
    {
      start: '2023-05-20',
      end: '2023-06-08',
      duration: 19,
      maxDrawdown: -8.76,
      recovery: '2023-07-12',
    },
    {
      start: '2023-08-12',
      end: '2023-08-28',
      duration: 16,
      maxDrawdown: -6.45,
      recovery: '2023-09-15',
    },
  ];

  // 权益曲线图表配置
  const equityCurveOption = {
    title: {
      text: '权益曲线分析',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const equity = params[0];
        const drawdown = params[1];
        return `
          ${equity.name}: $${equity.value.toLocaleString()}<br/>
          ${drawdown.name}: ${drawdown.value.toFixed(2)}%
        `;
      },
    },
    legend: {
      data: ['账户权益', '回撤'],
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 365 }, (_, i) => {
        const date = dayjs('2023-01-01').add(i, 'day');
        return date.format('MM-DD');
      }),
    },
    yAxis: [
      {
        type: 'value',
        name: '权益 ($)',
        position: 'left',
        axisLabel: {
          formatter: '${value}',
        },
      },
      {
        type: 'value',
        name: '回撤 (%)',
        position: 'right',
        max: 0,
        axisLabel: {
          formatter: '{value}%',
        },
      },
    ],
    series: [
      {
        name: '账户权益',
        type: 'line',
        data: Array.from({ length: 365 }, (_, i) => {
          const baseValue = 100000;
          const trend = i * 0.0007; // 年化约25%
          const noise = (Math.random() - 0.5) * 0.02;
          return Math.round(baseValue * (1 + trend + noise));
        }),
        lineStyle: {
          color: '#1890ff',
          width: 2,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.05)' },
            ],
          },
        },
      },
      {
        name: '回撤',
        type: 'line',
        yAxisIndex: 1,
        data: Array.from({ length: 365 }, () => {
          return -(Math.random() * 15);
        }),
        lineStyle: {
          color: '#ff4d4f',
          width: 1,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 77, 79, 0.3)' },
              { offset: 1, color: 'rgba(255, 77, 79, 0.05)' },
            ],
          },
        },
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
  };

  // 月度收益图表配置
  const monthlyReturnOption = {
    title: {
      text: '月度收益分析',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0];
        return `${data.name}<br/>收益率: ${data.value}%<br/>交易次数: ${monthlyReturns[data.dataIndex].trades}`;
      },
    },
    xAxis: {
      type: 'category',
      data: monthlyReturns.map(item => item.month),
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        data: monthlyReturns.map(item => ({
          value: item.return,
          itemStyle: {
            color: item.return >= 0 ? '#52c41a' : '#ff4d4f',
          },
        })),
        type: 'bar',
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
  };

  // 风险收益散点图配置
  const riskReturnOption = {
    title: {
      text: '风险收益分析',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `收益率: ${params.value[0]}%<br/>波动率: ${params.value[1]}%<br/>夏普比率: ${params.value[2]}`;
      },
    },
    xAxis: {
      type: 'value',
      name: '年化收益率 (%)',
      axisLabel: {
        formatter: '{value}%',
      },
    },
    yAxis: {
      type: 'value',
      name: '年化波动率 (%)',
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        symbolSize: (data: number[]) => Math.sqrt(data[2]) * 20,
        data: [
          [18.45, 12.34, 1.85], // 当前策略
          [15.2, 18.5, 0.82],   // 基准1
          [22.1, 25.3, 0.87],   // 基准2
          [8.5, 8.2, 1.04],     // 基准3
        ],
        type: 'scatter',
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
  };

  const drawdownColumns = [
    {
      title: '开始日期',
      dataIndex: 'start',
      key: 'start',
    },
    {
      title: '结束日期',
      dataIndex: 'end',
      key: 'end',
    },
    {
      title: '持续天数',
      dataIndex: 'duration',
      key: 'duration',
      render: (value: number) => `${value}天`,
    },
    {
      title: '最大回撤',
      dataIndex: 'maxDrawdown',
      key: 'maxDrawdown',
      render: (value: number) => (
        <Text type="danger">{value.toFixed(2)}%</Text>
      ),
    },
    {
      title: '恢复日期',
      dataIndex: 'recovery',
      key: 'recovery',
    },
  ];

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  return (
    <div style={{ padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>分析报告</Title>
        <Space>
          <Select
            value={selectedStrategy}
            onChange={setSelectedStrategy}
            style={{ width: 200 }}
          >
            <Option value="atr_grid">ATR网格策略</Option>
            <Option value="mean_reversion">均值回归策略</Option>
            <Option value="momentum">动量策略</Option>
          </Select>
          <Select
            value={selectedPeriod}
            onChange={setSelectedPeriod}
            style={{ width: 150 }}
          >
            <Option value="1month">近1个月</Option>
            <Option value="3months">近3个月</Option>
            <Option value="6months">近6个月</Option>
            <Option value="1year">近1年</Option>
            <Option value="all">全部</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<DownloadOutlined />}>
            导出报告
          </Button>
          <Button icon={<PrinterOutlined />}>
            打印
          </Button>
          <Button icon={<ShareAltOutlined />}>
            分享
          </Button>
        </Space>
      </div>

      <Alert
        message="策略表现总结"
        description={`${analysisData.strategy}在${analysisData.period}期间表现优异，总收益率达到${analysisData.totalReturn}%，夏普比率${analysisData.sharpeRatio}，最大回撤控制在${Math.abs(analysisData.maxDrawdown)}%以内。`}
        type="success"
        style={{ marginBottom: '24px' }}
      />

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'overview',
            label: '策略概览',
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="总收益率"
                        value={analysisData.totalReturn}
                        precision={2}
                        valueStyle={{ color: analysisData.totalReturn >= 0 ? '#3f8600' : '#cf1322' }}
                        prefix={analysisData.totalReturn >= 0 ? <RiseOutlined /> : <FallOutlined />}
                        suffix="%"
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="年化收益率"
                        value={analysisData.annualizedReturn}
                        precision={2}
                        valueStyle={{ color: '#3f8600' }}
                        suffix="%"
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="夏普比率"
                        value={analysisData.sharpeRatio}
                        precision={2}
                        valueStyle={{ color: '#1890ff' }}
                        prefix={<TrophyOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="最大回撤"
                        value={Math.abs(analysisData.maxDrawdown)}
                        precision={2}
                        valueStyle={{ color: '#cf1322' }}
                        suffix="%"
                      />
                    </Card>
                  </Col>
                </Row>

                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic title="胜率" value={analysisData.winRate} precision={1} suffix="%" />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic title="盈利因子" value={analysisData.profitFactor} precision={2} />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic title="总交易次数" value={analysisData.totalTrades} />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic title="平均持仓时间" value={analysisData.avgTradeDuration} />
                    </Card>
                  </Col>
                </Row>

                <Card>
                  <ReactECharts option={equityCurveOption} style={{ height: '400px' }} />
                </Card>
              </>
            )
          },

          {
            key: 'returns',
            label: '收益分析',
            children: (
              <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                <Col xs={24} lg={12}>
                  <Card>
                    <ReactECharts option={monthlyReturnOption} style={{ height: '300px' }} />
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card>
                    <Title level={4}>收益统计</Title>
                    <Row gutter={[16, 16]}>
                      <Col span={12}>
                        <Statistic
                          title="平均盈利"
                          value={analysisData.avgWin}
                          precision={2}
                          valueStyle={{ color: '#3f8600' }}
                          suffix="%"
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="平均亏损"
                          value={Math.abs(analysisData.avgLoss)}
                          precision={2}
                          valueStyle={{ color: '#cf1322' }}
                          suffix="%"
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="最大单笔盈利"
                          value={analysisData.largestWin}
                          precision={2}
                          valueStyle={{ color: '#3f8600' }}
                          suffix="%"
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="最大单笔亏损"
                          value={Math.abs(analysisData.largestLoss)}
                          precision={2}
                          valueStyle={{ color: '#cf1322' }}
                          suffix="%"
                        />
                      </Col>
                    </Row>
                    
                    <Divider />
                    
                    <div>
                      <Text strong>盈亏比: </Text>
                      <Text>{(analysisData.avgWin / Math.abs(analysisData.avgLoss)).toFixed(2)}</Text>
                    </div>
                    <div style={{ marginTop: '8px' }}>
                      <Text strong>盈利交易: </Text>
                      <Tag color="green">{analysisData.winningTrades}笔</Tag>
                      <Text strong>亏损交易: </Text>
                      <Tag color="red">{analysisData.losingTrades}笔</Tag>
                    </div>
                  </Card>
                </Col>
              </Row>
            )
          },

          {
            key: 'risk',
            label: '风险分析',
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="年化波动率"
                        value={analysisData.volatility}
                        precision={2}
                        suffix="%"
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="索提诺比率"
                        value={analysisData.sortinoRatio}
                        precision={2}
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="卡玛比率"
                        value={analysisData.calmarRatio}
                        precision={2}
                      />
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card>
                      <Statistic
                        title="恢复因子"
                        value={analysisData.recoveryFactor}
                        precision={2}
                      />
                    </Card>
                  </Col>
                </Row>

                <Row gutter={[16, 16]}>
                  <Col xs={24} lg={12}>
                    <Card>
                      <ReactECharts option={riskReturnOption} style={{ height: '300px' }} />
                    </Card>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Card>
                      <Title level={4}>主要回撤期</Title>
                      <Table
                        columns={drawdownColumns}
                        dataSource={drawdownPeriods}
                        rowKey="start"
                        size="small"
                        pagination={false}
                      />
                    </Card>
                  </Col>
                </Row>
              </>
            )
          },

          {
            key: 'benchmark',
            label: '基准对比',
            children: (
              <Card>
                <Title level={4}>策略 vs 基准表现</Title>
                <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
                  <Col xs={24} sm={6}>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                          ATR网格策略
                        </div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3f8600', marginTop: '8px' }}>
                          +24.67%
                        </div>
                        <div style={{ color: '#666' }}>年化收益率</div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={6}>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                          ETH持有策略
                        </div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3f8600', marginTop: '8px' }}>
                          +18.92%
                        </div>
                        <div style={{ color: '#666' }}>年化收益率</div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={6}>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                          市场指数
                        </div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3f8600', marginTop: '8px' }}>
                          +12.45%
                        </div>
                        <div style={{ color: '#666' }}>年化收益率</div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={6}>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                          无风险利率
                        </div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>
                          +3.50%
                        </div>
                        <div style={{ color: '#666' }}>年化收益率</div>
                      </div>
                    </Card>
                  </Col>
                </Row>

                <div style={{ marginTop: '24px' }}>
                  <Alert
                    message="策略优势"
                    description="相比基准策略，ATR网格策略在风险调整后收益方面表现突出，夏普比率达到1.85，显著优于市场平均水平。策略在控制回撤的同时实现了稳定的超额收益。"
                    type="info"
                  />
                </div>
              </Card>
            )
          }
        ]}
       />
     </div>
  );
};

export default AnalysisPage;