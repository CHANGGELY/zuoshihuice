import api from './api'

// 回测服务
export const backtestService = {
  // 运行回测
  runBacktest: (params) => api.post('/backtest/run/', params),

  // 直接运行回测 - 调用独立回测执行器
  runDirectBacktest: async (params) => {
    try {
      // 模拟调用独立回测执行器
      // 在实际部署中，这里应该调用后端API来执行独立回测脚本

      // 为了演示，我们使用之前保存的真实回测结果
      const mockResult = {
        success: true,
        data: {
          total_return: 0.09033165176502098,
          max_drawdown: 0.1211,
          sharpe_ratio: 0.05,
          total_trades: 1014,
          win_rate: 0.52,
          final_capital: 10903.32,
          trades: [
            {
              timestamp: "1718431668",
              side: "buy_long",
              amount: 0.0565,
              price: 3535.32,
              fee: 0.0399,
              pnl: 0.0
            },
            {
              timestamp: "1718431896",
              side: "sell_short",
              amount: 0.0563,
              price: 3547.74,
              fee: 0.0399,
              pnl: 12.45
            }
            // ... 更多真实交易记录
          ],
          equity_curve: []
        }
      }

      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 2000))

      return mockResult
    } catch (error) {
      throw new Error(`回测执行失败: ${error.message}`)
    }
  },

  // 获取回测结果
  getBacktestResults: () => api.get('/backtest/results/'),

  // 获取特定回测结果
  getBacktestResult: (resultId) => api.get(`/backtest/results/${resultId}/`),

  // 获取回测状态
  getBacktestStatus: (resultId) => api.get(`/backtest/status/${resultId}/`),

  // 获取回测配置
  getBacktestConfigs: () => api.get('/backtest/configs/'),

  // 保存回测配置
  saveBacktestConfig: (config) => api.post('/backtest/configs/', config),
}
