// 回测服务

import { v4 as uuidv4 } from 'uuid';
import { H5Reader } from '../data/h5/H5Reader';

// 回测配置接口
export interface BacktestConfig {
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialBalance: number;
  strategy: string;
  params: Record<string, any>;
}

// K线数据接口
export interface KlineData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 交易记录接口
export interface Trade {
  id: string;
  timestamp: number;
  type: 'BUY' | 'SELL';
  price: number;
  amount: number;
  value: number;
  fee: number;
}

// 权益点接口
export interface EquityPoint {
  timestamp: number;
  equity: number;
  drawdown: number;
}

// 回测指标接口
export interface BacktestMetrics {
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
}

// 回测结果接口
export interface BacktestResult {
  id: string;
  config: BacktestConfig;
  trades: Trade[];
  metrics: BacktestMetrics;
  equity: EquityPoint[];
  startTime: number;
  endTime: number;
  duration: number;
}

// 回测状态接口
export interface BacktestStatus {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'stopped';
  progress: number;
  message?: string;
  result?: BacktestResult;
  error?: string;
  startTime: number;
  endTime?: number;
}

export class BacktestService {
  private static instance: BacktestService;
  private backtests: Map<string, BacktestStatus> = new Map();
  private h5Reader: H5Reader;

  private constructor() {
    this.h5Reader = new H5Reader();
  }

  static getInstance(): BacktestService {
    if (!BacktestService.instance) {
      BacktestService.instance = new BacktestService();
    }
    return BacktestService.instance;
  }

  /**
   * 启动回测
   */
  async startBacktest(config: BacktestConfig): Promise<string> {
    const id = uuidv4();
    const status: BacktestStatus = {
      id,
      status: 'queued',
      progress: 0,
      startTime: Date.now()
    };

    this.backtests.set(id, status);

    // 异步执行回测
    this.runBacktest(id, config).catch(error => {
      const currentStatus = this.backtests.get(id);
      if (currentStatus) {
        currentStatus.status = 'failed';
        currentStatus.error = error.message;
        currentStatus.endTime = Date.now();
      }
    });

    return id;
  }

  /**
   * 执行回测逻辑
   */
  private async runBacktest(_id: string, config: BacktestConfig): Promise<void> {
    const status = this.backtests.get(_id);
    if (!status) return;

    try {
      status.status = 'running';
      status.progress = 10;
      status.message = '加载数据中...';

      // 加载K线数据
      const startTime = new Date(config.startDate).getTime();
      const endTime = new Date(config.endDate).getTime();
      const klineData = await this.h5Reader.readData(startTime, endTime);

      if (klineData.length === 0) {
        throw new Error('指定时间范围内没有数据');
      }

      status.progress = 30;
      status.message = '执行回测策略...';

      // 执行简单的网格策略回测
      const result = await this.executeGridStrategy(_id, config, klineData);

      status.status = 'completed';
      status.progress = 100;
      status.message = '回测完成';
      status.result = result;
      status.endTime = Date.now();

    } catch (error) {
      status.status = 'failed';
      status.error = error instanceof Error ? error.message : '未知错误';
      status.endTime = Date.now();
    }
  }

