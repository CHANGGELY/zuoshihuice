export interface HedgeGridParams {
  symbol: string;
  gridSpacing: number;
  gridLevels: number;
  orderSize: number;
  maxPosition: number;
  atrPeriod: number;
  atrMultiplier: number;
  riskPerTrade: number;
  maxDrawdown: number;
}

export const DEFAULT_HEDGE_GRID_PARAMS: HedgeGridParams = {
  symbol: 'ETHUSDT',
  gridSpacing: 0.01, // 1%
  gridLevels: 10,
  orderSize: 0.1,
  maxPosition: 1.0,
  atrPeriod: 14,
  atrMultiplier: 2.0,
  riskPerTrade: 0.02, // 2%
  maxDrawdown: 0.2 // 20%
};