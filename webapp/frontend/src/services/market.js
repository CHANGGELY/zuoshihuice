import api from './api'

// 市场数据服务
export const marketService = {
  // 获取K线数据
  getKlineData: (params) => api.get('/market/klines/', { params }),
  
  // 获取市场统计
  getMarketStats: (params) => api.get('/market/stats/', { params }),
  
  // 获取支持的时间周期
  getTimeframes: () => api.get('/market/timeframes/'),
  
  // 获取支持的交易对
  getSymbols: () => api.get('/market/symbols/'),
}
