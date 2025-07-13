import api, { apiService } from './api'

// 回测服务 - 适配FastAPI后端
export const backtestService = {
  // 运行回测
  async runBacktest(params) {
    try {
      console.log('🚀 发送回测请求:', params)
      const response = await apiService.runBacktest(params)
      console.log('✅ 回测响应:', response)
      return response
    } catch (error) {
      console.error('❌ 回测请求失败:', error)
      throw error
    }
  },

  // 获取回测结果
  async getResults(backtestId) {
    try {
      const response = await apiService.getBacktestResult(backtestId)
      return response
    } catch (error) {
      console.error('❌ 获取回测结果失败:', error)
      throw error
    }
  },

  // 获取回测历史
  async getHistory(limit = 50) {
    try {
      const response = await apiService.getBacktestHistory(limit)
      return response
    } catch (error) {
      console.error('❌ 获取回测历史失败:', error)
      throw error
    }
  },

  // 删除回测结果
  async deleteResult(backtestId) {
    try {
      const response = await apiService.deleteBacktestResult(backtestId)
      return response
    } catch (error) {
      console.error('❌ 删除回测结果失败:', error)
      throw error
    }
  },

  // 获取缓存状态
  async getCacheStatus() {
    try {
      const response = await apiService.getCacheStatus()
      return response
    } catch (error) {
      console.error('❌ 获取缓存状态失败:', error)
      throw error
    }
  },

  // 清空缓存
  async clearCache() {
    try {
      const response = await apiService.clearCache()
      return response
    } catch (error) {
      console.error('❌ 清空缓存失败:', error)
      throw error
    }
  },

  // WebSocket连接
  connectWebSocket() {
    const wsUrl = 'ws://localhost:8000/ws/backtest'
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('🔌 WebSocket连接已建立')
      ws.send(JSON.stringify({
        type: 'subscribe_progress'
      }))
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📨 WebSocket消息:', data)
      } catch (error) {
        console.error('❌ WebSocket消息解析失败:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket错误:', error)
    }
    
    ws.onclose = () => {
      console.log('🔌 WebSocket连接已关闭')
    }
    
    return ws
  }
}
