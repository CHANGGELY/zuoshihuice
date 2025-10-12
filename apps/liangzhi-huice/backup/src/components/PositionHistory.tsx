import React, { useState, useMemo } from 'react';
import { Card, Table, Tag, Button, Select, DatePicker, Space, Statistic, Row, Col } from 'antd';
import { FilterOutlined, DownloadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import type { ColumnsType } from 'antd/es/table';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface TradeRecord {
  id: string;
  timestamp: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'open_long' | 'close_long' | 'open_short' | 'close_short';
  price: number;
  amount: number;
  fee: number;
  pnl?: number;
  totalValue: number;
  status: 'filled' | 'pending' | 'cancelled';
}

interface PositionHistoryProps {
  trades: TradeRecord[];
  loading?: boolean;
}

const PositionHistory: React.FC<PositionHistoryProps> = ({ trades, loading = false }) => {
  const [filterType, setFilterType] = useState<string>('all');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('all');

  // 过滤和统计数据
  const { filteredTrades, statistics } = useMemo(() => {
    let filtered = [...trades];

    // 按交易类型过滤
    if (filterType !== 'all') {
      filtered = filtered.filter(trade => trade.type === filterType);
    }

    // 按交易对过滤
    if (selectedSymbol !== 'all') {
      filtered = filtered.filter(trade => trade.symbol === selectedSymbol);
    }

    // 按日期范围过滤
    if (dateRange) {
      const [start, end] = dateRange;
      filtered = filtered.filter(trade => {
        const tradeDate = dayjs(trade.timestamp);
        return tradeDate.isAfter(start) && tradeDate.isBefore(end);
      });
    }

    // 计算统计数据
    const totalTrades = filtered.length;
    const totalPnl = filtered.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
    const totalFees = filtered.reduce((sum, trade) => sum + trade.fee, 0);
    const winningTrades = filtered.filter(trade => (trade.pnl || 0) > 0).length;
    const losingTrades = filtered.filter(trade => (trade.pnl || 0) < 0).length;
    const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;

    const stats = {
      totalTrades,
      totalPnl,
      totalFees,
      winningTrades,
      losingTrades,
      winRate
    };

    return { filteredTrades: filtered, statistics: stats };
  }, [trades, filterType, dateRange, selectedSymbol]);

  // 获取唯一的交易对列表
  const symbols = useMemo(() => {
    const uniqueSymbols = Array.from(new Set(trades.map(trade => trade.symbol)));
    return uniqueSymbols;
  }, [trades]);

  // 表格列定义
  const columns: ColumnsType<TradeRecord> = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 150,
      render: (timestamp: string) => (
        <div>
          <div>{dayjs(timestamp).format('MM-DD')}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {dayjs(timestamp).format('HH:mm:ss')}
          </div>
        </div>
      ),
      sorter: (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      defaultSortOrder: 'descend'
    },
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => (
        <Tag color="blue">{symbol}</Tag>
      )
    },
    {
      title: '操作类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const typeConfig = {
          'open_long': { color: 'green', text: '开多' },
          'close_long': { color: 'lime', text: '平多' },
          'open_short': { color: 'red', text: '开空' },
          'close_short': { color: 'pink', text: '平空' }
        };
        const config = typeConfig[type as keyof typeof typeConfig] || { color: 'default', text: type };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 120,
      render: (price: number) => (
        <span style={{ fontFamily: 'monospace' }}>
          ${price.toFixed(4)}
        </span>
      ),
      sorter: (a, b) => a.price - b.price
    },
    {
      title: '数量',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (amount: number) => (
        <span style={{ fontFamily: 'monospace' }}>
          {amount.toFixed(6)}
        </span>
      ),
      sorter: (a, b) => a.amount - b.amount
    },
    {
      title: '手续费',
      dataIndex: 'fee',
      key: 'fee',
      width: 100,
      render: (fee: number) => (
        <span style={{ fontFamily: 'monospace', color: '#ff4d4f' }}>
          -${fee.toFixed(4)}
        </span>
      )
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      width: 120,
      render: (pnl: number | undefined) => {
        if (pnl === undefined || pnl === 0) {
          return <span style={{ color: '#666' }}>-</span>;
        }
        const color = pnl > 0 ? '#52c41a' : '#ff4d4f';
        const prefix = pnl > 0 ? '+' : '';
        return (
          <span style={{ fontFamily: 'monospace', color, fontWeight: 'bold' }}>
            {prefix}${pnl.toFixed(4)}
          </span>
        );
      },
      sorter: (a, b) => (a.pnl || 0) - (b.pnl || 0)
    },
    {
      title: '总价值',
      dataIndex: 'totalValue',
      key: 'totalValue',
      width: 120,
      render: (totalValue: number) => (
        <span style={{ fontFamily: 'monospace' }}>
          ${totalValue.toFixed(2)}
        </span>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const statusConfig = {
          'filled': { color: 'success', text: '已成交' },
          'pending': { color: 'processing', text: '待成交' },
          'cancelled': { color: 'error', text: '已取消' }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    }
  ];

  // 导出数据
  const handleExport = () => {
    const csvContent = [
      ['时间', '交易对', '操作类型', '价格', '数量', '手续费', '盈亏', '总价值', '状态'].join(','),
      ...filteredTrades.map(trade => [
        dayjs(trade.timestamp).format('YYYY-MM-DD HH:mm:ss'),
        trade.symbol,
        trade.type,
        trade.price,
        trade.amount,
        trade.fee,
        trade.pnl || 0,
        trade.totalValue,
        trade.status
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `position_history_${dayjs().format('YYYY-MM-DD')}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Card 
      title="持仓历史"
      extra={
        <Space>
          <Button 
            icon={<DownloadOutlined />} 
            onClick={handleExport}
            size="small"
          >
            导出
          </Button>
        </Space>
      }
    >
      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Statistic 
            title="总交易数" 
            value={statistics.totalTrades} 
            valueStyle={{ fontSize: '16px' }}
          />
        </Col>
        <Col span={4}>
          <Statistic 
            title="总盈亏" 
            value={statistics.totalPnl} 
            precision={2}
            prefix="$"
            valueStyle={{ 
              fontSize: '16px',
              color: statistics.totalPnl >= 0 ? '#52c41a' : '#ff4d4f'
            }}
          />
        </Col>
        <Col span={4}>
          <Statistic 
            title="总手续费" 
            value={statistics.totalFees} 
            precision={4}
            prefix="$"
            valueStyle={{ fontSize: '16px', color: '#ff4d4f' }}
          />
        </Col>
        <Col span={4}>
          <Statistic 
            title="胜率" 
            value={statistics.winRate} 
            precision={1}
            suffix="%"
            valueStyle={{ fontSize: '16px' }}
          />
        </Col>
        <Col span={4}>
          <Statistic 
            title="盈利交易" 
            value={statistics.winningTrades} 
            valueStyle={{ fontSize: '16px', color: '#52c41a' }}
          />
        </Col>
        <Col span={4}>
          <Statistic 
            title="亏损交易" 
            value={statistics.losingTrades} 
            valueStyle={{ fontSize: '16px', color: '#ff4d4f' }}
          />
        </Col>
      </Row>

      {/* 过滤器 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Select
            placeholder="选择操作类型"
            value={filterType}
            onChange={setFilterType}
            style={{ width: '100%' }}
            allowClear
          >
            <Option value="all">全部类型</Option>
            <Option value="open_long">开多</Option>
            <Option value="close_long">平多</Option>
            <Option value="open_short">开空</Option>
            <Option value="close_short">平空</Option>
          </Select>
        </Col>
        <Col span={6}>
          <Select
            placeholder="选择交易对"
            value={selectedSymbol}
            onChange={setSelectedSymbol}
            style={{ width: '100%' }}
            allowClear
          >
            <Option value="all">全部交易对</Option>
            {symbols.map(symbol => (
              <Option key={symbol} value={symbol}>{symbol}</Option>
            ))}
          </Select>
        </Col>
        <Col span={12}>
          <RangePicker
            value={dateRange}
            onChange={setDateRange}
            showTime
            style={{ width: '100%' }}
            placeholder={['开始时间', '结束时间']}
          />
        </Col>
      </Row>

      {/* 交易记录表格 */}
      <Table
        columns={columns}
        dataSource={filteredTrades}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => 
            `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
        }}
        scroll={{ x: 1000 }}
        size="small"
      />
    </Card>
  );
};

export default PositionHistory;