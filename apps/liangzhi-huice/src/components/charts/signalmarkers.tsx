// SignalMarkers 交易信号标记组件

import React, { useMemo, useCallback } from 'react';
import { Card, Table, Tag, Button, Space, Select, DatePicker, Input } from 'antd';
import {
  DownloadOutlined,
  EyeOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useKlineStore } from '../../stores';
import { TradingSignal, SignalType } from '../../types/kline';
// import { TableLoading } from '../common/Loading';
import { formatPrice, formatTime, formatStrength } from '../../utils/format';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { Search } = Input;

// 信号标记组件属性
interface SignalMarkersProps {
  // 交易信号数据
  signals?: TradingSignal[];
  // 是否显示在图表上
  showOnChart?: boolean;
  // 是否显示表格
  showTable?: boolean;
  // 是否显示过滤器
  showFilters?: boolean;
  // 是否显示下载按钮
  showDownload?: boolean;
  // 表格高度
  tableHeight?: number;
  // 自定义样式
  style?: React.CSSProperties;
  // 是否可以编辑信号
  editable?: boolean;
  // 信号点击回调
  onSignalClick?: (signal: TradingSignal) => void;
}

// 信号过滤器
interface SignalFilter {
  type?: SignalType;
  dateRange?: [string, string];
  priceRange?: [number, number];
  searchText?: string;
}

// 获取信号颜色
const getSignalColor = (type: SignalType): string => {
  switch (type) {
    case SignalType.BUY:
      return '#52c41a';
    case SignalType.SELL:
      return '#ff4d4f';
    case SignalType.CLOSE_BUY:
    case SignalType.CLOSE_SELL:
      return '#1890ff';
    default:
      return '#666';
  }
};

// 获取信号图标
const getSignalIcon = (type: SignalType): React.ReactNode => {
  switch (type) {
    case SignalType.BUY:
      return <ArrowUpOutlined style={{ color: '#52c41a' }} />;
    case SignalType.SELL:
      return <ArrowDownOutlined style={{ color: '#ff4d4f' }} />;
    case SignalType.CLOSE_BUY:
    case SignalType.CLOSE_SELL:
      return <EyeOutlined style={{ color: '#1890ff' }} />;
    default:
      return null;
  }
};

// 单个信号标记组件（暂未使用）
// const SignalMarker: React.FC<{
//   signal: TradingSignal;
//   onClick?: (signal: TradingSignal) => void;
// }> = ({ signal, onClick }) => {
//   const handleClick = useCallback(() => {
//     onClick?.(signal);
//   }, [signal, onClick]);
//
//   return (
//     <Tooltip
//       title={
//         <div>
//           <div>类型: {signal.type}</div>
//           <div>价格: {formatPrice(signal.price)}</div>
//           <div>时间: {formatTime(signal.timestamp)}</div>
//           <div>强度: {formatStrength(signal.strength)}</div>
//           {signal.reason && <div>原因: {signal.reason}</div>}
//         </div>
//       }
//     >
//       <div
//         onClick={handleClick}
//         style={{
//           position: 'absolute',
//           width: '12px',
//           height: '12px',
//           borderRadius: '50%',
//           backgroundColor: getSignalColor(signal.type),
//           border: '2px solid #fff',
//           cursor: onClick ? 'pointer' : 'default',
//           boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
//           zIndex: 10,
//         }}
//       />
//     </Tooltip>
//   );
// };