  /**
   * 执行网格策略
   */
  private async executeGridStrategy(
    id: string,
    config: BacktestConfig,
    klineData: KlineData[]
  ): Promise<BacktestResult> {
    const trades: Trade[] = [];
    const equity: EquityPoint[] = [];
    
    let balance = config.initialBalance;
    let position = 0; // 持仓数量
    let lastPrice = klineData[0].close;
    let tradeCount = 0;

    // 简单网格参数
    const gridSpacing = 0.01; // 1%网格间距
    const orderSize = config.initialBalance * 0.1; // 每次交易10%资金

    for (let i = 1; i < klineData.length; i++) {
      const candle = klineData[i];
      const priceChange = (candle.close - lastPrice) / lastPrice;
      
      // 更新进度
      if (i % 1000 === 0) {
        const status = this.backtests.get(id);
        if (status) {
          status.progress = 30 + (i / klineData.length) * 60;
        }
      }

      // 网格交易逻辑
      if (Math.abs(priceChange) >= gridSpacing) {
        if (priceChange > 0 && position > 0) {
          // 价格上涨，卖出
          const sellAmount = Math.min(position, orderSize / candle.close);
          const sellValue = sellAmount * candle.close;
          const fee = sellValue * 0.001; // 0.1%手续费
          
          balance += sellValue - fee;
          position -= sellAmount;
          
          trades.push({
            id: `trade_${++tradeCount}`,
            timestamp: candle.timestamp,
            type: 'SELL',
            price: candle.close,
            amount: sellAmount,
            value: sellValue,
            fee
          });
        } else if (priceChange < 0 && balance > orderSize) {
          // 价格下跌，买入
          const buyValue = Math.min(balance * 0.5, orderSize);
          const buyAmount = buyValue / candle.close;
          const fee = buyValue * 0.001;
          
          balance -= buyValue + fee;
          position += buyAmount;
          
          trades.push({
            id: `trade_${++tradeCount}`,
            timestamp: candle.timestamp,
            type: 'BUY',
            price: candle.close,
            amount: buyAmount,
            value: buyValue,
            fee
          });
        }
        
        lastPrice = candle.close;
      }

      // 记录权益曲线
      if (i % 100 === 0) {
        const totalEquity = balance + position * candle.close;
        equity.push({
          timestamp: candle.timestamp,
          equity: totalEquity,
          drawdown: Math.max(0, (config.initialBalance - totalEquity) / config.initialBalance)
        });
      }
    }

    // 计算最终权益
    const finalPrice = klineData[klineData.length - 1].close;
    const finalEquity = balance + position * finalPrice;
    
    // 计算指标
    const metrics = this.calculateMetrics(trades, config.initialBalance, finalEquity, equity);

    return {
      id,
      config,
      trades,
      metrics,
      equity,
      startTime: klineData[0].timestamp,
      endTime: klineData[klineData.length - 1].timestamp,
      duration: klineData[klineData.length - 1].timestamp - klineData[0].timestamp
    };
  }

  /**
   * 计算回测指标
   */
  private calculateMetrics(
    trades: Trade[],
    initialBalance: number,
    finalEquity: number,
    equity: EquityPoint[]
  ): BacktestMetrics {
    const totalReturn = (finalEquity - initialBalance) / initialBalance;
    const duration = equity.length > 0 ? equity[equity.length - 1].timestamp - equity[0].timestamp : 0;
    const annualizedReturn = duration > 0 ? Math.pow(1 + totalReturn, (365 * 24 * 60 * 60 * 1000) / duration) - 1 : 0;
    
    // 计算夏普比率
    const returns = equity.map((point, index) => {
      if (index === 0) return 0;
      return (point.equity - equity[index - 1].equity) / equity[index - 1].equity;
    }).slice(1);
    
    const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    const returnStd = Math.sqrt(returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length);
    const sharpeRatio = returnStd > 0 ? avgReturn / returnStd : 0;
    
    // 计算最大回撤
    const maxDrawdown = Math.max(...equity.map(point => point.drawdown));
    
    // 计算胜率
    const winningTrades = trades.filter(trade => {
      // 简化计算，假设卖出交易为盈利判断
      return trade.type === 'SELL';
    }).length;
    const winRate = trades.length > 0 ? winningTrades / trades.length : 0;
    
    // 计算盈亏比
    const profits = trades.filter(t => t.type === 'SELL').reduce((sum, t) => sum + t.value, 0);
    const losses = trades.filter(t => t.type === 'BUY').reduce((sum, t) => sum + t.value, 0);
    const profitFactor = losses > 0 ? profits / losses : 0;

    return {
      totalReturn,
      annualizedReturn,
      sharpeRatio,
      maxDrawdown,
      winRate,
      profitFactor,
      totalTrades: trades.length
    };
  }

  /**
   * 获取回测状态
   */
  getBacktestStatus(id: string): BacktestStatus | undefined {
    return this.backtests.get(id);
  }

  /**
   * 获取回测结果
   */
  getBacktestResult(id: string): BacktestResult | undefined {
    const status = this.backtests.get(id);
    return status?.result;
  }

  /**
   * 获取所有回测历史
   */
  getBacktestHistory(): BacktestStatus[] {
    return Array.from(this.backtests.values());
  }

  /**
   * 停止回测
   */
  stopBacktest(id: string): boolean {
    const status = this.backtests.get(id);
    if (status && status.status === 'running') {
      status.status = 'stopped';
      status.endTime = Date.now();
      return true;
    }
    return false;
  }
}