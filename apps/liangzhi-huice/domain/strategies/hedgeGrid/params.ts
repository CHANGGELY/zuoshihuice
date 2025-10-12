// 对冲网格策略参数

export interface HedgeGridParams {
  // 网格参数
  gridSize: number;           // 网格大小（价格间距）
  gridLevels: number;         // 网格层数
  baseOrderSize: number;      // 基础订单大小
  
  // 对冲参数
  hedgeRatio: number;         // 对冲比例 (0-1)
  hedgeThreshold: number;     // 对冲触发阈值
  
  // 风险控制
  maxPosition: number;        // 最大持仓
  stopLoss: number;           // 止损百分比
  takeProfit: number;         // 止盈百分比
  
  // 其他参数
  symbol: string;             // 交易对
  timeframe: string;          // 时间周期
}

// 默认参数
export const DEFAULT_HEDGE_GRID_PARAMS: HedgeGridParams = {
  gridSize: 0.01,             // 1% 网格间距
  gridLevels: 10,             // 10层网格
  baseOrderSize: 100,         // 基础订单100USDT
  
  hedgeRatio: 0.5,            // 50%对冲
  hedgeThreshold: 0.02,       // 2%触发对冲
  
  maxPosition: 1000,          // 最大持仓1000USDT
  stopLoss: 0.05,             // 5%止损
  takeProfit: 0.03,           // 3%止盈
  
  symbol: 'ETHUSDT',
  timeframe: '1m',
};