// 策略类型定义

// 策略类型枚举
export enum StrategyType {
  // 对冲网格策略
  HEDGE_GRID = 'hedge_grid',
  // 移动平均线交叉
  MA_CROSS = 'ma_cross',
  // 移动平均收敛散度
  MACD = 'macd',
  // 相对强弱指数
  RSI = 'rsi',
  // 布林带
  BOLLINGER = 'bollinger',
  // 随机指标
  KDJ = 'kdj',
  // 自定义
  CUSTOM = 'custom'
}

// 对冲网格策略参数
export interface HedgeGridParams {
  grid_spacing: number;      // 网格间距（%）
  grid_count: number;        // 网格数量
  base_amount: number;       // 基础下单量
  max_position: number;      // 最大持仓量
  stop_loss?: number;        // 止损比例（%）
  take_profit?: number;      // 止盈比例（%）
  enable_hedge: boolean;     // 是否启用对冲
  hedge_ratio: number;       // 对冲比例
}

export interface MACrossParams {
  fast_period: number;
  slow_period: number;
}

export interface MACDParams {
  fast_period: number;
  slow_period: number;
  signal_period: number;
}

export interface RSIParams {
  period: number;
  overbought: number;
  oversold: number;
}

export interface BollingerParams {
  period: number;
  std_dev: number;
}

export interface KDJParams {
  k_period: number;
  d_period: number;
  j_period: number;
}

export interface CustomParams {
  [key: string]: any;
}

export type StrategyParameters<T extends StrategyType> =
  T extends StrategyType.MA_CROSS ? MACrossParams :
  T extends StrategyType.MACD ? MACDParams :
  T extends StrategyType.RSI ? RSIParams :
  T extends StrategyType.BOLLINGER ? BollingerParams :
  T extends StrategyType.KDJ ? KDJParams :
  T extends StrategyType.CUSTOM ? CustomParams :
  T extends StrategyType.HEDGE_GRID ? HedgeGridParams :
  never;

// 策略配置接口
export type StrategyConfig = {
  id?: string;
  name: string;
  symbol: string;
  timeframe: string;
  /** 初始资金 */
  initial_capital?: number;
  /** 手续费率 */
  commission?: number;
  /** 滑点 */
  slippage?: number;
  /** 最大仓位比例 */
  max_position_size?: number;
  /** 止损比例 */
  stop_loss?: number;
  /** 止盈比例 */
  take_profit?: number;
  /** 风险管理配置 */
  risk_management?: {
    max_drawdown: number;
    risk_per_trade: number;
    position_sizing: 'fixed' | 'percent_risk' | 'kelly';
  };
  /** 过滤器配置 */
  filters?: {
    min_volume: number;
    volatility_threshold: number;
  };
  enabled?: boolean;
  created_at?: string;
  updated_at?: string;
} & ({
  type: StrategyType.MA_CROSS;
  parameters: MACrossParams;
} | {
  type: StrategyType.MACD;
  parameters: MACDParams;
} | {
  type: StrategyType.RSI;
  parameters: RSIParams;
} | {
  type: StrategyType.BOLLINGER;
  parameters: BollingerParams;
} | {
  type: StrategyType.KDJ;
  parameters: KDJParams;
} | {
  type: StrategyType.CUSTOM;
  parameters: CustomParams;
} | {
  type: StrategyType.HEDGE_GRID;
  parameters: HedgeGridParams;
});

// 策略运行状态
export enum StrategyStatus {
  STOPPED = 'stopped',
  RUNNING = 'running',
  PAUSED = 'paused',
  ERROR = 'error'
}

// 策略实例接口
export interface StrategyInstance {
  id: string;
  config: StrategyConfig;
  status: StrategyStatus;
  start_time?: string;
  stop_time?: string;
  current_position: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_trades: number;
  win_rate: number;
  error_message?: string;
}

// 策略验证结果
export interface StrategyValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// 策略模板接口
export interface StrategyTemplate<T extends StrategyType> {
  id?: string;
  type: T;
  name: string;
  description: string;
  defaultParams: StrategyParameters<T>;
  /** 完整策略配置，可直接加载 */
  config?: StrategyConfig;
  paramRules: {
    [key: string]: {
      min?: number;
      max?: number;
      step?: number;
      required: boolean;
      description: string;
    };
  };
}

// 策略性能指标
export interface StrategyMetrics {
  total_return: number;      // 总收益率
  annual_return: number;     // 年化收益率
  max_drawdown: number;      // 最大回撤
  sharpe_ratio: number;      // 夏普比率
  win_rate: number;          // 胜率
  profit_factor: number;     // 盈利因子
  total_trades: number;      // 总交易次数
  avg_trade_return: number;  // 平均交易收益
}