// 信号表格组件
const SignalTable: React.FC<{
  signals: TradingSignal[];
  loading: boolean;
  height?: number;
  onSignalClick?: (signal: TradingSignal) => void;
}> = ({ signals, loading, height = 400, onSignalClick }) => {
  const [filter, setFilter] = React.useState<SignalFilter>({});
  const [pagination, setPagination] = React.useState({ current: 1, pageSize: 50 });

  // 过滤信号数据
  const filteredSignals = useMemo(() => {
    if (!Array.isArray(signals)) {
      return [];
    }

    let filtered = [...signals];

    // 按类型过滤
    if (filter.type) {
      filtered = filtered.filter(signal => signal.type === filter.type);
    }

    // 按时间范围过滤
    if (filter.dateRange) {
      const [start, end] = filter.dateRange;
      const startTime = new Date(start).getTime();
      const endTime = new Date(end).getTime();
      filtered = filtered.filter(
        signal => signal.timestamp >= startTime && signal.timestamp <= endTime
      );
    }

    // 按价格范围过滤
    if (filter.priceRange) {
      const [minPrice, maxPrice] = filter.priceRange;
      filtered = filtered.filter(
        signal => signal.price && signal.price >= minPrice && signal.price <= maxPrice
      );
    }

    // 按搜索文本过滤
    if (filter.searchText) {
      const searchText = filter.searchText.toLowerCase();
      filtered = filtered.filter(
        signal =>
          signal.type?.toLowerCase().includes(searchText) ||
          signal.reason?.toLowerCase().includes(searchText)
      );
    }

    return filtered.sort((a, b) => b.timestamp - a.timestamp);
  }, [signals, filter]);

  // 表格列定义
  const columns: ColumnsType<TradingSignal> = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: number) => formatTime(timestamp),
      sorter: (a, b) => a.timestamp - b.timestamp,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: SignalType) => (
        <Tag color={getSignalColor(type)} icon={getSignalIcon(type)}>
          {type}
        </Tag>
      ),
      filters: [
        { text: 'BUY', value: SignalType.BUY },
        { text: 'SELL', value: SignalType.SELL },
        { text: 'CLOSE_BUY', value: SignalType.CLOSE_BUY },
        { text: 'CLOSE_SELL', value: SignalType.CLOSE_SELL },
      ],
      onFilter: (value: boolean | React.Key, record: TradingSignal) => record.type === value,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 120,
      render: (price: number | undefined) => formatPrice(price),
      sorter: (a, b) => {
        const priceA = Number(a.price) || 0;
        const priceB = Number(b.price) || 0;
        return priceA - priceB;
      },
    },
    {
      title: '强度',
      dataIndex: 'strength',
      key: 'strength',
      width: 100,
      render: (strength: number | undefined) => {
        return formatStrength(strength);
      },
      sorter: (a, b) => {
        const strengthA = Number(a.strength) || 0;
        const strengthB = Number(b.strength) || 0;
        return strengthA - strengthB;
      },
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      render: (volume?: number) => (volume ? volume.toLocaleString() : '-'),
      sorter: (a, b) => (a.volume || 0) - (b.volume || 0),
    },
    {
      title: '原因',
      dataIndex: 'reason',
      key: 'reason',
      ellipsis: true,
      render: (reason?: string) => reason || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            size="small"
            onClick={() => onSignalClick?.(record)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="选择信号类型"
          style={{ width: 120 }}
          allowClear
          value={filter.type}
          onChange={(value) => setFilter(prev => ({ ...prev, type: value }))}
        >
          <Option value={SignalType.BUY}>买入</Option>
          <Option value={SignalType.SELL}>卖出</Option>
          <Option value={SignalType.CLOSE_BUY}>平多</Option>
          <Option value={SignalType.CLOSE_SELL}>平空</Option>
        </Select>

        <RangePicker
          onChange={(dates, dateStrings) => {
            setFilter(prev => ({
              ...prev,
              dateRange: dates ? [dateStrings[0], dateStrings[1]] : undefined,
            }));
          }}
        />

        <Search
          placeholder="搜索原因"
          style={{ width: 200 }}
          onSearch={(value) => setFilter(prev => ({ ...prev, searchText: value }))}
          allowClear
        />
      </Space>

      <Table
        columns={columns}
        dataSource={filteredSignals}
        loading={loading}
        rowKey={(record) => `${record.timestamp}-${record.type}`}
        scroll={{ y: height }}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: filteredSignals.length,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `显示 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPagination({ current: page, pageSize: pageSize || 50 });
          },
        }}
      />
    </div>
  );
};

export const SignalMarkers: React.FC<SignalMarkersProps> = ({
  signals = [],
  showOnChart = true,
  showTable = true,
  showDownload = false,
  tableHeight = 400,
  style,
  onSignalClick,
}) => {
  const { tradingSignals, loadingState } = useKlineStore();

  // 使用传入的 signals 或 store 中的 signals
  const displaySignals = signals.length > 0 ? signals : tradingSignals;

  const handleDownload = useCallback(() => {
    if (!displaySignals || displaySignals.length === 0) {
      return;
    }

    const csvContent = displaySignals
      .map(signal => [
        formatTime(signal.timestamp),
        signal.type,
        formatPrice(signal.price),
        formatStrength(signal.strength),
        signal.volume || '',
        signal.reason || '',
      ])
      .map(row => row.join(','))
      .join('\n');

    const csvData = `时间,类型,价格,强度,成交量,原因\n${csvContent}`;
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'trading-signals.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, [displaySignals]);

  if (!showOnChart && !showTable) {
    return null;
  }

  return (
    <div style={style}>
      {showTable && (
        <Card
          title={
            <Space>
              <span>交易信号</span>
              {showDownload && (
                <Button
                  type="primary"
                  size="small"
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                  disabled={!displaySignals || displaySignals.length === 0}
                >
                  导出
                </Button>
              )}
            </Space>
          }
          size="small"
        >
          <SignalTable
            signals={displaySignals}
            loading={loadingState.isLoading}
            height={tableHeight}
            onSignalClick={onSignalClick}
          />
        </Card>
      )}
    </div>
  );
};

export default SignalMarkers;