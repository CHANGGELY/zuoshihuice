// StrategyConfigForm 策略配置表单组件

import React, { useCallback, useEffect } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Card,
  Space,
  Divider,
  Tooltip,
  Alert,
  Collapse,
  Row,
  Col,
  message,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import { useBacktestStore } from '../../stores';
import { StrategyConfig, TimeFrame, StrategyType } from '../../types';

const { Option } = Select;
const { TextArea } = Input;

// 策略配置表单属性
interface StrategyConfigFormProps {
  // 初始配置
  initialConfig?: Partial<StrategyConfig>;
  // 是否显示运行按钮
  showRunButton?: boolean;
  // 是否显示保存按钮
  showSaveButton?: boolean;
  // 是否显示模板选择
  showTemplateSelector?: boolean;
  // 表单提交回调
  onSubmit?: (config: StrategyConfig) => void;
  // 配置变化回调
  onChange?: (config: Partial<StrategyConfig>) => void;
  // 自定义样式
  style?: React.CSSProperties;
}

// 时间周期选项
const timeframeOptions = [
  { label: '1分钟', value: TimeFrame.M1 },
  { label: '5分钟', value: TimeFrame.M5 },
  { label: '15分钟', value: TimeFrame.M15 },
  { label: '30分钟', value: TimeFrame.M30 },
  { label: '1小时', value: TimeFrame.H1 },
  { label: '4小时', value: TimeFrame.H4 },
  { label: '1天', value: TimeFrame.D1 },
  { label: '1周', value: TimeFrame.W1 },
];

// 策略类型选项
const strategyTypeOptions = [
  { label: '移动平均线', value: 'ma_cross' },
  { label: 'MACD', value: 'macd' },
  { label: 'RSI', value: 'rsi' },
  { label: '布林带', value: 'bollinger' },
  { label: 'KDJ', value: 'kdj' },
  { label: '自定义', value: 'custom' },
];

// 默认策略配置
const defaultConfig: StrategyConfig = {
  name: '新策略',
  type: StrategyType.MA_CROSS,
  symbol: 'ETHUSDT',
  timeframe: TimeFrame.H1,
  initial_capital: 1000,
  commission: 0.001,
  slippage: 0.0001,
  max_position_size: 1.0,
  stop_loss: 0.02,
  take_profit: 0.04,
  parameters: {
    fast_period: 10,
    slow_period: 20,
  },
  risk_management: {
    max_drawdown: 0.1,
    position_sizing: 'fixed',
    risk_per_trade: 0.02,
  },
  filters: {
    min_volume: 1000000,
    volatility_threshold: 0.02,
  },
};

// 参数配置组件
const ParameterConfig: React.FC<{
  strategyType: string;
  parameters: Record<string, any>;
  onChange: (parameters: Record<string, any>) => void;
}> = ({ strategyType, parameters, onChange }) => {
  const handleParameterChange = useCallback((key: string, value: any) => {
    onChange({ ...parameters, [key]: value });
  }, [parameters, onChange]);

  const renderParameterFields = () => {
    switch (strategyType) {
      case 'ma_cross':
        return (
          <>
            <Col span={12}>
              <Form.Item label="快速周期">
                <InputNumber
                  value={parameters.fast_period ?? 10}
                  onChange={(value) => handleParameterChange('fast_period', value)}
                  min={1}
                  max={100}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="慢速周期">
                <InputNumber
                  value={parameters.slow_period ?? 20}
                  onChange={(value) => handleParameterChange('slow_period', value)}
                  min={1}
                  max={200}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </>
        );
      
      case 'macd':
        return (
          <>
            <Col span={8}>
              <Form.Item label="快速EMA">
                <InputNumber
                  value={parameters.fast_period ?? 12}
                  onChange={(value) => handleParameterChange('fast_period', value)}
                  min={1}
                  max={50}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="慢速EMA">
                <InputNumber
                  value={parameters.slow_period ?? 26}
                  onChange={(value) => handleParameterChange('slow_period', value)}
                  min={1}
                  max={100}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="信号线">
                <InputNumber
                  value={parameters.signal_period ?? 9}
                  onChange={(value) => handleParameterChange('signal_period', value)}
                  min={1}
                  max={50}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </>
        );
      
      case 'rsi':
        return (
          <>
            <Col span={8}>
              <Form.Item label="RSI周期">
                <InputNumber
                  value={parameters.period ?? 14}
                  onChange={(value) => handleParameterChange('period', value)}
                  min={1}
                  max={50}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="超买线">
                <InputNumber
                  value={parameters.overbought ?? 70}
                  onChange={(value) => handleParameterChange('overbought', value)}
                  min={50}
                  max={90}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="超卖线">
                <InputNumber
                  value={parameters.oversold ?? 30}
                  onChange={(value) => handleParameterChange('oversold', value)}
                  min={10}
                  max={50}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </>
        );
      
      case 'bollinger':
        return (
          <>
            <Col span={8}>
              <Form.Item label="周期">
                <InputNumber
                  value={parameters.period ?? 20}
                  onChange={(value) => handleParameterChange('period', value)}
                  min={1}
                  max={100}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="标准差倍数">
                <InputNumber
                  value={parameters.std_dev ?? 2}
                  onChange={(value) => handleParameterChange('std_dev', value)}
                  min={0.5}
                  max={5}
                  step={0.1}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </>
        );
      
      default:
        return (
          <Col span={24}>
            <Form.Item label="自定义参数">
              <TextArea
                value={JSON.stringify(parameters ?? {}, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value);
                    onChange(parsed);
                  } catch (error) {
                    // 忽略JSON解析错误
                  }
                }}
                rows={6}
                placeholder="请输入JSON格式的参数配置"
              />
            </Form.Item>
          </Col>
        );
    }
  };

  return (
    <Row gutter={16}>
      {renderParameterFields()}
    </Row>
  );
};

