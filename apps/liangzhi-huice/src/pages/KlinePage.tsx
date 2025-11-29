// KlinePage K线图表页面

import React, { useEffect, useCallback, useState } from 'react';
import {
  Layout,
  Card,
  Row,
  Col,
  Space,
  Button,
  Select,
  Switch,
  Tooltip,
  message,
  Drawer,
  Badge,
  Divider,
  Alert,
  Spin,
} from 'antd';
import {
  FullscreenOutlined,
  FullscreenExitOutlined,
  DownloadOutlined,
  ReloadOutlined,
  SettingOutlined,
  BarChartOutlined,
  BellOutlined,
  MenuOutlined,
} from '@ant-design/icons';
import { EChartsKlineChart, SignalMarkers } from '../components/charts';
import { StrategyConfigForm, DateRangePicker } from '../components/forms';
import { ErrorBoundary } from '../components/common';
import { useKlineStore, useBacktestStore, useUIStore } from '../stores';
import { TimeFrame } from '../types';
import { useNavigate } from 'react-router-dom';



const { Content, Sider } = Layout;
const { Option } = Select;

// 交易对选项
const symbolOptions = [
  { label: 'ETH/USDT', value: 'ETHUSDT' },
  
  { label: 'BNB/USDT', value: 'BNBUSDT' },
  { label: 'ADA/USDT', value: 'ADAUSDT' },
  { label: 'SOL/USDT', value: 'SOLUSDT' },
  { label: 'DOT/USDT', value: 'DOTUSDT' },
  { label: 'MATIC/USDT', value: 'MATICUSDT' },
  { label: 'AVAX/USDT', value: 'AVAXUSDT' },
];

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

