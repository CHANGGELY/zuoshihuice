// K线数据服务

import { apiClient, API_ENDPOINTS } from './api';
import {
  KlineData,
  KlineRequest,
  TimeFrame,
  TradingSignal,
  ApiResponse,
} from '../types';

// K线数据服务类
class KlineService {
  // 获取K线数据
  async getKlineData(params: KlineRequest): Promise<ApiResponse<KlineData[]>> {
    try {
      console.log('klineService.getKlineData 调用参数', params);
      // 使用后端根路由 /api/kline，支持 symbol/timeframe 与时间范围过滤
      const response = await apiClient.get<KlineData[]>(API_ENDPOINTS.KLINE, {
        symbol: params.symbol,
        timeframe: params.timeframe,
        start_time: params.start_time,
        end_time: params.end_time,
        limit: params.limit || 1000,
      });
      console.log('klineService.getKlineData 原始响应', response);
      
      if (response.success && response.data) {
        // 确保时间戳格式正确（毫秒级Unix时间戳）
        const formattedData = response.data.map((item: any) => ({
          timestamp: typeof item.timestamp === 'number' ? item.timestamp : new Date(item.timestamp).getTime(),
          open: Number(item.open),
          high: Number(item.high),
          low: Number(item.low),
          close: Number(item.close),
          volume: Number(item.volume),
          datetime: new Date(typeof item.timestamp === 'number' ? item.timestamp : new Date(item.timestamp).getTime()).toISOString(),
        }));
        console.log('klineService.getKlineData 转换后数据样本', formattedData.slice(0, 3));
        
        return {
          success: true,
          data: formattedData,
          message: response.message,
        };
      } else {
        return {
          success: false,
          message: response.message || 'Failed to fetch H5 kline data',
        };
      }
    } catch (error) {
      console.error('klineService.getKlineData 异常', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch kline data',
      };
    }
  }

  // 获取历史K线数据 - 使用根路由 /api/kline
  async getHistoryKlineData(
    symbol: string,
    timeframe: TimeFrame,
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<KlineData[]>> {
    try {
      const response = await apiClient.get<KlineData[]>(API_ENDPOINTS.KLINE, {
        symbol,
        timeframe,
        start_time: startDate,
        end_time: endDate,
      });

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch history kline data',
      };
    }
  }

  // 获取实时K线数据 - 使用根路由 /api/kline
  async getRealTimeKlineData(
    symbol: string,
    timeframe: TimeFrame,
    limit: number = 100
  ): Promise<ApiResponse<KlineData[]>> {
    try {
      const response = await apiClient.get<KlineData[]>(API_ENDPOINTS.KLINE, {
        symbol,
        timeframe,
        limit,
      });

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch real-time kline data',
      };
    }
  }

  // 获取支持的交易对列表 - 使用正确的路由
  async getSupportedSymbols(): Promise<ApiResponse<string[]>> {
    try {
      const response = await apiClient.get<string[]>(API_ENDPOINTS.SYMBOLS);
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch supported symbols',
      };
    }
  }

  // 获取支持的时间周期列表 - 使用正确的路由
  async getSupportedTimeframes(): Promise<ApiResponse<TimeFrame[]>> {
    try {
      const response = await apiClient.get<TimeFrame[]>(API_ENDPOINTS.TIMEFRAMES);
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch supported timeframes',
      };
    }
  }

  // 上传H5文件获取K线数据
  async uploadH5File(file: File): Promise<ApiResponse<KlineData[]>> {
    try {
      const response = await apiClient.upload<KlineData[]>(API_ENDPOINTS.UPLOAD_H5, file);
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to upload H5 file',
      };
    }
  }

  // 获取交易信号 - 使用正确的路由
  async getTradingSignals(
    symbol: string,
    timeframe: TimeFrame,
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<TradingSignal[]>> {
    try {
      const response = await apiClient.get<TradingSignal[]>(API_ENDPOINTS.SIGNALS, {
        symbol,
        timeframe,
        start_date: startDate,
        end_date: endDate,
      });

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch trading signals',
      };
    }
  }

  // 数据格式转换工具
  formatKlineData(rawData: any[]): KlineData[] {
    return rawData.map((item) => ({
      timestamp: typeof item.timestamp === 'string' ? 
        new Date(item.timestamp).getTime() : item.timestamp,
      open: Number(item.open),
      high: Number(item.high),
      low: Number(item.low),
      close: Number(item.close),
      volume: Number(item.volume),
      datetime: item.datetime || new Date(item.timestamp).toISOString(),
    }));
  }

  // 数据验证
  validateKlineData(data: KlineData[]): boolean {
    if (!Array.isArray(data) || data.length === 0) {
      return false;
    }

    return data.every((item) => {
      return (
        typeof item.timestamp === 'number' &&
        typeof item.open === 'number' &&
        typeof item.high === 'number' &&
        typeof item.low === 'number' &&
        typeof item.close === 'number' &&
        typeof item.volume === 'number' &&
        item.high >= item.low &&
        item.high >= Math.max(item.open, item.close) &&
        item.low <= Math.min(item.open, item.close)
      );
    });
  }

  // 计算技术指标（简单移动平均线）
  calculateSMA(data: KlineData[], period: number): number[] {
    const sma: number[] = [];
    
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        sma.push(NaN);
      } else {
        const sum = data.slice(i - period + 1, i + 1)
          .reduce((acc, item) => acc + item.close, 0);
        sma.push(sum / period);
      }
    }
    
    return sma;
  }

  // 计算价格变化百分比
  calculatePriceChange(data: KlineData[]): Array<{ timestamp: number; change: number }> {
    const changes: Array<{ timestamp: number; change: number }> = [];
    
    for (let i = 1; i < data.length; i++) {
      const prevClose = data[i - 1].close;
      const currentClose = data[i].close;
      const change = ((currentClose - prevClose) / prevClose) * 100;
      
      changes.push({
        timestamp: data[i].timestamp,
        change,
      });
    }
    
    return changes;
  }
}

// 创建K线服务实例
export const klineService = new KlineService();

// 导出服务类
export { KlineService };