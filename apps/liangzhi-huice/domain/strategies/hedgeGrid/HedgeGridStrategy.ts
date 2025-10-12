// 对冲网格策略

import { HedgeGridParams } from './params';
import { Bar } from '../../backtesting/BacktestEngine';

export class HedgeGridStrategy {
  private _params: HedgeGridParams;
  private _initialized: boolean = false;

  constructor(params: HedgeGridParams) {
    this._params = params;
  }

  async init(_bars: Bar[]): Promise<void> {
    // 初始化策略
    this._initialized = true;
  }

  get params(): HedgeGridParams {
    return this._params;
  }

  get initialized(): boolean {
    return this._initialized;
  }

  // 生成交易信号
  generateSignal(currentBar: Bar, historicalBars: Bar[]): 'BUY' | 'SELL' | 'HOLD' {
    if (!this._initialized) {
      return 'HOLD';
    }

    // 简单的网格策略逻辑
    if (historicalBars.length < 2) {
      return 'HOLD';
    }

    const previousBar = historicalBars[historicalBars.length - 2];
    const priceChange = (currentBar.close - previousBar.close) / previousBar.close;

    if (priceChange <= -this._params.gridSize) {
      return 'BUY';
    } else if (priceChange >= this._params.gridSize) {
      return 'SELL';
    }

    return 'HOLD';
  }

  // 计算订单大小
  calculateOrderSize(currentPrice: number, availableBalance: number): number {
    const maxOrderValue = Math.min(
      availableBalance * 0.1, // 最多使用10%资金
      this._params.baseOrderSize
    );
    
    return maxOrderValue / currentPrice;
  }

  // 检查风险控制
  checkRiskLimits(currentPosition: number, currentPrice: number): boolean {
    const positionValue = Math.abs(currentPosition * currentPrice);
    return positionValue <= this._params.maxPosition;
  }
}