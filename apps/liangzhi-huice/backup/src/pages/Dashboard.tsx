import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Typography,
  Alert,
  Spin,
  Empty,
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  LineChartOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';


const { Title, Text } = Typography;

interface PerformanceData {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  profitFactor: number;
}

interface RecentTrade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  pnl: number;
  time: string;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [recentTrades, setRecentTrades] = useState<RecentTrade[]>([]);

  useEffect(() => {
    // 实际应该从API获取数据
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // 渲染空状态的组件
  const renderEmptyState = (title: string, description?: string) => (
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      description={
        <div>
          <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>{title}</div>
          <div style={{ color: '#999' }}>{description || `暂无${title}数据，请运行回测以查看相关信息`}</div>
        </div>
      }
    />
  );

  const tradeColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (side: 'buy' | 'sell') => (
        <span style={{ color: side === 'buy' ? '#52c41a' : '#ff4d4f' }}>
          {side === 'buy' ? '买入' : '卖出'}
        </span>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value: number) => value.toFixed(2),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (value: number) => (
        <Text type={value >= 0 ? 'success' : 'danger'}>
          {value >= 0 ? '+' : ''}${value.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time',
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载仪表盘数据...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '0 16px' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        仪表盘
      </Title>

      <Alert
        message="量化交易系统"
        description="请运行回测以查看策略表现数据。"
        type="info"
        showIcon
        style={{ marginBottom: '24px' }}
      />

      {/* 关键指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            {performanceData ? (
              <Statistic
                title="总收益率"
                value={performanceData.totalReturn}
                precision={2}
                valueStyle={{ color: '#3f8600' }}
                prefix={<ArrowUpOutlined />}
                suffix="%"
              />
            ) : (
              <Statistic
                title="总收益率"
                value="--"
                valueStyle={{ color: '#999' }}
                prefix={<ArrowUpOutlined />}
                suffix="%"
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            {performanceData ? (
              <Statistic
                title="夏普比率"
                value={performanceData.sharpeRatio}
                precision={2}
                valueStyle={{ color: '#1890ff' }}
                prefix={<LineChartOutlined />}
              />
            ) : (
              <Statistic
                title="夏普比率"
                value="--"
                valueStyle={{ color: '#999' }}
                prefix={<LineChartOutlined />}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            {performanceData ? (
              <Statistic
                title="最大回撤"
                value={Math.abs(performanceData.maxDrawdown)}
                precision={2}
                valueStyle={{ color: '#cf1322' }}
                prefix={<ArrowDownOutlined />}
                suffix="%"
              />
            ) : (
              <Statistic
                title="最大回撤"
                value="--"
                valueStyle={{ color: '#999' }}
                prefix={<ArrowDownOutlined />}
                suffix="%"
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            {performanceData ? (
              <Statistic
                title="胜率"
                value={performanceData.winRate}
                precision={1}
                valueStyle={{ color: '#722ed1' }}
                prefix={<ThunderboltOutlined />}
                suffix="%"
              />
            ) : (
              <Statistic
                title="胜率"
                value="--"
                valueStyle={{ color: '#999' }}
                prefix={<ThunderboltOutlined />}
                suffix="%"
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 进度指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="交易统计" size="small">
            {performanceData ? (
              <div>
                <div>
                  <Text>总交易次数: {performanceData.totalTrades}</Text>
                </div>
                <div>
                  <Text>盈利因子: {performanceData.profitFactor}</Text>
                </div>
              </div>
            ) : (
              renderEmptyState('交易统计', '请运行回测以查看交易统计数据')
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="系统状态" size="small">
            {renderEmptyState('系统状态', '系统监控功能开发中')}
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="权益曲线">
            {performanceData ? (
              <div style={{ height: '300px' }}>
                {/* 这里将来会显示真实的权益曲线图表 */}
                <Empty description="权益曲线图表开发中" />
              </div>
            ) : (
              renderEmptyState('权益曲线', '请运行回测以查看权益曲线数据')
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="月度收益分布">
            {performanceData ? (
              <div style={{ height: '300px' }}>
                {/* 这里将来会显示真实的月度收益分布图表 */}
                <Empty description="月度收益分布图表开发中" />
              </div>
            ) : (
              renderEmptyState('月度收益分布', '请运行回测以查看月度收益数据')
            )}
          </Card>
        </Col>
      </Row>

      {/* K线图表 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24}>
          <Card title="历史K线数据" size="small">
            {renderEmptyState('历史K线数据', 'K线图表组件开发中')}
          </Card>
        </Col>
      </Row>

      {/* 最近交易 */}
      <Card title="最近交易" size="small">
        {recentTrades.length > 0 ? (
          <Table
            columns={tradeColumns}
            dataSource={recentTrades}
            pagination={false}
            size="small"
            rowKey="id"
          />
        ) : (
          renderEmptyState('最近交易', '暂无交易记录，请运行回测以查看交易数据')
        )}
      </Card>
    </div>
  );
};

export default Dashboard;