import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例 - 适配简单回测服务器
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1',
  timeout: 300000, // 5分钟超时，适应回测需求
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API请求:', config.method?.toUpperCase(), config.url, config.data)

    // 添加Token认证
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('❌ 请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response
    
    // 如果响应包含success字段，检查是否成功
    if (data.hasOwnProperty('success') && !data.success) {
      const errorMessage = data.error || '请求失败'
      ElMessage.error(errorMessage)
      return Promise.reject(new Error(errorMessage))
    }
    
    return data
  },
  (error) => {
    let errorMessage = '网络错误'
    
    if (error.response) {
      // 服务器响应错误
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = data.error || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权访问，请重新登录'
          // 清除本地认证信息
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          // 可以在这里触发跳转到登录页面
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          errorMessage = '禁止访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = data.error || '服务器内部错误'
          break
        default:
          errorMessage = data.error || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 网络错误
      errorMessage = '网络连接失败，请检查网络设置'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }
    
    ElMessage.error(errorMessage)
    return Promise.reject(new Error(errorMessage))
  }
)

// API服务 - 适配简单回测服务器
export const apiService = {
  // 系统相关
  getHealthCheck: () => api.get('/health'),
  getSystemInfo: () => api.get('/'),

  // 回测相关 - 简化版本，只支持核心回测功能
  runBacktest: (params) => api.post('/backtest/run', params),

  // 注意：简单回测服务器不支持以下功能，前端需要适配
  // getBacktestResult: (resultId) => api.get(`/backtest/results/${resultId}`),
  // getBacktestHistory: (limit = 50) => api.get(`/backtest/history?limit=${limit}`),
  // deleteBacktestResult: (resultId) => api.delete(`/backtest/results/${resultId}`),
  // getCacheStatus: () => api.get('/backtest/cache/status'),
  // clearCache: () => api.post('/backtest/cache/clear'),

  // 市场数据相关 - 简单回测服务器不支持
  // getKlines: (params) => api.get('/market/klines', { params }),
  // getMarketStats: () => api.get('/market/stats'),
  // getSymbols: () => api.get('/market/symbols'),
  // getTimeframes: () => api.get('/market/timeframes'),

  // 认证相关 - 简单回测服务器不支持
  // login: (credentials) => api.post('/auth/login', credentials),
  // logout: () => api.post('/auth/logout'),
  // getProfile: () => api.get('/auth/profile'),
  // getPermissions: () => api.get('/auth/permissions'),
}

export default api