// K线页面组件
export const KlinePage: React.FC = () => {
  const navigate = useNavigate();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [configDrawerVisible, setConfigDrawerVisible] = useState(false);
  const [signalDrawerVisible, setSignalDrawerVisible] = useState(false);

  // Store hooks
  const {
    klineData,
    tradingSignals,
    currentSymbol,
    currentTimeframe,
    chartConfig,
    loadingState,
    error,
    dateRange,
    fetchKlineData,
    fetchTradingSignals,
    updateSymbol,
    updateTimeframe,
    updateChartConfig,
    initialize,
  } = useKlineStore();

  const {
    currentBacktest,
    runBacktest,
  } = useBacktestStore();

  const {
    isMobile,
    sidebarCollapsed,
    setSidebarCollapsed,
  } = useUIStore();

  // 初始化和数据加载
  useEffect(() => {
    console.log('KlinePage: 初始化开始');
    initialize();
  }, [initialize]);

  // 监听symbol和timeframe变化，重新加载数据
  useEffect(() => {
    console.log('KlinePage: 数据加载开始', { currentSymbol, currentTimeframe, dateRange });
    if (currentSymbol && currentTimeframe) {
      fetchKlineData(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
    }
  }, [fetchKlineData, currentSymbol, currentTimeframe, dateRange.start, dateRange.end]);


  // 自动刷新逻辑
  useEffect(() => {
    if (chartConfig.autoRefresh && chartConfig.refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchKlineData(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
      }, chartConfig.refreshInterval * 1000);
      
      return () => clearInterval(interval);
    }
  }, [chartConfig.autoRefresh, chartConfig.refreshInterval, fetchKlineData, currentSymbol, currentTimeframe, dateRange.start, dateRange.end]);

  // 处理股票代码变化
  const handleSymbolChange = useCallback((symbol: string) => {
    updateSymbol(symbol);
    message.success(`已切换到 ${symbol}`);
  }, [updateSymbol]);

  // 处理时间周期变化
  const handleTimeframeChange = useCallback((timeframe: TimeFrame) => {
    updateTimeframe(timeframe);
    message.success(`已切换到 ${timeframe}`);
  }, [updateTimeframe]);

  // 处理图表配置变化
  const handleChartConfigChange = useCallback((key: string, value: any) => {
    updateChartConfig({ [key]: value });
  }, [updateChartConfig]);

  // 处理全屏切换
  const handleFullscreenToggle = useCallback(() => {
    setIsFullscreen(!isFullscreen);
    if (!isFullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }, [isFullscreen]);

  // 处理数据刷新
  const handleRefresh = useCallback(() => {
    fetchKlineData(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
    // 仅当回测已启动后才刷新交易信号
    if (currentBacktest?.status && currentBacktest.status !== 'idle') {
      fetchTradingSignals(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
    }
    message.success('数据已刷新');
  }, [fetchKlineData, fetchTradingSignals, currentSymbol, currentTimeframe, dateRange.start, dateRange.end, currentBacktest?.status]);



  // 处理策略配置提交
  const handleStrategySubmit = useCallback(async (config: any) => {
    try {
      await runBacktest(config);
      // 开始回测后，拉取交易信号
      await fetchTradingSignals(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
      message.success('策略配置已应用，回测已开始');
      setConfigDrawerVisible(false);
    } catch (error) {
      message.error('策略配置失败');
    }
  }, [runBacktest, fetchTradingSignals, currentSymbol, currentTimeframe, dateRange.start, dateRange.end]);



  // 工具栏组件
  const Toolbar = () => (
    <Card size="small" style={{ marginBottom: 8 }}>
      <Row justify="space-between" align="middle">
        <Col>
          <Space>
            {/* 移动端菜单按钮 */}
            {isMobile && (
              <Button
                icon={<MenuOutlined />}
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              />
            )}
            
            {/* 交易对选择 */}
            <Select
              value={currentSymbol}
              onChange={handleSymbolChange}
              style={{ width: 120 }}
              size="small"
            >
              {symbolOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
            
            {/* 时间周期选择 */}
            <Select
              value={currentTimeframe}
              onChange={handleTimeframeChange}
              style={{ width: 80 }}
              size="small"
            >
              {timeframeOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
            
            <Divider type="vertical" />
            

            
            {/* 自动刷新开关 */}
            <Tooltip title={chartConfig.autoRefresh ? '关闭自动刷新' : '开启自动刷新'}>
              <Switch
                checked={chartConfig.autoRefresh}
                onChange={(checked) => updateChartConfig({ autoRefresh: checked })}
                checkedChildren="自动"
                unCheckedChildren="手动"
                size="small"
              />
            </Tooltip>
          </Space>
        </Col>
        
        <Col>
          <Space>
            {/* 信号通知 */}
            <Badge count={tradingSignals.length} size="small" overflowCount={999999}>
              <Tooltip title="交易信号">
                <Button
                  icon={<BellOutlined />}
                  size="small"
                  onClick={() => setSignalDrawerVisible(true)}
                />
              </Tooltip>
            </Badge>
            
            {/* 回测结果 */}
            <Tooltip title="回测结果">
              <Button
                icon={<BarChartOutlined />}
                size="small"
                onClick={() => navigate(currentBacktest?.id ? `/backtest/${currentBacktest.id}` : '/backtest')}
              />
            </Tooltip>
            
            {/* 策略配置 */}
            <Tooltip title="策略配置">
              <Button
                icon={<SettingOutlined />}
                size="small"
                onClick={() => setConfigDrawerVisible(true)}
              />
            </Tooltip>
            
            {/* 刷新数据 */}
            <Tooltip title="刷新数据">
              <Button
                icon={<ReloadOutlined />}
                size="small"
                onClick={handleRefresh}
                loading={loadingState.isLoading}
              />
            </Tooltip>
            
            {/* 全屏切换 */}
            <Tooltip title={isFullscreen ? '退出全屏' : '全屏显示'}>
              <Button
                icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                size="small"
                onClick={handleFullscreenToggle}
              />
            </Tooltip>
          </Space>
        </Col>
      </Row>
    </Card>
  );

  // 图表配置面板
  const ChartConfigPanel = () => (
    <Card title="图表配置" size="small" style={{ marginBottom: 8 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Row gutter={8}>
          <Col span={12}>
            <Tooltip title="显示成交量">
              <Switch
                checked={chartConfig.showVolume}
                onChange={(checked) => handleChartConfigChange('showVolume', checked)}
                checkedChildren="成交量"
                unCheckedChildren="成交量"
                size="small"
              />
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="显示网格">
              <Switch
                checked={chartConfig.showGrid}
                onChange={(checked) => handleChartConfigChange('showGrid', checked)}
                checkedChildren="网格"
                unCheckedChildren="网格"
                size="small"
              />
            </Tooltip>
          </Col>
        </Row>
        
        <Row gutter={8}>
          <Col span={12}>
            <Tooltip title="显示十字光标">
              <Switch
                checked={chartConfig.showCrosshair}
                onChange={(checked) => handleChartConfigChange('showCrosshair', checked)}
                checkedChildren="十字线"
                unCheckedChildren="十字线"
                size="small"
              />
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="显示交易信号">
              <Switch
                checked={chartConfig.showSignals}
                onChange={(checked) => handleChartConfigChange('showSignals', checked)}
                checkedChildren="信号"
                unCheckedChildren="信号"
                size="small"
              />
            </Tooltip>
          </Col>
        </Row>
        
        <Row gutter={8}>
          <Col span={12}>
            <Tooltip title="自动缩放">
              <Switch
                checked={chartConfig.showGrid}
                onChange={(checked) => handleChartConfigChange('showGrid', checked)}
                checkedChildren="网格"
                unCheckedChildren="无网格"
                size="small"
              />
            </Tooltip>
          </Col>
          <Col span={12}>
            <Select
              value={chartConfig.theme}
              onChange={(value) => handleChartConfigChange('theme', value)}
              size="small"
              style={{ width: '100%' }}
            >
              <Option value="light">浅色</Option>
              <Option value="dark">深色</Option>
            </Select>
          </Col>
        </Row>
      </Space>
    </Card>
  );

  // 侧边栏内容
  const SiderContent = () => (
    <div style={{ padding: '8px' }}>
      <ChartConfigPanel />
      
      <DateRangePicker
        showQuickSelect
        showPresets
        style={{ marginBottom: 8 }}
      />
      
      {/* 当前回测状态 */}
      {currentBacktest && (
        <Card title="当前回测" size="small" style={{ marginBottom: 8 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <strong>策略:</strong> {currentBacktest.params?.strategy?.name || '未命名'}
            </div>
            <div>
              <strong>状态:</strong> 
              <Badge 
                status={currentBacktest.status === 'running' ? 'processing' : 
                       currentBacktest.status === 'completed' ? 'success' : 'error'}
                text={currentBacktest.status === 'running' ? '运行中' : 
                     currentBacktest.status === 'completed' ? '已完成' : '失败'}
              />
            </div>
            {currentBacktest.progress !== undefined && (
              <div>
                <strong>进度:</strong> {(currentBacktest.progress * 100).toFixed(1)}%
              </div>
            )}
          </Space>
        </Card>
      )}
      
      {/* 快速操作 */}
      <Card title="快速操作" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button
            type="primary"
            icon={<SettingOutlined />}
            onClick={() => setConfigDrawerVisible(true)}
            block
            size="small"
          >
            策略配置
          </Button>
          
          <Button
            icon={<BellOutlined />}
            onClick={() => setSignalDrawerVisible(true)}
            block
            size="small"
          >
            交易信号 ({tradingSignals.length})
          </Button>
          
          <Button
            icon={<DownloadOutlined />}
            onClick={() => {
              // 导出数据逻辑
              message.info('导出功能开发中');
            }}
            block
            size="small"
          >
            导出数据
          </Button>
        </Space>
      </Card>
    </div>
  );

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden', background: 'transparent' }}>
      <Sider
        collapsible
        collapsed={siderCollapsed}
        onCollapse={setSiderCollapsed}
        theme="light"
        width={260}
        style={{ 
          borderRight: '1px solid var(--color-border)',
          background: 'var(--color-bg-surface)',
          backdropFilter: 'blur(12px)',
          zIndex: 20 
        }}
        trigger={null}
      >
        <div style={{ 
          height: '64px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: '1px solid var(--color-border)'
        }}>
          <h1 className="text-gradient" style={{ 
            fontSize: siderCollapsed ? '14px' : '20px', 
            fontWeight: 'bold',
            margin: 0,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            transition: 'all 0.3s'
          }}>
            {siderCollapsed ? '量知' : '量知·回测'}
          </h1>
        </div>
        
        <div style={{ padding: '16px', overflowY: 'auto', height: 'calc(100% - 64px)' }}>
          {!siderCollapsed && (
            <div className="animate-fade-in">
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ 
                  fontSize: '12px', 
                  textTransform: 'uppercase', 
                  color: 'var(--color-text-tertiary)',
                  marginBottom: '12px',
                  letterSpacing: '1px'
                }}>
                  市场选择
                </h3>
                <Select
                  style={{ width: '100%' }}
                  value={currentSymbol}
                  onChange={updateSymbol}
                  options={symbolOptions}
                  size="large"
                  className="glass-panel"
                  variant="borderless"
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ 
                  fontSize: '12px', 
                  textTransform: 'uppercase', 
                  color: 'var(--color-text-tertiary)',
                  marginBottom: '12px',
                  letterSpacing: '1px'
                }}>
                  时间周期
                </h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {timeframeOptions.map(option => (
                    <Button
                      key={option.value}
                      type={currentTimeframe === option.value ? 'primary' : 'default'}
                      onClick={() => updateTimeframe(option.value)}
                      size="small"
                      style={{ flex: '1 0 30%' }}
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>

              <Divider style={{ margin: '16px 0' }} />

              <Button 
                block 
                icon={<SettingOutlined />} 
                onClick={() => setConfigDrawerVisible(true)}
                style={{ marginBottom: '12px' }}
              >
                策略配置
              </Button>
              
              <Button 
                block 
                type="primary"
                icon={<BarChartOutlined />} 
                onClick={() => runBacktest()}
                loading={loadingState.isLoading}
              >
                开始回测
              </Button>
            </div>
          )}
          
          {siderCollapsed && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', marginTop: '16px' }}>
               <Tooltip title="配置" placement="right">
                 <Button type="text" icon={<SettingOutlined />} onClick={() => setConfigDrawerVisible(true)} />
               </Tooltip>
               <Tooltip title="运行回测" placement="right">
                 <Button type="primary" shape="circle" icon={<BarChartOutlined />} onClick={() => runBacktest()} />
               </Tooltip>
            </div>
          )}
        </div>
      </Sider>

      <Layout>
        <Content style={{ 
          padding: '16px', 
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '8px'
          }}>
             <Space>
               <Button 
                 type="text" 
                 icon={<MenuOutlined />} 
                 onClick={() => setSiderCollapsed(!siderCollapsed)} 
               />
               <div>
                 <span style={{ fontSize: '18px', fontWeight: 600 }}>{currentSymbol}</span>
                 <span style={{ marginLeft: '8px', color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                   {timeframeOptions.find(t => t.value === currentTimeframe)?.label}
                 </span>
               </div>
             </Space>
             
             <Space>
               <Tooltip title="重新加载数据">
                 <Button 
                   icon={<ReloadOutlined />} 
                   onClick={() => fetchKlineData(currentSymbol, currentTimeframe)}
                   loading={loadingState.isLoading}
                   shape="circle"
                 />
               </Tooltip>
               <Tooltip title="全屏模式">
                 <Button 
                   icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />} 
                   onClick={() => setIsFullscreen(!isFullscreen)}
                   shape="circle"
                 />
               </Tooltip>
             </Space>
          </div>

          {error && (
            <Alert
              message="数据加载错误"
              description={error.message}
              type="error"
              showIcon
              closable
              className="animate-fade-in"
              style={{ borderRadius: '8px' }}
            />
          )}

          <div className="glass-panel animate-fade-in" style={{ 
            flex: 1, 
            padding: '4px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            {loadingState.isLoading && !klineData.length ? (
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                flexDirection: 'column',
                gap: '16px'
              }}>
                <Spin size="large" />
                <div style={{ color: 'var(--color-text-secondary)' }}>Loading Market Data...</div>
              </div>
            ) : (
              <EChartsKlineChart 
                data={klineData}
                signals={tradingSignals}
                config={chartConfig}
                style={{ width: '100%', height: '100%' }}
              />
            )}
          </div>
        </Content>
      </Layout>

      {/* Drawers remain same but with better styling if needed */}
      <Drawer
        title="策略配置"
        placement="right"
        onClose={() => setConfigDrawerVisible(false)}
        open={configDrawerVisible}
        width={400}
        styles={{ body: { padding: 0 } }}
      >
        <StrategyConfigForm />
      </Drawer>
    </Layout>
  );
};

export default KlinePage;