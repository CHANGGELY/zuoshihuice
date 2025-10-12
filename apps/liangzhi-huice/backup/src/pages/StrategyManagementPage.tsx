import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Input,
  Switch,
  Tabs,
  Alert,
  Badge,
  Progress,
  Divider,
  Form,
  InputNumber,
  DatePicker,
  Space,
  Row,
  Col,
  Typography,
  message,
  Spin,
  Table,
  Modal
} from 'antd';
import {
  PlayCircleOutlined,
  SettingOutlined,
  RiseOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  AimOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  DownloadOutlined,
  EyeOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const { Title, Text } = Typography;

// =====================================================================================
// 类型定义
// =====================================================================================

interface StrategyConfig {
  name: string;
  description: string;
  strategy_type: string;
  
  // ATR配置
  enable_volatility_adaptive: boolean;
  atr_period: number;
  high_volatility_threshold: number;
  extreme_volatility_threshold: number;
  
  // 策略参数
  leverage: number;
  spread: number;
  position_size_ratio: number;
  hedge_mode: boolean;
  
  // 风险控制
  enable_position_balance: boolean;
  enable_emergency_close: boolean;
  emergency_close_threshold: number;
  
  // 回测参数
  initial_balance: number;
  start_date: string;
  end_date: string;
}

interface BacktestResult {
  task_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  total_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  total_trades?: number;
  equity_curve?: Array<{date: string; equity: number}>;
  trade_history?: Array<any>;
  performance_metrics?: any;
  error_message?: string;
}

interface ValidationResult {
  is_valid: boolean;
  validation_errors: string[];
  warnings: string[];
  estimated_memory_usage?: number;
  estimated_runtime?: number;
}

// =====================================================================================
// 主组件
// =====================================================================================

const StrategyManagementPage: React.FC = () => {
  // 状态管理
  const [activeTab, setActiveTab] = useState('config');
  const [strategyConfig, setStrategyConfig] = useState<StrategyConfig>({
    name: 'ATR对冲网格策略',
    description: '基于ATR波动率自适应的对冲网格策略',
    strategy_type: 'atr_hedge_grid',
    
    // ATR配置
    enable_volatility_adaptive: true,
    atr_period: 720,
    high_volatility_threshold: 0.3,
    extreme_volatility_threshold: 0.5,
    
    // 策略参数
    leverage: 125,
    spread: 0.004,
    position_size_ratio: 1.0,
    hedge_mode: true,
    
    // 风险控制
    enable_position_balance: true,
    enable_emergency_close: false,
    emergency_close_threshold: 0.2,
    
    // 回测参数
    initial_balance: 1000,
    start_date: '2020-01-01',
    end_date: '2020-05-20'
  });
  
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [currentBacktest, setCurrentBacktest] = useState<BacktestResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isRunningBacktest, setIsRunningBacktest] = useState(false);
  const [loading, setLoading] = useState(false);

  // =====================================================================================
  // API调用函数
  // =====================================================================================

  const validateStrategy = async () => {
    setIsValidating(true);
    try {
      const response = await fetch('/api/v1/strategy/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(strategyConfig),
      });
      
      if (!response.ok) {
        throw new Error('策略验证失败');
      }
      
      const result = await response.json();
      setValidationResult(result);
      
      if (result.is_valid) {
        message.success('策略配置验证通过');
      } else {
        message.error('策略配置验证失败');
      }
    } catch (error) {
      console.error('验证策略失败:', error);
      message.error('验证策略失败');
    } finally {
      setIsValidating(false);
    }
  };

  const runBacktest = async () => {
    if (!validationResult?.is_valid) {
      message.error('请先验证策略配置');
      return;
    }
    
    setIsRunningBacktest(true);
    try {
      const response = await fetch('/api/v1/strategy/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_config: strategyConfig,
          data_source: 'h5',
          symbol: 'ETHUSDT',
          timeframe: '1m'
        }),
      });
      
      if (!response.ok) {
        throw new Error('启动回测失败');
      }
      
      const result = await response.json();
      setCurrentBacktest(result);
      message.success('回测已启动');
      
      // 开始轮询回测状态
      pollBacktestStatus(result.task_id);
    } catch (error) {
      console.error('启动回测失败:', error);
      message.error('启动回测失败');
    } finally {
      setIsRunningBacktest(false);
    }
  };

  const pollBacktestStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/strategy/backtest/${taskId}`);
        if (response.ok) {
          const result = await response.json();
          setCurrentBacktest(result);
          
          if (result.status === 'completed' || result.status === 'failed') {
            clearInterval(pollInterval);
            if (result.status === 'completed') {
              message.success('回测完成');
            } else {
              message.error('回测失败');
            }
          }
        }
      } catch (error) {
        console.error('轮询回测状态失败:', error);
      }
    }, 2000);
  };

  const loadBacktestResults = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/strategy/backtest');
      if (response.ok) {
        const results = await response.json();
        setBacktestResults(results);
      }
    } catch (error) {
      console.error('加载回测结果失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================================================
  // 生命周期
  // =====================================================================================

  useEffect(() => {
    loadBacktestResults();
  }, []);

  // =====================================================================================
  // 渲染函数
  // =====================================================================================

  const renderConfigTab = () => (
    <Row gutter={[16, 16]}>
      {/* ATR配置 */}
      <Col span={24}>
        <Card title={<><ThunderboltOutlined /> ATR配置</>} size="small">
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>启用波动率自适应</Text>
                <Switch
                  checked={strategyConfig.enable_volatility_adaptive}
                  onChange={(checked) => setStrategyConfig({...strategyConfig, enable_volatility_adaptive: checked})}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>ATR计算周期（分钟）</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.atr_period}
                  onChange={(value) => setStrategyConfig({...strategyConfig, atr_period: value || 720})}
                  min={1}
                  max={1440}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>高波动率阈值</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.high_volatility_threshold}
                  onChange={(value) => setStrategyConfig({...strategyConfig, high_volatility_threshold: value || 0.3})}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                />
              </Space>
            </Col>
          </Row>
        </Card>
      </Col>

      {/* 策略参数 */}
      <Col span={24}>
        <Card title={<><AimOutlined /> 策略参数</>} size="small">
          <Row gutter={[16, 16]}>
            <Col span={6}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>杠杆倍数</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.leverage}
                  onChange={(value) => setStrategyConfig({...strategyConfig, leverage: value || 125})}
                  min={1}
                  max={125}
                />
              </Space>
            </Col>
            <Col span={6}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>价差</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.spread}
                  onChange={(value) => setStrategyConfig({...strategyConfig, spread: value || 0.004})}
                  min={0.001}
                  max={0.1}
                  step={0.001}
                />
              </Space>
            </Col>
            <Col span={6}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>仓位比例</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.position_size_ratio}
                  onChange={(value) => setStrategyConfig({...strategyConfig, position_size_ratio: value || 1.0})}
                  min={0.1}
                  max={2.0}
                  step={0.1}
                />
              </Space>
            </Col>
            <Col span={6}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>对冲模式</Text>
                <Switch
                  checked={strategyConfig.hedge_mode}
                  onChange={(checked) => setStrategyConfig({...strategyConfig, hedge_mode: checked})}
                />
              </Space>
            </Col>
          </Row>
        </Card>
      </Col>

      {/* 风险控制 */}
      <Col span={24}>
        <Card title={<><SafetyOutlined /> 风险控制</>} size="small">
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>启用仓位平衡</Text>
                <Switch
                  checked={strategyConfig.enable_position_balance}
                  onChange={(checked) => setStrategyConfig({...strategyConfig, enable_position_balance: checked})}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>启用紧急平仓</Text>
                <Switch
                  checked={strategyConfig.enable_emergency_close}
                  onChange={(checked) => setStrategyConfig({...strategyConfig, enable_emergency_close: checked})}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>紧急平仓阈值</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.emergency_close_threshold}
                  onChange={(value) => setStrategyConfig({...strategyConfig, emergency_close_threshold: value || 0.2})}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                />
              </Space>
            </Col>
          </Row>
        </Card>
      </Col>

      {/* 回测参数 */}
      <Col span={24}>
        <Card title={<><BarChartOutlined /> 回测参数</>} size="small">
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>初始资金（USDT）</Text>
                <InputNumber
                  style={{ width: '100%' }}
                  value={strategyConfig.initial_balance}
                  onChange={(value) => setStrategyConfig({...strategyConfig, initial_balance: value || 1000})}
                  min={100}
                  max={1000000}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>开始日期</Text>
                <DatePicker
                  style={{ width: '100%' }}
                  value={dayjs(strategyConfig.start_date)}
                  onChange={(date) => setStrategyConfig({...strategyConfig, start_date: date?.format('YYYY-MM-DD') || '2020-01-01'})}
                />
              </Space>
            </Col>
            <Col span={8}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>结束日期</Text>
                <DatePicker
                  style={{ width: '100%' }}
                  value={dayjs(strategyConfig.end_date)}
                  onChange={(date) => setStrategyConfig({...strategyConfig, end_date: date?.format('YYYY-MM-DD') || '2020-05-20'})}
                />
              </Space>
            </Col>
          </Row>
        </Card>
      </Col>
    </Row>
  );

  const renderValidationTab = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space>
        <Button
          type="primary"
          icon={isValidating ? <ReloadOutlined spin /> : <CheckCircleOutlined />}
          onClick={validateStrategy}
          loading={isValidating}
        >
          验证配置
        </Button>
        
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={runBacktest}
          disabled={!validationResult?.is_valid || isRunningBacktest}
          loading={isRunningBacktest}
        >
          启动回测
        </Button>
      </Space>

      {validationResult && (
        <Card title="验证结果" size="small">
          {validationResult.is_valid ? (
            <Alert
              message="策略配置验证通过"
              description={`预计内存使用: ${validationResult.estimated_memory_usage}MB，预计运行时间: ${validationResult.estimated_runtime}秒`}
              type="success"
              showIcon
            />
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {validationResult.validation_errors.map((error, index) => (
                <Alert
                  key={index}
                  message={error}
                  type="error"
                  showIcon
                />
              ))}
            </Space>
          )}
          
          {validationResult.warnings.length > 0 && (
            <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
              {validationResult.warnings.map((warning, index) => (
                <Alert
                  key={index}
                  message={warning}
                  type="warning"
                  showIcon
                />
              ))}
            </Space>
          )}
        </Card>
      )}

      {currentBacktest && (
        <Card title="当前回测" size="small">
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>任务ID: </Text>
              <Text code>{currentBacktest.task_id}</Text>
              <Badge
                status={currentBacktest.status === 'running' ? 'processing' : currentBacktest.status === 'completed' ? 'success' : 'error'}
                text={currentBacktest.status === 'running' ? '运行中' : currentBacktest.status}
                style={{ marginLeft: 8 }}
              />
            </div>
            <Progress percent={currentBacktest.status === 'running' ? 50 : 100} />
            <Text type="secondary">
              开始时间: {new Date(currentBacktest.start_time).toLocaleString()}
            </Text>
          </Space>
        </Card>
      )}
    </Space>
  );

  const renderResultsTab = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      {currentBacktest && currentBacktest.status === 'completed' && (
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: '#52c41a' }}>
                  {((currentBacktest.total_return || 0) * 100).toFixed(2)}%
                </Title>
                <Text type="secondary">总收益率</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {(currentBacktest.sharpe_ratio || 0).toFixed(2)}
                </Title>
                <Text type="secondary">夏普比率</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: '#ff4d4f' }}>
                  {((currentBacktest.max_drawdown || 0) * 100).toFixed(2)}%
                </Title>
                <Text type="secondary">最大回撤</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {((currentBacktest.win_rate || 0) * 100).toFixed(2)}%
                </Title>
                <Text type="secondary">胜率</Text>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {currentBacktest?.equity_curve && (
        <Card title="权益曲线" size="small">
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={currentBacktest.equity_curve}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="equity" stroke="#1890ff" fill="#1890ff" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}
    </Space>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>ATR对冲网格策略管理</Title>
      <Text type="secondary">配置和运行基于ATR波动率自适应的对冲网格策略</Text>
      
      <Divider />
      
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'config',
            label: <><SettingOutlined /> 策略配置</>,
            children: renderConfigTab()
          },
          {
            key: 'validation',
            label: <><CheckCircleOutlined /> 验证与回测</>,
            children: renderValidationTab()
          },
          {
            key: 'results',
            label: <><RiseOutlined /> 回测结果</>,
            children: renderResultsTab()
          }
        ]}
      />
    </div>
  );
};

export default StrategyManagementPage;