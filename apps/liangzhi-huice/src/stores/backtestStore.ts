// 回测状态管理

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  BacktestParams,
  BacktestResult,
  BacktestHistory,
  TradeRecord,
  PositionRecord,
  StrategyConfig,
  LoadingState,
  ErrorInfo,
  PaginationParams,
} from '../types';
import { backtestService } from '../services';

// 回测状态接口
interface BacktestState {
  // 当前回测
  currentBacktest: {
    id: string | null;
    params: BacktestParams | null;
    result: BacktestResult | null;
    status: 'idle' | 'running' | 'completed' | 'failed';
    progress: number;
  };
  
  // 回测历史
  backtestHistory: {
    items: BacktestHistory[];
    total: number;
    pagination: PaginationParams;
  };
  
  // 策略配置
  strategyConfig: StrategyConfig | null;
  strategyTemplates: StrategyConfig[];
  
  // 交易记录
  tradeRecords: TradeRecord[];
  positionRecords: PositionRecord[];
  
  // 比较功能
  selectedBacktests: string[];
  comparisonResult: any | null;
  
  // 加载状态
  loadingState: LoadingState;
  error: ErrorInfo | null;
  
  // UI状态
  activeTab: 'overview' | 'trades' | 'positions' | 'analysis';
  showComparison: boolean;
}

// 回测操作接口
interface BacktestActions {
  // 回测执行
  runBacktest: (params: BacktestParams) => Promise<void>;
  pollBacktestStatus: (backtestId: string) => Promise<void>;
  checkBacktestStatus: (backtestId: string) => Promise<void>;
  getBacktestResult: (backtestId: string) => Promise<void>;
  
  // 历史记录
  fetchBacktestHistory: (page?: number, pageSize?: number) => Promise<void>;
  deleteBacktest: (backtestId: string) => Promise<void>;
  
  // 策略管理
  updateStrategyConfig: (config: StrategyConfig) => void;
  validateStrategy: (config: StrategyConfig) => Promise<boolean>;
  saveStrategy: (config: StrategyConfig) => Promise<void>;
  loadStrategyTemplates: () => Promise<void>;
  
  // 交易记录
  fetchTradeRecords: (backtestId: string) => Promise<void>;
  fetchPositionRecords: (backtestId: string) => Promise<void>;
  
  // 比较功能
  selectBacktestForComparison: (backtestId: string) => void;
  removeBacktestFromComparison: (backtestId: string) => void;
  compareBacktests: () => Promise<void>;
  
  // 导出功能
  exportBacktestResult: (backtestId: string, format: 'csv' | 'excel' | 'json') => Promise<void>;
  
  // UI控制
  setActiveTab: (tab: 'overview' | 'trades' | 'positions' | 'analysis') => void;
  toggleComparison: () => void;
  
  // 错误处理
  clearError: () => void;
  setError: (error: ErrorInfo) => void;
  
  // 重置状态
  reset: () => void;
  resetCurrentBacktest: () => void;
}

// 初始状态
const initialState: BacktestState = {
  currentBacktest: {
    id: null,
    params: null,
    result: null,
    status: 'idle',
    progress: 0,
  },
  
  backtestHistory: {
    items: [],
    total: 0,
    pagination: {
      page: 1,
      page_size: 20,
      total: 0,
    },
  },
  
  strategyConfig: null,
  strategyTemplates: [],
  
  tradeRecords: [],
  positionRecords: [],
  
  selectedBacktests: [],
  comparisonResult: null,
  
  loadingState: {
    isLoading: false,
    progress: 0,
    message: '',
  },
  error: null,
  
  activeTab: 'overview',
  showComparison: false,
};

