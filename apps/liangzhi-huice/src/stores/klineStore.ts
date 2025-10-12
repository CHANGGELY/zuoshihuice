// K线数据状态管理

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  KlineData,
  TimeFrame,
  TradingSignal,
  ChartConfig,
  LoadingState,
  ErrorInfo,
} from '../types';
import { klineService } from '../services';

// K线状态接口
interface KlineState {
  // 数据状态
  klineData: KlineData[];
  tradingSignals: TradingSignal[];
  currentSymbol: string;
  currentTimeframe: TimeFrame;
  
  // 图表配置
  chartConfig: ChartConfig;
  
  // 加载状态
  loadingState: LoadingState;
  error: ErrorInfo | null;
  
  // 数据范围
  dateRange: {
    start: string;
    end: string;
  };
  
  // 支持的交易对和时间周期
  supportedSymbols: string[];
  supportedTimeframes: TimeFrame[];
  
  // 实时数据
  isRealTime: boolean;
  lastUpdateTime: number;
}

// K线操作接口
interface KlineActions {
  // 数据获取
  fetchKlineData: (symbol: string, timeframe: TimeFrame, startDate?: string, endDate?: string) => Promise<void>;
  fetchRealTimeData: (symbol: string, timeframe: TimeFrame) => Promise<void>;
  fetchTradingSignals: (symbol: string, timeframe: TimeFrame, startDate: string, endDate: string) => Promise<void>;
  
  // 配置更新
  updateSymbol: (symbol: string) => void;
  updateTimeframe: (timeframe: TimeFrame) => void;
  updateDateRange: (start: string, end: string) => void;
  updateChartConfig: (config: Partial<ChartConfig>) => void;
  
  // 实时数据控制
  startRealTime: () => void;
  stopRealTime: () => void;
  
  // 文件上传
  uploadH5File: (file: File) => Promise<void>;
  
  // 初始化
  initialize: () => Promise<void>;
  
  // 错误处理
  clearError: () => void;
  setError: (error: ErrorInfo) => void;
  
  // 重置状态
  reset: () => void;
}

// 初始状态
const initialState: KlineState = {
  klineData: [],
  tradingSignals: [],
  currentSymbol: 'ETHUSDT',
  currentTimeframe: TimeFrame.M1,
  
  chartConfig: {
    symbol: 'ETHUSDT',
    timeframe: TimeFrame.M1,
    theme: 'dark',
    showVolume: true,
    showSignals: true,
    showGrid: true,
    showCrosshair: true,
    autoRefresh: false,
    refreshInterval: 60,
  },
  
  loadingState: {
    isLoading: false,
    progress: 0,
    message: '',
  },
  error: null,
  
  dateRange: {
    start: '2024-01-01', // H5文件数据范围内的开始日期
    end: '2024-12-31', // H5文件数据范围内的结束日期
  },
  
  supportedSymbols: ['ETHUSDT', 'BNBUSDT'],
  supportedTimeframes: Object.values(TimeFrame),
  
  isRealTime: false,
  lastUpdateTime: 0,
};

