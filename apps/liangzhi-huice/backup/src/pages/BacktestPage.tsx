import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Form,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Table,
  Tabs,
  Typography,
  Space,
  Tag,
  Progress,
  Statistic,
  Spin,
  Divider,
  Empty,
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface BacktestConfig {
  strategy: string;
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
}

interface BacktestResult {
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
  avgTrade: number;
  bestTrade: number;
  worstTrade: number;
}

interface Trade {
  id: string;
  entryTime: string;
  exitTime: string;
  symbol: string;
  side: 'long' | 'short';
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  pnlPercent: number;
  duration: string;
}

const BacktestPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BacktestResult | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [activeTab, setActiveTab] = useState('config');

  // 删除虚假的模拟数据，改为真实的API调用

  const runBacktest = async () => {
    try {
      const values = await form.validateFields();
      setBacktestRunning(true);
      setProgress(0);
      setActiveTab('results');

      // TODO: 实现真实的回测API调用
      // 这里应该调用后端API进行真实的回测
      console.log('回测配置:', values);
      
      // 临时模拟进度，实际应该通过WebSocket或轮询获取真实进度
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            setBacktestRunning(false);
            // 实际应该从API获取真实结果
            // setResults(apiResults);
            // setTrades(apiTrades);
            return 100;
          }
          return prev + 10;
        });
      }, 500);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const stopBacktest = () => {
    setBacktestRunning(false);
    setProgress(0);
  };

  const resetBacktest = () => {
    setResults(null);
    setTrades([]);
    setProgress(0);
    setActiveTab('config');
  };

  // 权益曲线图表配置 - 基于真实数据
  const getEquityCurveOption = () => {
    if (!results) {
      return null;
    }
    
    return {
      title: {
        text: '权益曲线',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>权益: $${data.value.toLocaleString()}`;
        },
      },
      xAxis: {
        type: 'category',
        data: [], // 实际应该从回测结果获取日期数据
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '${value}',
        },
      },
      series: [
        {
          data: [], // 实际应该从回测结果获取权益数据
          type: 'line',
          smooth: true,
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
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
    };
  };

  // 回撤图表配置 - 基于真实数据
  const getDrawdownOption = () => {
    if (!results) {
      return null;
    }
    
    return {
      title: {
        text: '回撤分析',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>回撤: ${data.value}%`;
        },
      },
      xAxis: {
        type: 'category',
        data: [], // 实际应该从回测结果获取日期数据
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%',
        },
        max: 0,
      },
      series: [
        {
          data: [], // 实际应该从回测结果获取回撤数据
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#ff4d4f',
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
        bottom: '3%',
        containLabel: true,
      },
    };
  };

  const tradeColumns = [
    {
      title: '入场时间',
      dataIndex: 'entryTime',
      key: 'entryTime',
      width: 150,
    },
    {
      title: '出场时间',
      dataIndex: 'exitTime',
      key: 'exitTime',
      width: 150,
    },
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 80,
      render: (side: 'long' | 'short') => (
        <Tag color={side === 'long' ? 'green' : 'red'}>
          {side === 'long' ? '做多' : '做空'}
        </Tag>
      ),
    },
    {
      title: '入场价',
      dataIndex: 'entryPrice',
      key: 'entryPrice',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '出场价',
      dataIndex: 'exitPrice',
      key: 'exitPrice',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      width: 100,
      render: (value: number) => (
        <Text type={value >= 0 ? 'success' : 'danger'}>
          {value >= 0 ? '+' : ''}${value.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '盈亏%',
      dataIndex: 'pnlPercent',
      key: 'pnlPercent',
      width: 80,
      render: (value: number) => (
        <Text type={value >= 0 ? 'success' : 'danger'}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </Text>
      ),
    },
    {
      title: '持仓时间',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
    },
  ];

  return (
    <div style={{ padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>策略回测</Title>
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={runBacktest}
            loading={backtestRunning}
            disabled={backtestRunning}
          >
            开始回测
          </Button>
          <Button
            icon={<PauseCircleOutlined />}
            onClick={stopBacktest}
            disabled={!backtestRunning}
          >
            停止回测
          </Button>
          <Button icon={<ReloadOutlined />} onClick={resetBacktest}>
            重置
          </Button>
          <Button icon={<DownloadOutlined />} disabled={!results}>
            导出报告
          </Button>
        </Space>
      </div>

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'config',
            label: '回测配置',
            children: (
              <Card>
                <Form
                  form={form}
                  layout="vertical"
                  initialValues={{
                    strategy: 'atr_grid',
                    symbol: 'ETHUSDT',
                    timeframe: '1h',
                    startDate: dayjs().subtract(1, 'year'),
                    endDate: dayjs(),
                    initialCapital: 100000,
                    commission: 0.001,
                    slippage: 0.0005,
                    atrPeriod: 14,
                    gridMultiplier: 1.5,
                    maxPositions: 5,
                  }}
                >
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="策略类型"
                        name="strategy"
                        rules={[{ required: true, message: '请选择策略类型' }]}
                      >
                        <Select>
                          <Option value="atr_grid">ATR网格策略</Option>
                          <Option value="mean_reversion">均值回归策略</Option>
                          <Option value="momentum">动量策略</Option>
                          <Option value="arbitrage">套利策略</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="交易对"
                        name="symbol"
                        rules={[{ required: true, message: '请选择交易对' }]}
                      >
                        <Select>
                          <Option value="ETHUSDT">ETH/USDT</Option>
                          <Option value="BTCUSDT">BTC/USDT</Option>
                          <Option value="ADAUSDT">ADA/USDT</Option>
                          <Option value="DOTUSDT">DOT/USDT</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="时间周期"
                        name="timeframe"
                        rules={[{ required: true, message: '请选择时间周期' }]}
                      >
                        <Select>
                          <Option value="1m">1分钟</Option>
                          <Option value="5m">5分钟</Option>
                          <Option value="15m">15分钟</Option>
                          <Option value="1h">1小时</Option>
                          <Option value="4h">4小时</Option>
                          <Option value="1d">1天</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="回测时间范围"
                        name="dateRange"
                        rules={[{ required: true, message: '请选择回测时间范围' }]}
                      >
                        <RangePicker style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="初始资金"
                        name="initialCapital"
                        rules={[{ required: true, message: '请输入初始资金' }]}
                      >
                        <InputNumber
                          style={{ width: '100%' }}
                          min={1000}
                          max={10000000}
                          formatter={(value) => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                          parser={(value) => value!.replace(/\$\s?|(,*)/g, '')}
                        />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item
                        label="手续费率"
                        name="commission"
                        rules={[{ required: true, message: '请输入手续费率' }]}
                      >
                        <InputNumber
                          style={{ width: '100%' }}
                          min={0}
                          max={0.01}
                          step={0.0001}
                          formatter={(value) => `${(Number(value) * 100).toFixed(2)}%`}
                          parser={(value) => (Number(value!.replace('%', '')) / 100).toString()}
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Divider>策略参数</Divider>

                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item label="ATR周期" name="atrPeriod">
                        <InputNumber style={{ width: '100%' }} min={1} max={100} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item label="网格间距倍数" name="gridMultiplier">
                        <InputNumber style={{ width: '100%' }} min={0.1} max={5} step={0.1} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12} lg={8}>
                      <Form.Item label="最大持仓数" name="maxPositions">
                        <InputNumber style={{ width: '100%' }} min={1} max={20} />
                      </Form.Item>
                    </Col>
                  </Row>
                </Form>
              </Card>
            )
          },

          {
            key: 'results',
            label: '回测结果',
            children: (
              <>
                {backtestRunning && (
                  <Card style={{ marginBottom: '16px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <Spin size="large" />
                      <div style={{ marginTop: '16px', marginBottom: '16px' }}>
                        <Text>回测进行中...</Text>
                      </div>
                      <Progress percent={progress} status="active" />
                    </div>
                  </Card>
                )}

                {results && (
                  <>
                    <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic
                            title="总收益率"
                            value={results.totalReturn}
                            precision={2}
                            valueStyle={{ color: results.totalReturn >= 0 ? '#3f8600' : '#cf1322' }}
                            suffix="%"
                          />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic
                            title="年化收益率"
                            value={results.annualizedReturn}
                            precision={2}
                            valueStyle={{ color: results.annualizedReturn >= 0 ? '#3f8600' : '#cf1322' }}
                            suffix="%"
                          />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic
                            title="夏普比率"
                            value={results.sharpeRatio}
                            precision={2}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic
                            title="最大回撤"
                            value={Math.abs(results.maxDrawdown)}
                            precision={2}
                            valueStyle={{ color: '#cf1322' }}
                            suffix="%"
                          />
                        </Card>
                      </Col>
                    </Row>

                    <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                      <Col xs={24} lg={12}>
                        <Card title="权益曲线">
                          {getEquityCurveOption() ? (
                            <ReactECharts option={getEquityCurveOption()} style={{ height: '300px' }} />
                          ) : (
                            <Empty description="权益曲线数据开发中" style={{ height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
                          )}
                        </Card>
                      </Col>
                      <Col xs={24} lg={12}>
                        <Card title="回撤分析">
                          {getDrawdownOption() ? (
                            <ReactECharts option={getDrawdownOption()} style={{ height: '300px' }} />
                          ) : (
                            <Empty description="回撤分析数据开发中" style={{ height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
                          )}
                        </Card>
                      </Col>
                    </Row>

                    <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic title="胜率" value={results.winRate} precision={1} suffix="%" />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic title="盈利因子" value={results.profitFactor} precision={2} />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic title="总交易次数" value={results.totalTrades} />
                        </Card>
                      </Col>
                      <Col xs={24} sm={12} lg={6}>
                        <Card>
                          <Statistic title="平均每笔" value={results.avgTrade} precision={2} suffix="%" />
                        </Card>
                      </Col>
                    </Row>
                  </>
                )}
              </>
            )
          },
          {
            key: 'trades',
            label: '交易明细',
            children: (
              trades.length > 0 ? (
                <Card>
                  <Table
                    columns={tradeColumns}
                    dataSource={trades}
                    rowKey="id"
                    scroll={{ x: 1000 }}
                    pagination={{
                      pageSize: 20,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total) => `共 ${total} 条交易记录`,
                    }}
                  />
                </Card>
              ) : (
                <Card>
                  <div style={{ textAlign: 'center', padding: '50px 0' }}>
                    <Text type="secondary">暂无交易记录，请先运行回测</Text>
                  </div>
                </Card>
              )
            )
          }
        ]}
      />
    </div>
  );
};

export default BacktestPage;