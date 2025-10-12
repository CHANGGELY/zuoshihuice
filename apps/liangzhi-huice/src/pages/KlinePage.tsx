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
    <ErrorBoundary>
      <Layout style={{ height: '100vh', overflow: 'hidden' }}>
        {/* 侧边栏 */}
        {!isMobile && (
          <Sider
            width={300}
            collapsed={siderCollapsed}
            onCollapse={setSiderCollapsed}
            theme="light"
            style={{
              overflow: 'auto',
              height: '100vh',
              position: 'fixed',
              left: 0,
              top: 0,
              bottom: 0,
            }}
          >
            <SiderContent />
          </Sider>
        )}
        
        {/* 主内容区 */}
        <Layout style={{ marginLeft: !isMobile && !siderCollapsed ? 300 : 0 }}>
          <Content style={{ padding: '8px', overflow: 'auto' }}>
            {/* 错误提示 */}
            {error && (
              <Alert
                message="数据加载错误"
                description={error.message || '未知错误'}
                type="error"
                showIcon
                closable
                style={{ marginBottom: 8 }}
              />
            )}
            
            {/* 工具栏 */}
            <Toolbar />
            
            {/* 主图表区域 */}
            <Card
              style={{ height: 'calc(100vh - 120px)' }}
              styles={{ body: { padding: 0, height: '100%' } }}
            >
              {loadingState.isLoading ? (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '100%' 
                }}>
                  <div style={{ textAlign: 'center' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: 16 }}>加载K线数据中...</div>
                  </div>
                </div>
              ) : (
                <EChartsKlineChart
                  data={klineData}
                  signals={tradingSignals}
                  config={chartConfig}
                  onConfigChange={handleChartConfigChange}
                  height={undefined}
                  style={{ height: '100%' }}
                />
              )}
            </Card>
          </Content>
        </Layout>
        
        {/* 策略配置抽屉 */}
        <Drawer
          title="策略配置"
          placement="right"
          width={isMobile ? '100%' : 600}
          open={configDrawerVisible}
          onClose={() => setConfigDrawerVisible(false)}
          destroyOnClose
        >
          <StrategyConfigForm
            onSubmit={handleStrategySubmit}
            showRunButton
            showSaveButton
            showTemplateSelector
          />
        </Drawer>
        
        {/* 交易信号抽屉 */}
        <Drawer
          title="交易信号"
          placement="right"
          width={isMobile ? '100%' : 500}
          open={signalDrawerVisible}
          onClose={() => setSignalDrawerVisible(false)}
          destroyOnClose
        >
          <SignalMarkers
            signals={tradingSignals}
            showTable
            showFilters
            showDownload
          />
        </Drawer>
        
        {/* 移动端侧边栏抽屉 */}
        {isMobile && (
          <Drawer
            title="工具面板"
            placement="left"
            width={300}
            open={!sidebarCollapsed}
            onClose={() => setSidebarCollapsed(true)}
            destroyOnClose
          >
            <SiderContent />
          </Drawer>
        )}
      </Layout>
    </ErrorBoundary>
  );
};

export default KlinePage;