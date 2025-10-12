export interface Bar {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Order {
  id: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  quantity: number;
  price?: number;
  timestamp: number;
}

export interface Trade {
  id: string;
  orderId: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  fee: number;
  timestamp: number;
}

export interface PositionSnapshot {
  symbol: string;
  quantity: number;
  averagePrice: number;
  unrealizedPnl: number;
  timestamp: number;
}

export interface EquitySnapshot {
  ts: number;
  equity: number;
  cash: number;
  unrealizedPnl: number;
  realizedPnl: number;
}

export interface BacktestResult {
  metrics: Record<string, any>;
  equity: EquitySnapshot[];
  trades: Trade[];
  positions: PositionSnapshot[];
}