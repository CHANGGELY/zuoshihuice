// 回测服务

import { apiClient, API_ENDPOINTS } from './api';
import {
  BacktestParams,
  BacktestResult,
  BacktestRequest,
  BacktestResponse,
  BacktestStatusResponse,
  BacktestHistory,
  BacktestComparison,
  TradeRecord,
  PositionRecord,
  StrategyConfig,
  ApiResponse,
} from '../types';

// 回测服务类
class BacktestService {
  // 执行回测
  async runBacktest(params: BacktestRequest): Promise<ApiResponse<BacktestResponse>> {
    try {
      const response = await apiClient.post<BacktestResponse>(API_ENDPOINTS.BACKTEST, params);
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to run backtest',
      };
    }
  }

  // 查询回测状态
  async getBacktestStatus(backtestId: string): Promise<ApiResponse<BacktestStatusResponse>> {
    try {
      const response = await apiClient.get<BacktestStatusResponse>(
        `${API_ENDPOINTS.BACKTEST_STATUS}?id=${backtestId}`
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get backtest status',
      };
    }
  }

  // 获取回测结果
  async getBacktestResult(backtestId: string): Promise<ApiResponse<BacktestResult>> {
    try {
      const response = await apiClient.get<BacktestResult>(
        `${API_ENDPOINTS.BACKTEST}/result/${backtestId}`
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get backtest result',
      };
    }
  }

  // 获取回测历史记录
  async getBacktestHistory(): Promise<ApiResponse<BacktestHistory[]>> {
    try {
      const response = await apiClient.get<BacktestHistory[]>(
        API_ENDPOINTS.BACKTEST_HISTORY
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get backtest history',
      };
    }
  }

  // 删除回测记录
  async deleteBacktest(backtestId: string): Promise<ApiResponse<void>> {
    try {
      const response = await apiClient.delete<void>(`${API_ENDPOINTS.BACKTEST}/${backtestId}`);
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to delete backtest',
      };
    }
  }

  // 获取交易记录
  async getTradeRecords(backtestId: string): Promise<ApiResponse<TradeRecord[]>> {
    try {
      const response = await apiClient.get<TradeRecord[]>(
        `${API_ENDPOINTS.BACKTEST}/${backtestId}/trades`
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get trade records',
      };
    }
  }

  // 获取持仓记录
  async getPositionRecords(backtestId: string): Promise<ApiResponse<PositionRecord[]>> {
    try {
      const response = await apiClient.get<PositionRecord[]>(
        `${API_ENDPOINTS.BACKTEST}/${backtestId}/positions`
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get position records',
      };
    }
  }

  // 比较多个回测结果
  async compareBacktests(backtestIds: string[]): Promise<ApiResponse<BacktestComparison>> {
    try {
      const response = await apiClient.post<BacktestComparison>(
        `${API_ENDPOINTS.BACKTEST}/compare`,
        { backtest_ids: backtestIds }
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to compare backtests',
      };
    }
  }

  // 导出回测结果
  async exportBacktestResult(
    backtestId: string,
    format: 'csv' | 'excel' | 'json' = 'csv'
  ): Promise<ApiResponse<Blob>> {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.BACKTEST}/${backtestId}/export?format=${format}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        return {
          success: false,
          message: `Export failed: ${response.statusText}`,
        };
      }

      const blob = await response.blob();
      return {
        success: true,
        data: blob,
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to export backtest result',
      };
    }
  }

  // 验证策略配置
  async validateStrategy(strategyConfig: StrategyConfig): Promise<ApiResponse<{ valid: boolean; errors?: string[] }>> {
    try {
      const response = await apiClient.post<{ valid: boolean; errors?: string[] }>(
        API_ENDPOINTS.STRATEGY_VALIDATE,
        strategyConfig
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to validate strategy',
      };
    }
  }

  // 获取策略模板
  async getStrategyTemplates(): Promise<ApiResponse<StrategyConfig[]>> {
    try {
      const response = await apiClient.get<StrategyConfig[]>('/api/strategy/templates');
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get strategy templates',
      };
    }
  }

  // 保存策略配置
  async saveStrategy(strategyConfig: StrategyConfig): Promise<ApiResponse<{ id: string }>> {
    try {
      const response = await apiClient.post<{ id: string }>(
        API_ENDPOINTS.STRATEGY,
        strategyConfig
      );
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to save strategy',
      };
    }
  }

  // 工具方法：计算回测性能指标
  calculatePerformanceMetrics(result: BacktestResult) {
    const { equity_curve, trades } = result;
    
    if (!equity_curve || equity_curve.length === 0) {
      return null;
    }

    const initialEquity = equity_curve[0].equity;
    const finalEquity = equity_curve[equity_curve.length - 1].equity;
    const totalReturn = ((finalEquity - initialEquity) / initialEquity) * 100;

    // 计算最大回撤
    let maxDrawdown = 0;
    let peak = initialEquity;
    
    for (const point of equity_curve) {
      if (point.equity > peak) {
        peak = point.equity;
      }
      const drawdown = ((peak - point.equity) / peak) * 100;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }

    // 计算胜率
    const winningTrades = trades.filter(trade => (trade.pnl || 0) > 0).length;
    const winRate = trades.length > 0 ? (winningTrades / trades.length) * 100 : 0;

    // 计算平均盈亏
    const totalPnl = trades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
    const avgPnl = trades.length > 0 ? totalPnl / trades.length : 0;

    return {
      totalReturn: Number(totalReturn.toFixed(2)),
      maxDrawdown: Number(maxDrawdown.toFixed(2)),
      winRate: Number(winRate.toFixed(2)),
      avgPnl: Number(avgPnl.toFixed(2)),
      totalTrades: trades.length,
      winningTrades,
      losingTrades: trades.length - winningTrades,
    };
  }

  // 工具方法：格式化回测参数
  formatBacktestParams(params: BacktestParams): BacktestRequest {
    return {
      strategy_config: params.strategy,
      start_date: params.start_date,
      end_date: params.end_date,
      initial_capital: params.initial_capital,
      commission_rate: params.commission_rate,
      slippage: params.slippage,
    };
  }

  // 工具方法：下载文件
  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// 创建回测服务实例
export const backtestService = new BacktestService();

// 导出服务类
export { BacktestService };