// 创建K线状态管理
export const useKlineStore = create<KlineState & KlineActions>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // 获取K线数据
      fetchKlineData: async (symbol: string, timeframe: TimeFrame, startDate?: string, endDate?: string) => {
        const state = get();
        
        console.log('klineStore: fetchKlineData 开始', { symbol, timeframe, startDate, endDate });
        
        set({
          loadingState: {
            isLoading: true,
            progress: 0,
            message: 'Loading kline data...',
          },
          error: null,
        });

        try {
          const start = startDate || state.dateRange.start;
          const end = endDate || state.dateRange.end;
          
          console.log('klineStore: 准备调用 klineService.getKlineData', { symbol, timeframe, start, end });
          
          const response = await klineService.getKlineData({
            symbol,
            timeframe,
            start_time: start,
            end_time: end,
          });

          console.log('klineStore: klineService 响应', response);

          if (response.success && response.data) {
            console.log('klineStore: 数据成功，设置 klineData', { dataLength: response.data.length, sampleData: response.data.slice(0, 3) });
            set({
              klineData: response.data,
              lastUpdateTime: Date.now(),
              loadingState: {
                isLoading: false,
                progress: 100,
                message: 'Data loaded successfully',
              },
            });
          } else {
            console.error('klineStore: 数据加载失败', response);
            set({
              error: {
                message: response.message || 'Failed to fetch kline data',
                code: 'FETCH_ERROR',
                timestamp: Date.now(),
              },
              loadingState: {
                isLoading: false,
                progress: 0,
                message: '',
              },
            });
          }
        } catch (error) {
          console.error('klineStore: 网络错误', error);
          set({
            error: {
              message: error instanceof Error ? error.message : 'Unknown error',
              code: 'NETWORK_ERROR',
              timestamp: Date.now(),
            },
            loadingState: {
              isLoading: false,
              progress: 0,
              message: '',
            },
          });
        }
      },

      // 获取实时数据
      fetchRealTimeData: async (symbol: string, timeframe: TimeFrame) => {
        try {
          const response = await klineService.getRealTimeKlineData(symbol, timeframe);
          
          if (response.success && response.data) {
            set({
              klineData: response.data,
              lastUpdateTime: Date.now(),
            });
          }
        } catch (error) {
          console.error('Failed to fetch real-time data:', error);
        }
      },

      // 获取交易信号
      fetchTradingSignals: async (symbol: string, timeframe: TimeFrame, startDate: string, endDate: string) => {
        try {
          const response = await klineService.getTradingSignals(symbol, timeframe, startDate, endDate);
          
          if (response.success && response.data) {
            set({
              tradingSignals: response.data,
            });
          }
        } catch (error) {
          console.error('Failed to fetch trading signals:', error);
        }
      },

      // 更新交易对
      updateSymbol: (symbol: string) => {
        set({ currentSymbol: symbol });
      },

      // 更新时间周期
      updateTimeframe: (timeframe: TimeFrame) => {
        set({ currentTimeframe: timeframe });
      },

      // 更新日期范围
      updateDateRange: (start: string, end: string) => {
        set({
          dateRange: { start, end },
        });
      },

      // 更新图表配置
      updateChartConfig: (config: Partial<ChartConfig>) => {
        set({
          chartConfig: {
            ...get().chartConfig,
            ...config,
          },
        });
      },

      // 开始实时数据
      startRealTime: () => {
        set({ isRealTime: true });
        
        const { currentSymbol, currentTimeframe } = get();
        
        // 设置定时器获取实时数据
        const interval = setInterval(() => {
          if (get().isRealTime) {
            get().fetchRealTimeData(currentSymbol, currentTimeframe);
          } else {
            clearInterval(interval);
          }
        }, 5000); // 每5秒更新一次
      },

      // 停止实时数据
      stopRealTime: () => {
        set({ isRealTime: false });
      },

      // 上传H5文件
      uploadH5File: async (file: File) => {
        set({
          loadingState: {
            isLoading: true,
            progress: 0,
            message: 'Uploading H5 file...',
          },
          error: null,
        });

        try {
          const response = await klineService.uploadH5File(file);
          
          if (response.success && response.data) {
            set({
              klineData: response.data,
              lastUpdateTime: Date.now(),
              loadingState: {
                isLoading: false,
                progress: 100,
                message: 'File uploaded successfully',
              },
            });
          } else {
            set({
              error: {
                message: response.message || 'Failed to upload file',
                code: 'UPLOAD_ERROR',
                timestamp: Date.now(),
              },
              loadingState: {
                isLoading: false,
                progress: 0,
                message: '',
              },
            });
          }
        } catch (error) {
          set({
            error: {
              message: error instanceof Error ? error.message : 'Upload failed',
              code: 'UPLOAD_ERROR',
              timestamp: Date.now(),
            },
            loadingState: {
              isLoading: false,
              progress: 0,
              message: '',
            },
          });
        }
      },

      // 初始化
      initialize: async () => {
        try {
          // 获取支持的交易对
          const symbolsResponse = await klineService.getSupportedSymbols();
          if (symbolsResponse.success && symbolsResponse.data) {
            set({ supportedSymbols: symbolsResponse.data });
          }

          // 获取支持的时间周期
          const timeframesResponse = await klineService.getSupportedTimeframes();
          if (timeframesResponse.success && timeframesResponse.data) {
            set({ supportedTimeframes: timeframesResponse.data });
          }

          // 加载默认数据
          const { currentSymbol, currentTimeframe, dateRange } = get();
          await get().fetchKlineData(currentSymbol, currentTimeframe, dateRange.start, dateRange.end);
        } catch (error) {
          console.error('Failed to initialize kline store:', error);
        }
      },

      // 清除错误
      clearError: () => {
        set({ error: null });
      },

      // 设置错误
      setError: (error: ErrorInfo) => {
        set({ error });
      },

      // 重置状态
      reset: () => {
        set(initialState);
      },
    }),
    {
      name: 'kline-store',
    }
  ));

// 选择器
export const useKlineData = () => useKlineStore((state) => state.klineData);
export const useTradingSignals = () => useKlineStore((state) => state.tradingSignals);
export const useCurrentSymbol = () => useKlineStore((state) => state.currentSymbol);
export const useCurrentTimeframe = () => useKlineStore((state) => state.currentTimeframe);
export const useChartConfig = () => useKlineStore((state) => state.chartConfig);
export const useKlineLoading = () => useKlineStore((state) => state.loadingState);
export const useKlineError = () => useKlineStore((state) => state.error);
export const useIsRealTime = () => useKlineStore((state) => state.isRealTime);