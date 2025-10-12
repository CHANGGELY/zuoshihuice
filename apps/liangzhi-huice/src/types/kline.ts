// K线数据类型定义

// 时间周期枚举
export enum TimeFrame {
  M1 = '1m',
  M5 = '5m',
  M15 = '15m',
  M30 = '30m',
  H1 = '1h',
  H4 = '4h',
  D1 = '1d',
  W1 = '1w',
  MN1 = '1M'
}

// K线数据接口
export interface KlineData {
  timestamp: number;          // 时间戳
  open: number;              // 开盘价
  high: number;              // 最高价
  low: number;               // 最低价
  close: number;             // 收盘价
  volume: number;            // 成交量
  datetime?: string;         // 可读时间格式
}

// K线数据请求参数
export interface KlineRequest {
  symbol: string;            // 交易对
  timeframe: TimeFrame;      // 时间周期
  start_time?: string;       // 开始时间
  end_time?: string;         // 结束时间
  limit?: number;            // 数据条数限制
}

// K线数据响应
export interface KlineResponse {
  success: boolean;
  data: KlineData[];
  message?: string;
  total?: number;
}

// 交易信号类型
export enum SignalType {
  BUY = 'buy',
  SELL = 'sell',
  CLOSE_BUY = 'close_buy',
  CLOSE_SELL = 'close_sell'
}

// 交易信号接口
export interface TradingSignal {
  timestamp: number;
  type: SignalType;
  price: number;
  volume?: number;
  strength: number;      // 信号强度
  reason?: string;
}

// 图表配置接口
export interface ChartConfig {
  symbol: string;
  timeframe: TimeFrame;
  theme: 'light' | 'dark';
  showVolume: boolean;
  showSignals: boolean;
  showGrid: boolean;
  showCrosshair: boolean;
  autoRefresh: boolean;
  refreshInterval: number;   // 刷新间隔（秒）
}

// 技术指标类型
export interface TechnicalIndicator {
  name: string;
  type: 'line' | 'histogram' | 'overlay';
  data: Array<{
    timestamp: number;
    value: number | number[];
  }>;
  color?: string;
  visible: boolean;
}