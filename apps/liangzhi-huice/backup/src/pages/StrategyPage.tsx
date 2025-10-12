import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Table,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Tag,
  Space,
  Typography,
  Popconfirm,
  message,
  Drawer,
  Descriptions,
  Tabs,
  Alert,
  Upload,
  Progress,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  EyeOutlined,
  CopyOutlined,
  UploadOutlined,
  DownloadOutlined,
  SettingOutlined,
  CodeOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

interface Strategy {
  id: string;
  name: string;
  type: string;
  description: string;
  status: 'active' | 'inactive' | 'running' | 'error';
  performance: {
    totalReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
  };
  parameters: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  author: string;
}

const StrategyPage: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [form] = Form.useForm();
  const [editMode, setEditMode] = useState(false);

  // 模拟策略数据
  const mockStrategies: Strategy[] = [
    {
      id: '1',
      name: 'ATR网格策略',
      type: 'grid',
      description: '基于ATR指标的动态网格交易策略，适用于震荡市场',
      status: 'active',
      performance: {
        totalReturn: 24.67,
        sharpeRatio: 1.85,
        maxDrawdown: -12.34,
        winRate: 65.8,
      },
      parameters: {
        atrPeriod: 14,
        gridMultiplier: 1.5,
        maxPositions: 5,
        riskPerTrade: 2,
      },
      createdAt: '2024-01-15',
      updatedAt: '2024-01-20',
      author: '系统内置',
    },
    {
      id: '2',
      name: '均值回归策略',
      type: 'mean_reversion',
      description: '基于价格偏离均值的回归特性进行交易',
      status: 'running',
      performance: {
        totalReturn: 18.92,
        sharpeRatio: 1.42,
        maxDrawdown: -8.76,
        winRate: 58.3,
      },
      parameters: {
        lookbackPeriod: 20,
        deviationThreshold: 2,
        exitThreshold: 0.5,
      },
      createdAt: '2024-01-10',
      updatedAt: '2024-01-18',
      author: '用户自定义',
    },
    {
      id: '3',
      name: '动量突破策略',
      type: 'momentum',
      description: '捕捉价格突破关键阻力位的动量机会',
      status: 'inactive',
      performance: {
        totalReturn: 31.45,
        sharpeRatio: 2.12,
        maxDrawdown: -15.67,
        winRate: 72.1,
      },
      parameters: {
        breakoutPeriod: 10,
        volumeConfirmation: true,
        stopLoss: 3,
        takeProfit: 6,
      },
      createdAt: '2024-01-05',
      updatedAt: '2024-01-12',
      author: '专家策略',
    },
  ];

  useEffect(() => {
    setStrategies(mockStrategies);
  }, []);

  const handleCreateStrategy = () => {
    setEditMode(false);
    setSelectedStrategy(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditStrategy = (strategy: Strategy) => {
    setEditMode(true);
    setSelectedStrategy(strategy);
    form.setFieldsValue({
      name: strategy.name,
      type: strategy.type,
      description: strategy.description,
      ...strategy.parameters,
    });
    setModalVisible(true);
  };

  const handleViewStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setDrawerVisible(true);
  };

  const handleDeleteStrategy = (id: string) => {
    setStrategies(strategies.filter(s => s.id !== id));
    message.success('策略删除成功');
  };

  const handleToggleStrategy = (id: string) => {
    setStrategies(strategies.map(s => {
      if (s.id === id) {
        const newStatus = s.status === 'active' ? 'inactive' : 'active';
        return { ...s, status: newStatus };
      }
      return s;
    }));
  };

  const handleRunStrategy = (id: string) => {
    setStrategies(strategies.map(s => {
      if (s.id === id) {
        return { ...s, status: 'running' };
      }
      return s;
    }));
    message.success('策略开始运行');
  };

  const handleStopStrategy = (id: string) => {
    setStrategies(strategies.map(s => {
      if (s.id === id) {
        return { ...s, status: 'active' };
      }
      return s;
    }));
    message.success('策略已停止');
  };

  const handleSaveStrategy = async () => {
    try {
      const values = await form.validateFields();
      
      if (editMode && selectedStrategy) {
        // 编辑现有策略
        setStrategies(strategies.map(s => {
          if (s.id === selectedStrategy.id) {
            return {
              ...s,
              name: values.name,
              type: values.type,
              description: values.description,
              parameters: {
                atrPeriod: values.atrPeriod,
                gridMultiplier: values.gridMultiplier,
                maxPositions: values.maxPositions,
                riskPerTrade: values.riskPerTrade,
              },
              updatedAt: new Date().toISOString().split('T')[0],
            };
          }
          return s;
        }));
        message.success('策略更新成功');
      } else {
        // 创建新策略
        const newStrategy: Strategy = {
          id: Date.now().toString(),
          name: values.name,
          type: values.type,
          description: values.description,
          status: 'inactive',
          performance: {
            totalReturn: 0,
            sharpeRatio: 0,
            maxDrawdown: 0,
            winRate: 0,
          },
          parameters: {
            atrPeriod: values.atrPeriod || 14,
            gridMultiplier: values.gridMultiplier || 1.5,
            maxPositions: values.maxPositions || 5,
            riskPerTrade: values.riskPerTrade || 2,
          },
          createdAt: new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString().split('T')[0],
          author: '用户自定义',
        };
        setStrategies([...strategies, newStrategy]);
        message.success('策略创建成功');
      }
      
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('保存策略失败:', error);
    }
  };

  const getStatusTag = (status: Strategy['status']) => {
    const statusConfig = {
      active: { color: 'green', text: '激活' },
      inactive: { color: 'default', text: '未激活' },
      running: { color: 'blue', text: '运行中' },
      error: { color: 'red', text: '错误' },
    };
    const config = statusConfig[status];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text: string, record: Strategy) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.type}</div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: Strategy['status']) => getStatusTag(status),
    },
    {
      title: '总收益率',
      dataIndex: ['performance', 'totalReturn'],
      key: 'totalReturn',
      width: 120,
      render: (value: number) => (
        <Text type={value >= 0 ? 'success' : 'danger'}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </Text>
      ),
    },
    {
      title: '夏普比率',
      dataIndex: ['performance', 'sharpeRatio'],
      key: 'sharpeRatio',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: '最大回撤',
      dataIndex: ['performance', 'maxDrawdown'],
      key: 'maxDrawdown',
      width: 120,
      render: (value: number) => (
        <Text type="danger">{value.toFixed(2)}%</Text>
      ),
    },
    {
      title: '胜率',
      dataIndex: ['performance', 'winRate'],
      key: 'winRate',
      width: 100,
      render: (value: number) => `${value.toFixed(1)}%`,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 120,
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: Strategy) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewStrategy(record)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditStrategy(record)}
          />
          {record.status === 'running' ? (
            <Button
              type="text"
              icon={<PauseCircleOutlined />}
              onClick={() => handleStopStrategy(record.id)}
            />
          ) : (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handleRunStrategy(record.id)}
              disabled={record.status === 'inactive'}
            />
          )}
          <Popconfirm
            title="确定要删除这个策略吗？"
            onConfirm={() => handleDeleteStrategy(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 性能图表配置
  const performanceOption = {
    title: {
      text: '策略性能对比',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      data: ['总收益率', '夏普比率', '胜率'],
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: strategies.map(s => s.name),
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: [
      {
        type: 'value',
        name: '收益率(%)',
        position: 'left',
      },
      {
        type: 'value',
        name: '比率',
        position: 'right',
      },
    ],
    series: [
      {
        name: '总收益率',
        type: 'bar',
        data: strategies.map(s => s.performance.totalReturn),
        itemStyle: {
          color: '#1890ff',
        },
      },
      {
        name: '夏普比率',
        type: 'line',
        yAxisIndex: 1,
        data: strategies.map(s => s.performance.sharpeRatio),
        itemStyle: {
          color: '#52c41a',
        },
      },
      {
        name: '胜率',
        type: 'line',
        yAxisIndex: 1,
        data: strategies.map(s => s.performance.winRate),
        itemStyle: {
          color: '#faad14',
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

  return (
    <div style={{ padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>策略管理</Title>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateStrategy}>
            创建策略
          </Button>
          <Button icon={<UploadOutlined />}>
            导入策略
          </Button>
          <Button icon={<DownloadOutlined />}>
            导出策略
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                {strategies.length}
              </div>
              <div style={{ color: '#666' }}>总策略数</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                {strategies.filter(s => s.status === 'active').length}
              </div>
              <div style={{ color: '#666' }}>激活策略</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#faad14' }}>
                {strategies.filter(s => s.status === 'running').length}
              </div>
              <div style={{ color: '#666' }}>运行中</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f5222d' }}>
                {strategies.filter(s => s.status === 'error').length}
              </div>
              <div style={{ color: '#666' }}>错误状态</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card>
            <ReactECharts option={performanceOption} style={{ height: '300px' }} />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={strategies}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个策略`,
          }}
        />
      </Card>

      {/* 创建/编辑策略模态框 */}
      <Modal
        title={editMode ? '编辑策略' : '创建策略'}
        open={modalVisible}
        onOk={handleSaveStrategy}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12}>
              <Form.Item
                label="策略名称"
                name="name"
                rules={[{ required: true, message: '请输入策略名称' }]}
              >
                <Input placeholder="请输入策略名称" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                label="策略类型"
                name="type"
                rules={[{ required: true, message: '请选择策略类型' }]}
              >
                <Select placeholder="请选择策略类型">
                  <Option value="grid">网格策略</Option>
                  <Option value="mean_reversion">均值回归</Option>
                  <Option value="momentum">动量策略</Option>
                  <Option value="arbitrage">套利策略</Option>
                  <Option value="custom">自定义策略</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            label="策略描述"
            name="description"
            rules={[{ required: true, message: '请输入策略描述' }]}
          >
            <TextArea rows={3} placeholder="请描述策略的核心逻辑和适用场景" />
          </Form.Item>

          <div style={{ marginBottom: '16px', fontWeight: 'bold' }}>策略参数</div>
          
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12}>
              <Form.Item label="ATR周期" name="atrPeriod">
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={100}
                  placeholder="默认14"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item label="网格间距倍数" name="gridMultiplier">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0.1}
                  max={5}
                  step={0.1}
                  placeholder="默认1.5"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item label="最大持仓数" name="maxPositions">
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={20}
                  placeholder="默认5"
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item label="单笔风险(%)" name="riskPerTrade">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0.1}
                  max={10}
                  step={0.1}
                  placeholder="默认2"
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 策略详情抽屉 */}
      <Drawer
        title="策略详情"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={600}
      >
        {selectedStrategy && (
          <div>
            <Descriptions title="基本信息" bordered column={1}>
              <Descriptions.Item label="策略名称">{selectedStrategy.name}</Descriptions.Item>
              <Descriptions.Item label="策略类型">{selectedStrategy.type}</Descriptions.Item>
              <Descriptions.Item label="状态">{getStatusTag(selectedStrategy.status)}</Descriptions.Item>
              <Descriptions.Item label="作者">{selectedStrategy.author}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{selectedStrategy.createdAt}</Descriptions.Item>
              <Descriptions.Item label="更新时间">{selectedStrategy.updatedAt}</Descriptions.Item>
              <Descriptions.Item label="描述">{selectedStrategy.description}</Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: '24px' }}>
              <Title level={4}>性能指标</Title>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '20px', fontWeight: 'bold', color: selectedStrategy.performance.totalReturn >= 0 ? '#52c41a' : '#f5222d' }}>
                        {selectedStrategy.performance.totalReturn >= 0 ? '+' : ''}{selectedStrategy.performance.totalReturn.toFixed(2)}%
                      </div>
                      <div style={{ color: '#666' }}>总收益率</div>
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                        {selectedStrategy.performance.sharpeRatio.toFixed(2)}
                      </div>
                      <div style={{ color: '#666' }}>夏普比率</div>
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f5222d' }}>
                        {selectedStrategy.performance.maxDrawdown.toFixed(2)}%
                      </div>
                      <div style={{ color: '#666' }}>最大回撤</div>
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                        {selectedStrategy.performance.winRate.toFixed(1)}%
                      </div>
                      <div style={{ color: '#666' }}>胜率</div>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>

            <div style={{ marginTop: '24px' }}>
              <Title level={4}>策略参数</Title>
              <Descriptions bordered column={1} size="small">
                {Object.entries(selectedStrategy.parameters).map(([key, value]) => (
                  <Descriptions.Item key={key} label={key}>
                    {typeof value === 'boolean' ? (value ? '是' : '否') : value}
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default StrategyPage;