// StrategyConfigForm主组件
export const StrategyConfigForm: React.FC<StrategyConfigFormProps> = ({
  initialConfig,
  showRunButton = true,
  showSaveButton = true,
  showTemplateSelector = true,
  onSubmit,
  onChange,
  style,
}) => {
  const [form] = Form.useForm();
  const [config, setConfig] = React.useState<StrategyConfig>({
    ...defaultConfig,
    ...initialConfig,
  } as StrategyConfig);

  const strategyTemplates = useBacktestStore((state) => state.strategyTemplates);
  const loading = useBacktestStore((state) => state.loadingState.isLoading);
  const errorInfo = useBacktestStore((state) => state.error);
  const loadStrategyTemplates = useBacktestStore((state) => state.loadStrategyTemplates);
  const saveStrategy = useBacktestStore((state) => state.saveStrategy);
  const runBacktest = useBacktestStore((state) => state.runBacktest);

  // 加载策略模板
  useEffect(() => {
    if (showTemplateSelector) {
      loadStrategyTemplates();
    }
  }, [showTemplateSelector, loadStrategyTemplates]);

  // 同步表单值
  useEffect(() => {
    form.setFieldsValue(config);
  }, [config, form]);

  // 处理配置变化
  const handleConfigChange = useCallback((changedFields: any) => {
    const newConfig = { ...config, ...changedFields };
    setConfig(newConfig);
    onChange?.(newConfig);
  }, [config, onChange]);

  // 处理模板选择
  const handleTemplateSelect = useCallback((templateId: string) => {
    const template = strategyTemplates.find(t => t.id === templateId);
    if (template) {
      const newConfig = { ...template } as StrategyConfig;
      setConfig(newConfig);
      form.setFieldsValue(newConfig);
      message.success(`已加载模板: ${template.name}`);
    }
  }, [strategyTemplates, form]);

  // 处理参数变化
  const handleParametersChange = useCallback((parameters: Record<string, any>) => {
    const newConfig = { ...config, parameters } as StrategyConfig;
    setConfig(newConfig);
    form.setFieldValue('parameters', parameters);
    onChange?.(newConfig);
  }, [config, form, onChange]);



  // 处理表单提交
  const handleSubmit = useCallback(async () => {
    try {
      const formData = form.getFieldsValue();
      const submitConfig = { ...config, ...formData };
      
      await onSubmit?.(submitConfig);
      message.success('策略配置已提交');
    } catch (error) {
      message.error('提交失败: ' + (error instanceof Error ? error.message : '未知错误'));
    }
  }, [config, form, onSubmit]);

  // 处理保存配置
  const handleSave = useCallback(async () => {
    try {
      const values = await form.validateFields();
      const finalConfig = { ...config, ...values };
      
      await saveStrategy(finalConfig);
      message.success('策略配置保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  }, [form, config, saveStrategy]);

  // 处理运行回测
  const handleRunBacktest = useCallback(async () => {
    try {
      const values = await form.validateFields();
      const finalConfig = { ...config, ...values };
      
      await runBacktest(finalConfig);
      message.success('回测已开始运行');
    } catch (error) {
      message.error('运行回测失败');
    }
  }, [form, config, runBacktest]);

  // 处理重置表单
  const handleReset = useCallback(() => {
    form.resetFields();
    setConfig({ ...defaultConfig, ...initialConfig } as StrategyConfig);
    message.info('表单已重置');
  }, [form, initialConfig]);

  // 处理复制配置
  const handleCopyConfig = useCallback(() => {
    const configText = JSON.stringify(config, null, 2);
    navigator.clipboard.writeText(configText).then(() => {
      message.success('配置已复制到剪贴板');
    }).catch(() => {
      message.error('复制失败');
    });
  }, [config]);

  return (
    <Card
      title="策略配置"
      extra={
        <Space>
          {showTemplateSelector && (
            <Select
              placeholder="选择模板"
              style={{ width: 150 }}
              onChange={handleTemplateSelect}
              loading={loading}
            >
              {strategyTemplates.map(template => (
                <Option key={template.id} value={template.id}>
                  {template.name}
                </Option>
              ))}
            </Select>
          )}
          
          <Tooltip title="复制配置">
            <Button icon={<CopyOutlined />} onClick={handleCopyConfig} />
          </Tooltip>
          
          <Tooltip title="重置表单">
            <Button icon={<ReloadOutlined />} onClick={handleReset} />
          </Tooltip>
        </Space>
      }
      style={style}
    >
      {errorInfo && (
        <Alert
          message="配置错误"
          description={errorInfo.message}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        initialValues={config}
        onValuesChange={handleConfigChange}
      >
        <Collapse 
          defaultActiveKey={['basic', 'parameters']}
          items={[
            {
              key: 'basic',
              label: '基础配置',
              children: (
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="策略名称"
                      name="name"
                      rules={[{ required: true, message: '请输入策略名称' }]}
                    >
                      <Input placeholder="请输入策略名称" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="策略类型"
                      name="type"
                      rules={[{ required: true, message: '请选择策略类型' }]}
                    >
                      <Select placeholder="请选择策略类型">
                        {strategyTypeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="交易对"
                      name="symbol"
                      rules={[{ required: true, message: '请输入交易对' }]}
                    >
                      <Input placeholder="如: ETHUSDT" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="时间周期"
                      name="timeframe"
                      rules={[{ required: true, message: '请选择时间周期' }]}
                    >
                      <Select placeholder="请选择时间周期">
                        {timeframeOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            {option.label}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              )
            },
            {
              key: 'parameters',
              label: '策略参数',
              children: (
                <ParameterConfig
                  strategyType={config.type}
                  parameters={config.parameters ?? {}}
                  onChange={handleParametersChange}
                />
              )
            },
            {
              key: 'capital',
              label: '资金管理',
              children: (
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item label="初始资金" name="initial_capital">
                      <InputNumber
                        min={1000}
                        max={10000000}
                        formatter={(value) => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={(value) => Number(value!.replace(/\$\s?|(,*)/g, '')) as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="手续费率" name="commission">
                      <InputNumber
                        min={0}
                        max={0.01}
                        step={0.0001}
                        formatter={(value) => `${(value! * 100).toFixed(2)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="滑点" name="slippage">
                      <InputNumber
                        min={0}
                        max={0.001}
                        step={0.00001}
                        formatter={(value) => `${(value! * 100).toFixed(3)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              )
            },
            {
              key: 'risk',
              label: '风险管理',
              children: (
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item label="止损比例" name="stop_loss">
                      <InputNumber
                        min={0.001}
                        max={0.5}
                        step={0.001}
                        formatter={(value) => `${(value! * 100).toFixed(1)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="止盈比例" name="take_profit">
                      <InputNumber
                        min={0.001}
                        max={1}
                        step={0.001}
                        formatter={(value) => `${(value! * 100).toFixed(1)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="最大仓位" name="max_position_size">
                      <InputNumber
                        min={0.1}
                        max={1}
                        step={0.1}
                        formatter={(value) => `${(value! * 100).toFixed(0)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="最大回撤" name={['risk_management', 'max_drawdown']}>
                      <InputNumber
                        min={0.01}
                        max={0.5}
                        step={0.01}
                        formatter={(value) => `${(value! * 100).toFixed(0)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="单笔风险" name={['risk_management', 'risk_per_trade']}>
                      <InputNumber
                        min={0.001}
                        max={0.1}
                        step={0.001}
                        formatter={(value) => `${(value! * 100).toFixed(1)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="仓位管理" name={['risk_management', 'position_sizing']}>
                      <Select
                        style={{ width: '100%' }}
                      >
                        <Option value="fixed">固定仓位</Option>
                        <Option value="percent_risk">风险百分比</Option>
                        <Option value="kelly">凯利公式</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              )
            },
            {
              key: 'filters',
              label: '过滤条件',
              children: (
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item label="最小成交量" name={['filters', 'min_volume']}>
                      <InputNumber
                        min={0}
                        formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={(value) => Number(value!.replace(/,/g, '')) as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label="波动率阈值" name={['filters', 'volatility_threshold']}>
                      <InputNumber
                        min={0}
                        max={1}
                        step={0.001}
                        formatter={(value) => `${(value! * 100).toFixed(1)}%`}
                        parser={(value) => Number(value!.replace('%', '')) / 100 as any}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              )
            }
          ]}
        />

        <Divider />

        {/* 操作按钮 */}
        <Space style={{ width: '100%', justifyContent: 'center' }}>
          {showSaveButton && (
            <Button
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
            >
              保存配置
            </Button>
          )}
          
          {showRunButton && (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleRunBacktest}
              loading={loading}
            >
              运行回测
            </Button>
          )}
          
          <Button onClick={handleSubmit} loading={loading}>
            应用配置
          </Button>
        </Space>
      </Form>
    </Card>
  );
};

export default StrategyConfigForm;