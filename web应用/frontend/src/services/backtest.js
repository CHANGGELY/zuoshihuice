import api from './api'

// 回测服务
export const backtestService = {
  // 运行回测
  runBacktest: (params) => api.post('/backtest/run/', params),
  
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
