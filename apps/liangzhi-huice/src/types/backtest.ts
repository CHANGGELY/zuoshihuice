// 回测类型定义

import { StrategyConfig, StrategyMetrics } from './strategy';
import { TradingSignal } from './kline';

// 回测参数接口
export interface BacktestParams {
  strategy: StrategyConfig;
  start_date: string;        // 回测开始日期
  end_date: string;          // 回测结束日期
  initial_capital: number;   // 初始资金
  commission_rate: number;   // 手续费率
  slippage: number;          // 滑点
}

// 交易记录接口
export interface TradeRecord {
  id: string;
  timestamp: number;
  datetime: string;
  symbol: string;
  side: 'buy' | 'sell';      // 交易方向
  type: 'open' | 'close';    // 开仓/平仓
  price: number;             // 成交价格
  quantity: number;          // 成交数量
  commission: number;        // 手续费
  pnl?: number;              // 盈亏（平仓时）
  position_size: number;     // 持仓大小
  balance: number;           // 账户余额
  signal?: TradingSignal;    // 对应的交易信号
}

// 持仓记录接口
export interface PositionRecord {
  timestamp: number;
  datetime: string;
  position_size: number;     // 持仓大小
  avg_price: number;         // 平均成本价
  unrealized_pnl: number;    // 浮动盈亏
  realized_pnl: number;      // 已实现盈亏
  total_pnl: number;         // 总盈亏
  balance: number;           // 账户余额
  equity: number;            // 净值
}

// 回测结果接口
export interface BacktestResult {
  id: string;
  params: BacktestParams;
  status: 'running' | 'completed' | 'failed';
  progress?: number;         // 回测进度（0-100）
  start_time: string;
  end_time?: string;
  
  // 回测统计 - 直接包含所有指标
  total_return: number;      // 总收益率
  annualized_return: number; // 年化收益率
  max_drawdown: number;      // 最大回撤
  sharpe_ratio: number;      // 夏普比率
  win_rate: number;          // 胜率
  profit_factor: number;     // 盈利因子
  profit_loss_ratio: number; // 盈亏比
  total_trades: number;      // 总交易次数
  avg_trade_return: number;  // 平均交易收益
  max_consecutive_losses: number; // 最大连续亏损
  
  // 兼容性：保留metrics字段
  metrics: StrategyMetrics;
  
  // 详细数据
  trades: TradeRecord[];     // 交易记录
  positions: PositionRecord[]; // 持仓历史
  equity_curve: Array<{      // 资金曲线
    timestamp: number;
    datetime: string;
    equity: number;
    drawdown: number;
  }>;
  
  // 错误信息
  error_message?: string;
}

// 回测请求接口
export interface BacktestRequest {
  strategy_config: StrategyConfig;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission_rate?: number;
  slippage?: number;
}

// 回测响应接口
export interface BacktestResponse {
  success: boolean;
  data?: {
    backtest_id: string;
    result?: BacktestResult;
  };
  message?: string;
  task_id?: string;          // 异步任务ID
}

// 回测状态查询响应
export interface BacktestStatusResponse {
  success: boolean;
  data?: {
    status: 'running' | 'completed' | 'failed';
    progress: number;
    result?: BacktestResult;
  };
  message?: string;
}

// 回测历史记录
export interface BacktestHistory {
  id: string;
  name: string;
  strategy_name: string;
  strategy_type: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_equity: number;
  total_return: number;
  max_drawdown: number;
  created_at: string;
  status: 'completed' | 'failed';
}

// 回测比较接口
export interface BacktestComparison {
  results: BacktestResult[];
  comparison_metrics: {
    [key: string]: {
      values: number[];
      best_index: number;
      worst_index: number;
    };
  };
}