// 创建回测状态管理
export const useBacktestStore = create<BacktestState & BacktestActions>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // 执行回测
      runBacktest: async (params: BacktestParams) => {
        set({
          loadingState: {
            isLoading: true,
            progress: 0,
            message: 'Starting backtest...',
          },
          error: null,
          currentBacktest: {
            id: null,
            params,
            result: null,
            status: 'running',
            progress: 0,
          },
        });

        try {
          const formattedParams = backtestService.formatBacktestParams(params);
          const response = await backtestService.runBacktest(formattedParams);
          
          if (response.success && response.data) {
            const backtestId = response.data?.data?.backtest_id;
            
            if (!backtestId) {
              set({
                error: {
                  message: 'Failed to get backtest ID',
                  code: 'BACKTEST_ID_ERROR',
                  timestamp: Date.now(),
                },
                currentBacktest: {
                  ...get().currentBacktest,
                  status: 'failed',
                },
                loadingState: {
                  isLoading: false,
                  progress: 0,
                  message: '',
                },
              });
              return;
            }
            
            set({
              currentBacktest: {
                id: backtestId,
                params,
                result: null,
                status: 'running',
                progress: 10,
              },
              loadingState: {
                isLoading: true,
                progress: 10,
                message: 'Backtest started, checking status...',
              },
            });

            // 开始轮询状态
            get().pollBacktestStatus(backtestId);
          } else {
            set({
              error: {
                message: response.message || 'Failed to start backtest',
                code: 'BACKTEST_START_ERROR',
                timestamp: Date.now(),
              },
              currentBacktest: {
                ...get().currentBacktest,
                status: 'failed',
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
              message: error instanceof Error ? error.message : 'Unknown error',
              code: 'NETWORK_ERROR',
              timestamp: Date.now(),
            },
            currentBacktest: {
              ...get().currentBacktest,
              status: 'failed',
            },
            loadingState: {
              isLoading: false,
              progress: 0,
              message: '',
            },
          });
        }
      },

      // 轮询回测状态
      pollBacktestStatus: async (backtestId: string) => {
        const pollInterval = setInterval(async () => {
          try {
            const response = await backtestService.getBacktestStatus(backtestId);
            
            if (response.success && response.data && response.data.data) {
              const status = response.data.data.status;
              const progress = response.data.data.progress;
              const message = response.data.message;
              
              set({
                currentBacktest: {
                  ...get().currentBacktest,
                  status: status as any,
                  progress: progress || 0,
                },
                loadingState: {
                  isLoading: status === 'running',
                  progress: progress || 0,
                  message: message || '',
                },
              });

              if (status === 'completed') {
                clearInterval(pollInterval);
                await get().getBacktestResult(backtestId);
              } else if (status === 'failed') {
                clearInterval(pollInterval);
                set({
                  error: {
                    message: message || 'Backtest failed',
                    code: 'BACKTEST_FAILED',
                    timestamp: Date.now(),
                  },
                  loadingState: {
                    isLoading: false,
                    progress: 0,
                    message: '',
                  },
                });
              }
            }
          } catch (error) {
            clearInterval(pollInterval);
            set({
              error: {
                message: 'Failed to check backtest status',
                code: 'STATUS_CHECK_ERROR',
                timestamp: Date.now(),
              },
              loadingState: {
                isLoading: false,
                progress: 0,
                message: '',
              },
            });
          }
        }, 2000); // 每2秒检查一次
      },

      // 检查回测状态
      checkBacktestStatus: async (backtestId: string) => {
        try {
          const response = await backtestService.getBacktestStatus(backtestId);
          
          if (response.success && response.data && response.data.data) {
            set({
              currentBacktest: {
                ...get().currentBacktest,
                status: response.data.data.status as any,
                progress: response.data.data.progress || 0,
              },
            });
          }
        } catch (error) {
          console.error('Failed to check backtest status:', error);
        }
      },

      // 获取回测结果
      getBacktestResult: async (backtestId: string) => {
        try {
          const response = await backtestService.getBacktestResult(backtestId);
          
          if (response.success && response.data) {
            set({
              currentBacktest: {
                ...get().currentBacktest,
                result: response.data,
                status: 'completed',
              },
              loadingState: {
                isLoading: false,
                progress: 100,
                message: 'Backtest completed successfully',
              },
            });

            // 自动获取交易记录
            await get().fetchTradeRecords(backtestId);
            await get().fetchPositionRecords(backtestId);
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to get backtest result',
              code: 'RESULT_FETCH_ERROR',
              timestamp: Date.now(),
            },
          });
        }
      },

      // 获取回测历史
      fetchBacktestHistory: async (page = 1, pageSize = 20) => {
        set({
          loadingState: {
            isLoading: true,
            progress: 0,
            message: 'Loading backtest history...',
          },
        });

        try {
          const response = await backtestService.getBacktestHistory();
          
          if (response.success && response.data) {
            set({
              backtestHistory: {
                items: response.data,
                total: response.data.length,
                pagination: {
                  page,
                  page_size: pageSize,
                  total: response.data.length,
                },
              },
              loadingState: {
                isLoading: false,
                progress: 100,
                message: '',
              },
            });
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to fetch backtest history',
              code: 'HISTORY_FETCH_ERROR',
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

      // 删除回测
      deleteBacktest: async (backtestId: string) => {
        try {
          const response = await backtestService.deleteBacktest(backtestId);
          
          if (response.success) {
            // 刷新历史记录
            const { pagination } = get().backtestHistory;
            await get().fetchBacktestHistory(pagination.page, pagination.page_size);
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to delete backtest',
              code: 'DELETE_ERROR',
              timestamp: Date.now(),
            },
          });
        }
      },

      // 更新策略配置
      updateStrategyConfig: (config: StrategyConfig) => {
        set({ strategyConfig: config });
      },

      // 验证策略
      validateStrategy: async (config: StrategyConfig) => {
        try {
          const response = await backtestService.validateStrategy(config);
          
          if (response.success && response.data) {
            if (!response.data.valid && response.data.errors) {
              set({
                error: {
                  message: response.data.errors.join(', '),
                  code: 'VALIDATION_ERROR',
                  timestamp: Date.now(),
                },
              });
            }
            return response.data.valid;
          }
          return false;
        } catch (error) {
          set({
            error: {
              message: 'Failed to validate strategy',
              code: 'VALIDATION_ERROR',
              timestamp: Date.now(),
            },
          });
          return false;
        }
      },

      // 保存策略
      saveStrategy: async (config: StrategyConfig) => {
        try {
          const response = await backtestService.saveStrategy(config);
          
          if (response.success) {
            set({ strategyConfig: config });
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to save strategy',
              code: 'SAVE_ERROR',
              timestamp: Date.now(),
            },
          });
        }
      },

      // 加载策略模板
      loadStrategyTemplates: async () => {
        try {
          const response = await backtestService.getStrategyTemplates();
          
          if (response.success && response.data) {
            set({ strategyTemplates: response.data });
          }
        } catch (error) {
          console.error('Failed to load strategy templates:', error);
        }
      },

      // 获取交易记录
      fetchTradeRecords: async (backtestId: string) => {
        try {
          const response = await backtestService.getTradeRecords(backtestId);
          
          if (response.success && response.data) {
            set({ tradeRecords: response.data });
          }
        } catch (error) {
          console.error('Failed to fetch trade records:', error);
        }
      },

      // 获取持仓记录
      fetchPositionRecords: async (backtestId: string) => {
        try {
          const response = await backtestService.getPositionRecords(backtestId);
          
          if (response.success && response.data) {
            set({ positionRecords: response.data });
          }
        } catch (error) {
          console.error('Failed to fetch position records:', error);
        }
      },

      // 选择回测进行比较
      selectBacktestForComparison: (backtestId: string) => {
        const { selectedBacktests } = get();
        if (!selectedBacktests.includes(backtestId) && selectedBacktests.length < 5) {
          set({
            selectedBacktests: [...selectedBacktests, backtestId],
          });
        }
      },

      // 从比较中移除回测
      removeBacktestFromComparison: (backtestId: string) => {
        const { selectedBacktests } = get();
        set({
          selectedBacktests: selectedBacktests.filter(id => id !== backtestId),
        });
      },

      // 比较回测
      compareBacktests: async () => {
        const { selectedBacktests } = get();
        
        if (selectedBacktests.length < 2) {
          set({
            error: {
              message: 'Please select at least 2 backtests to compare',
              code: 'COMPARISON_ERROR',
              timestamp: Date.now(),
            },
          });
          return;
        }

        try {
          const response = await backtestService.compareBacktests(selectedBacktests);
          
          if (response.success && response.data) {
            set({ comparisonResult: response.data });
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to compare backtests',
              code: 'COMPARISON_ERROR',
              timestamp: Date.now(),
            },
          });
        }
      },

      // 导出回测结果
      exportBacktestResult: async (backtestId: string, format: 'csv' | 'excel' | 'json') => {
        try {
          const response = await backtestService.exportBacktestResult(backtestId, format);
          
          if (response.success && response.data) {
            const filename = `backtest_${backtestId}.${format}`;
            backtestService.downloadFile(response.data, filename);
          }
        } catch (error) {
          set({
            error: {
              message: 'Failed to export backtest result',
              code: 'EXPORT_ERROR',
              timestamp: Date.now(),
            },
          });
        }
      },

      // 设置活动标签
      setActiveTab: (tab: 'overview' | 'trades' | 'positions' | 'analysis') => {
        set({ activeTab: tab });
      },

      // 切换比较模式
      toggleComparison: () => {
        set({ showComparison: !get().showComparison });
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

      // 重置当前回测
      resetCurrentBacktest: () => {
        set({
          currentBacktest: {
            id: null,
            params: null,
            result: null,
            status: 'idle',
            progress: 0,
          },
          tradeRecords: [],
          positionRecords: [],
        });
      },
    }),
    {
      name: 'backtest-store',
    }
  ));

// 选择器
export const useCurrentBacktest = () => useBacktestStore((state) => state.currentBacktest);
export const useBacktestHistory = () => useBacktestStore((state) => state.backtestHistory);
export const useStrategyConfig = () => useBacktestStore((state) => state.strategyConfig);
export const useTradeRecords = () => useBacktestStore((state) => state.tradeRecords);
export const usePositionRecords = () => useBacktestStore((state) => state.positionRecords);
export const useBacktestLoading = () => useBacktestStore((state) => state.loadingState);
export const useBacktestError = () => useBacktestStore((state) => state.error);
export const useActiveTab = () => useBacktestStore((state) => state.activeTab);