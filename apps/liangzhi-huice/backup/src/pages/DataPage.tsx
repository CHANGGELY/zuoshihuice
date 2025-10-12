import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Table,
  Upload,
  Progress,
  Typography,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  message,
  Tabs,
  Statistic,
  Alert,
  Popconfirm,
  Tooltip,
} from 'antd';
import DataImport from '../components/DataImport';
import {
  UploadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  CloudUploadOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import type { UploadProps } from 'antd';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;
const { Dragger } = Upload;

interface DataFile {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  records: number;
  size: string;
  format: string;
  status: 'imported' | 'importing' | 'failed' | 'pending';
  progress?: number;
  createdAt: string;
}

interface DataStats {
  totalFiles: number;
  totalRecords: number;
  totalSize: string;
  symbols: string[];
  timeframes: string[];
  dateRange: {
    start: string;
    end: string;
  };
}

const DataPage: React.FC = () => {
  const [dataFiles, setDataFiles] = useState<DataFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [previewModalVisible, setPreviewModalVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState<DataFile | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('files');
  const [dataStats, setDataStats] = useState<DataStats | null>(null);

  // 模拟数据文件
  const mockDataFiles: DataFile[] = [
    {
      id: '1',
      name: 'ETHUSDT_1m_2019-11-01_to_2025-06-15.h5',
      symbol: 'ETHUSDT',
      timeframe: '1m',
      startDate: '2019-11-01',
      endDate: '2025-06-15',
      records: 2856432,
      size: '245.6 MB',
      format: 'H5',
      status: 'imported',
      createdAt: '2024-01-15 10:30:00',
    },
    {
      id: '2',
      name: 'BTCUSDT_1h_2020-01-01_to_2024-12-31.csv',
      symbol: 'BTCUSDT',
      timeframe: '1h',
      startDate: '2020-01-01',
      endDate: '2024-12-31',
      records: 43824,
      size: '12.3 MB',
      format: 'CSV',
      status: 'imported',
      createdAt: '2024-01-14 15:20:00',
    },
    {
      id: '3',
      name: 'ADAUSDT_5m_2023-01-01_to_2024-01-01.json',
      symbol: 'ADAUSDT',
      timeframe: '5m',
      startDate: '2023-01-01',
      endDate: '2024-01-01',
      records: 105120,
      size: '28.7 MB',
      format: 'JSON',
      status: 'importing',
      progress: 65,
      createdAt: '2024-01-13 09:15:00',
    },
  ];

  const mockDataStats: DataStats = {
    totalFiles: 3,
    totalRecords: 3005376,
    totalSize: '286.6 MB',
    symbols: ['ETHUSDT', 'BTCUSDT', 'ADAUSDT'],
    timeframes: ['1m', '5m', '1h'],
    dateRange: {
      start: '2019-11-01',
      end: '2025-06-15',
    },
  };

  useEffect(() => {
    setDataFiles(mockDataFiles);
    setDataStats(mockDataStats);
  }, []);

  const handleUpload = () => {
    setUploadModalVisible(true);
  };

  const handlePreview = (file: DataFile) => {
    setSelectedFile(file);
    setPreviewModalVisible(true);
  };

  const handleDelete = (id: string) => {
    setDataFiles(dataFiles.filter(f => f.id !== id));
    message.success('数据文件删除成功');
  };

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      message.success('数据刷新完成');
    }, 1000);
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: '.csv,.json,.h5,.parquet',
    action: '/api/data/upload',
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        message.success(`${info.file.name} 文件上传成功`);
      } else if (status === 'error') {
        message.error(`${info.file.name} 文件上传失败`);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  const getStatusTag = (status: DataFile['status']) => {
    const statusConfig = {
      imported: { color: 'green', text: '已导入' },
      importing: { color: 'blue', text: '导入中' },
      failed: { color: 'red', text: '失败' },
      pending: { color: 'orange', text: '待处理' },
    };
    const config = statusConfig[status];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      width: 300,
      render: (text: string, record: DataFile) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.symbol} · {record.timeframe} · {record.format}
          </div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: DataFile['status'], record: DataFile) => (
        <div>
          {getStatusTag(status)}
          {status === 'importing' && record.progress && (
            <Progress percent={record.progress} size="small" style={{ marginTop: '4px' }} />
          )}
        </div>
      ),
    },
    {
      title: '时间范围',
      key: 'dateRange',
      width: 200,
      render: (_, record: DataFile) => (
        <div>
          <div>{record.startDate}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>至 {record.endDate}</div>
        </div>
      ),
    },
    {
      title: '记录数',
      dataIndex: 'records',
      key: 'records',
      width: 120,
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: '文件大小',
      dataIndex: 'size',
      key: 'size',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record: DataFile) => (
        <Space size="small">
          <Tooltip title="预览数据">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(record)}
              disabled={record.status !== 'imported'}
            />
          </Tooltip>
          <Tooltip title="下载文件">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              disabled={record.status !== 'imported'}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个数据文件吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除文件">
              <Button type="text" icon={<DeleteOutlined />} danger />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 数据分布图表配置
  const dataDistributionOption = {
    title: {
      text: '数据分布统计',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '交易对分布',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 2856432, name: 'ETHUSDT' },
          { value: 43824, name: 'BTCUSDT' },
          { value: 105120, name: 'ADAUSDT' },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };

  // 时间分布图表配置
  const timeDistributionOption = {
    title: {
      text: '时间周期分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: ['1分钟', '5分钟', '1小时'],
    },
    yAxis: {
      type: 'value',
      name: '记录数',
    },
    series: [
      {
        data: [2856432, 105120, 43824],
        type: 'bar',
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

  // 模拟预览数据
  const previewData = [
    {
      timestamp: '2024-01-15 09:30:00',
      open: 2456.78,
      high: 2467.89,
      low: 2445.23,
      close: 2461.45,
      volume: 1234567,
    },
    {
      timestamp: '2024-01-15 09:31:00',
      open: 2461.45,
      high: 2478.90,
      low: 2458.12,
      close: 2475.33,
      volume: 987654,
    },
    {
      timestamp: '2024-01-15 09:32:00',
      open: 2475.33,
      high: 2482.67,
      low: 2471.89,
      close: 2479.56,
      volume: 1567890,
    },
  ];

  const previewColumns = [
    {
      title: '时间戳',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 150,
    },
    {
      title: '开盘价',
      dataIndex: 'open',
      key: 'open',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '最高价',
      dataIndex: 'high',
      key: 'high',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '最低价',
      dataIndex: 'low',
      key: 'low',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '收盘价',
      dataIndex: 'close',
      key: 'close',
      width: 100,
      render: (value: number) => `$${value.toFixed(2)}`,
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      render: (value: number) => value.toLocaleString(),
    },
  ];

  return (
    <div style={{ padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>数据管理</Title>
        <Space>
          <Button type="primary" icon={<UploadOutlined />} onClick={handleUpload}>
            导入数据
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            刷新
          </Button>
          <Button icon={<SyncOutlined />}>
            同步数据
          </Button>
        </Space>
      </div>

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'files',
            label: '数据文件',
            children: (
              <>
                {dataStats && (
                  <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                    <Col xs={24} sm={6}>
                      <Card>
                        <Statistic
                          title="总文件数"
                          value={dataStats.totalFiles}
                          prefix={<DatabaseOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Card>
                        <Statistic
                          title="总记录数"
                          value={dataStats.totalRecords}
                          prefix={<FileTextOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Card>
                        <Statistic
                          title="总大小"
                          value={dataStats.totalSize}
                          prefix={<CloudUploadOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Card>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                            {dataStats.symbols.length}
                          </div>
                          <div style={{ color: '#666' }}>交易对数量</div>
                        </div>
                      </Card>
                    </Col>
                  </Row>
                )}

                <Card>
                  <Table
                    columns={columns}
                    dataSource={dataFiles}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1200 }}
                    pagination={{
                      pageSize: 10,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total) => `共 ${total} 个数据文件`,
                    }}
                  />
                </Card>
              </>
            )
          },
          {
            key: 'import',
            label: '数据导入',
            children: <DataImport />
          },
          {
            key: 'stats',
            label: '数据统计',
            children: (
              <>
                <Row gutter={[16, 16]}>
                  <Col xs={24} lg={12}>
                    <Card>
                      <ReactECharts option={dataDistributionOption} style={{ height: '300px' }} />
                    </Card>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Card>
                      <ReactECharts option={timeDistributionOption} style={{ height: '300px' }} />
                    </Card>
                  </Col>
                </Row>

                {dataStats && (
                  <Card style={{ marginTop: '16px' }}>
                    <Title level={4}>数据概览</Title>
                    <Row gutter={[16, 16]}>
                      <Col xs={24} sm={12}>
                        <div>
                          <Text strong>支持的交易对：</Text>
                          <div style={{ marginTop: '8px' }}>
                            {dataStats.symbols.map(symbol => (
                              <Tag key={symbol} color="blue">{symbol}</Tag>
                            ))}
                          </div>
                        </div>
                      </Col>
                      <Col xs={24} sm={12}>
                        <div>
                          <Text strong>支持的时间周期：</Text>
                          <div style={{ marginTop: '8px' }}>
                            {dataStats.timeframes.map(tf => (
                              <Tag key={tf} color="green">{tf}</Tag>
                            ))}
                          </div>
                        </div>
                      </Col>
                      <Col xs={24}>
                        <div>
                          <Text strong>数据时间范围：</Text>
                          <div style={{ marginTop: '8px' }}>
                            <Tag color="orange">{dataStats.dateRange.start}</Tag>
                            <span style={{ margin: '0 8px' }}>至</span>
                            <Tag color="orange">{dataStats.dateRange.end}</Tag>
                          </div>
                        </div>
                      </Col>
                    </Row>
                  </Card>
                )}
              </>
            )
          }
        ]}
      />

      {/* 上传数据模态框 */}
      <Modal
        title="导入数据文件"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={600}
      >
        <Alert
          message="支持的文件格式"
          description="支持 CSV、JSON、H5、Parquet 格式的K线数据文件。文件应包含时间戳、开盘价、最高价、最低价、收盘价、成交量等字段。"
          type="info"
          style={{ marginBottom: '16px' }}
        />
        
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <UploadOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。严禁上传公司数据或其他敏感文件。
          </p>
        </Dragger>

        <Form
          form={form}
          layout="vertical"
          style={{ marginTop: '24px' }}
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12}>
              <Form.Item label="交易对" name="symbol">
                <Select placeholder="请选择交易对">
                  <Option value="ETHUSDT">ETH/USDT</Option>
                  <Option value="BTCUSDT">BTC/USDT</Option>
                  <Option value="ADAUSDT">ADA/USDT</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item label="时间周期" name="timeframe">
                <Select placeholder="请选择时间周期">
                  <Option value="1m">1分钟</Option>
                  <Option value="5m">5分钟</Option>
                  <Option value="15m">15分钟</Option>
                  <Option value="1h">1小时</Option>
                  <Option value="4h">4小时</Option>
                  <Option value="1d">1天</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 数据预览模态框 */}
      <Modal
        title={`数据预览 - ${selectedFile?.name}`}
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedFile && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <Space>
                <Tag color="blue">{selectedFile.symbol}</Tag>
                <Tag color="green">{selectedFile.timeframe}</Tag>
                <Tag color="orange">{selectedFile.format}</Tag>
                <Text type="secondary">共 {selectedFile.records.toLocaleString()} 条记录</Text>
              </Space>
            </div>
            
            <Table
              columns={previewColumns}
              dataSource={previewData}
              rowKey="timestamp"
              size="small"
              pagination={false}
              scroll={{ x: 600 }}
            />
            
            <div style={{ textAlign: 'center', marginTop: '16px' }}>
              <Text type="secondary">仅显示前3条记录作为预览</Text>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DataPage;