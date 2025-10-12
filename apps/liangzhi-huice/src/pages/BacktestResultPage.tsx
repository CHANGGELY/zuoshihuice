// BacktestResultPage 回测结果页面

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  RefreshCwIcon,
  HistoryIcon,
  SettingsIcon,
  TrendingUpIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  EyeIcon
} from 'lucide-react';
import { toast } from 'sonner';
import BacktestConfigForm, { BacktestConfig } from '../components/BacktestConfigForm';
import { BacktestResultVisualization } from '../components/BacktestResultVisualization';
import { BacktestResult } from '../types/backtest';
import { backtestService } from '../services';
import { StrategyType, StrategyConfig } from '../types/strategy';

interface BacktestStatus {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: BacktestResult;
  error?: string;
}

interface BacktestHistoryItem {
  id: string;
  status: string;
  progress: number;
  message: string;
  result?: BacktestResult;
  createdAt: string;
}

export const BacktestResultPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('config');
  const [currentBacktest, setCurrentBacktest] = useState<BacktestStatus | null>(null);
  const [backtestHistory, setBacktestHistory] = useState<BacktestHistoryItem[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // 加载回测历史
  useEffect(() => {
    loadBacktestHistory();
  }, []);

  // 加载回测历史
  const loadBacktestHistory = async () => {
    try {
      const history = await backtestService.getBacktestHistory();
      // 转换BacktestHistory到BacktestHistoryItem格式
      const historyItems: BacktestHistoryItem[] = (history.data || []).map(item => ({
        id: item.id,
        status: item.status,
        progress: 100, // 历史记录都是已完成的
        message: item.status === 'completed' ? '已完成' : '失败',
        createdAt: item.created_at
      }));
      setBacktestHistory(historyItems);
    } catch (error) {
      toast.error('加载回测历史失败');
    }
  };

  // 启动回测
  const handleStartBacktest = async (config: BacktestConfig) => {
    try {
      setIsRunning(true);
      
      // 转换配置格式
      const request = {
        strategy_config: {
          name: 'hedge_grid',
          type: StrategyType.HEDGE_GRID,
          symbol: config.symbol,
          timeframe: '1m',
          parameters: {
            grid_spacing: config.bidSpread,
            grid_count: 10,
            base_amount: config.minOrderAmount,
            max_position: config.maxOrderAmount,
            enable_hedge: true,
            hedge_ratio: 0.5
          }
        } as StrategyConfig,
        start_date: config.startDate,
        end_date: config.endDate,
        initial_capital: config.initialBalance,
        commission_rate: 0.001,
        slippage: 0.0001
      };
      
      const response = await backtestService.runBacktest(request);
      
      const newBacktest: BacktestStatus = {
        id: response.data?.data?.backtest_id || '',
        status: 'queued',
        progress: 0,
        message: '回测已提交，等待执行...'
      };
      
      setCurrentBacktest(newBacktest);
      setActiveTab('status');
      
      // 开始轮询状态
      startPolling(response.data?.data?.backtest_id || '');
      
      toast.success('回测已启动');
    } catch (error) {
      setIsRunning(false);
      toast.error('启动回测失败');
    }
  };

  // 开始轮询回测状态
  const startPolling = (backtestId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await backtestService.getBacktestStatus(backtestId);
        
        setCurrentBacktest(prev => prev ? {
          ...prev,
          status: status.data?.data?.status as any,
          progress: status.data?.data?.progress || 0,
          message: status.message || '运行中...',
          error: status.message
        } : null);
        
        if (status.data?.data?.status === 'completed') {
          // 获取回测结果
          const result = await backtestService.getBacktestResult(backtestId);
          setCurrentBacktest(prev => prev ? {
            ...prev,
            result: result.data
          } : null);
          
          setIsRunning(false);
          setActiveTab('results');
          clearInterval(interval);
          setPollingInterval(null);
          
          // 刷新历史记录
          loadBacktestHistory();
          
          toast.success('回测完成');
        } else if (status.data?.data && status.data.data.status === 'failed') {
          setIsRunning(false);
          clearInterval(interval);
          setPollingInterval(null);
          const errorMsg = status.message || '未知错误';
          toast.error(`回测失败: ${errorMsg}`);
        }
      } catch (error) {
        console.error('轮询状态失败:', error);
      }
    }, 2000);
    
    setPollingInterval(interval);
  };

  // 停止回测
  const handleStopBacktest = async () => {
    if (!currentBacktest) return;
    
    try {
      await backtestService.deleteBacktest(currentBacktest.id);
      setIsRunning(false);
      setCurrentBacktest(null);
      
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
      
      toast.success('回测已停止');
    } catch (error) {
      toast.error('停止回测失败');
    }
  };

  // 查看历史回测结果
  const handleViewHistoryResult = async (historyItem: BacktestHistoryItem) => {
    if (historyItem.result) {
      setCurrentBacktest({
        id: historyItem.id,
        status: 'completed',
        progress: 100,
        message: '已完成',
        result: historyItem.result
      });
      setActiveTab('results');
    } else {
      try {
        const result = await backtestService.getBacktestResult(historyItem.id);
        setCurrentBacktest({
          id: historyItem.id,
          status: 'completed',
          progress: 100,
          message: '已完成',
          result: result.data
        });
        setActiveTab('results');
      } catch (error) {
        toast.error('加载回测结果失败');
      }
    }
  };

  // 获取状态图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircleIcon className="h-4 w-4 text-red-500" />;
      case 'running':
        return <ClockIcon className="h-4 w-4 text-blue-500" />;
      default:
        return <ClockIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">回测中心</h1>
          <p className="text-muted-foreground">
            配置策略参数，运行回测并查看结果
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadBacktestHistory}
          >
            <RefreshCwIcon className="h-4 w-4 mr-2" />
            刷新
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="config" className="flex items-center space-x-2">
            <SettingsIcon className="h-4 w-4" />
            <span>配置回测</span>
          </TabsTrigger>
          <TabsTrigger value="status" disabled={!currentBacktest}>
            <ClockIcon className="h-4 w-4 mr-2" />
            <span>运行状态</span>
          </TabsTrigger>
          <TabsTrigger value="results" disabled={!currentBacktest?.result}>
            <TrendingUpIcon className="h-4 w-4 mr-2" />
            <span>回测结果</span>
          </TabsTrigger>
          <TabsTrigger value="history">
            <HistoryIcon className="h-4 w-4 mr-2" />
            <span>历史记录</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <SettingsIcon className="h-5 w-5" />
                <span>回测配置</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <BacktestConfigForm
                onSubmit={handleStartBacktest}
                loading={isRunning}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="status" className="space-y-4">
          {currentBacktest && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <ClockIcon className="h-5 w-5" />
                    <span>回测状态</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusColor(currentBacktest.status)}>
                      {getStatusIcon(currentBacktest.status)}
                      <span className="ml-1">
                        {currentBacktest.status === 'queued' && '排队中'}
                        {currentBacktest.status === 'running' && '运行中'}
                        {currentBacktest.status === 'completed' && '已完成'}
                        {currentBacktest.status === 'failed' && '失败'}
                      </span>
                    </Badge>
                    {isRunning && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={handleStopBacktest}
                      >
                        停止回测
                      </Button>
                    )}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>进度</span>
                    <span>{currentBacktest.progress}%</span>
                  </div>
                  <Progress value={currentBacktest.progress} className="w-full" />
                </div>
                
                <div className="text-sm text-muted-foreground">
                  {currentBacktest.message}
                </div>
                
                {currentBacktest.error && (
                  <Alert>
                    <AlertCircleIcon className="h-4 w-4" />
                    <AlertDescription>
                      {currentBacktest.error}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {currentBacktest?.result ? (
            <BacktestResultVisualization result={currentBacktest.result} />
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64">
                <div className="text-center">
                  <TrendingUpIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">暂无回测结果</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    请先配置并运行回测
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <HistoryIcon className="h-5 w-5" />
                <span>回测历史</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {backtestHistory.length > 0 ? (
                <div className="space-y-3">
                  {backtestHistory.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(item.status)}
                        <div>
                          <div className="font-medium">
                            回测 #{item.id.slice(0, 8)}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {new Date(item.createdAt).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(item.status)}>
                          {item.status === 'completed' && '已完成'}
                          {item.status === 'failed' && '失败'}
                          {item.status === 'running' && '运行中'}
                          {item.status === 'queued' && '排队中'}
                        </Badge>
                        
                        {item.status === 'completed' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewHistoryResult(item)}
                          >
                            <EyeIcon className="h-4 w-4 mr-1" />
                            查看结果
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <HistoryIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">暂无回测历史</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    运行第一个回测来查看历史记录
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BacktestResultPage;