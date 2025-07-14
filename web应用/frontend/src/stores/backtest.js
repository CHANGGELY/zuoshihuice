import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { backtestService } from '@/services/backtest'

export const useBacktestStore = defineStore('backtest', () => {
  // 从localStorage恢复状态
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('backtest-current-result')
      return stored ? JSON.parse(stored) : null
    } catch (e) {
      console.warn('Failed to load backtest result from localStorage:', e)
      return null
    }
  }

  // 状态
  const backtestResults = ref([])
  const currentResult = ref(loadFromStorage())
  const backtestConfigs = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 当前运行的回测
  const runningBacktests = ref(new Map())
  
  // 计算属性
  const latestResult = computed(() => {
    return backtestResults.value.length > 0 ? backtestResults.value[0] : null
  })
  
  const completedResults = computed(() => {
    return backtestResults.value.filter(result => result.status === 'completed')
  })
  
  const runningResults = computed(() => {
    return backtestResults.value.filter(result => result.status === 'running')
  })
  
  // 运行回测
  const runBacktest = async (params) => {
    try {
      loading.value = true
      error.value = null

      // 调用简单回测服务器API
      const response = await backtestService.runBacktest(params)

      // 简单回测服务器直接返回结果，不需要轮询
      if (response.success && response.result) {
        // 将结果添加到历史记录
        const backtestResult = {
          id: Date.now().toString(),
          params: params,
          result: response.result,
          status: 'completed',
          created_at: new Date().toISOString(),
          completed_at: new Date().toISOString()
        }

        backtestResults.value.unshift(backtestResult)
        currentResult.value = response.result

        return {
          success: true,
          data: response.result
        }
      } else {
        return {
          success: false,
          error: response.error || '回测失败'
        }
      }
    } catch (err) {
      error.value = err.message
      return {
        success: false,
        error: err.message
      }
    } finally {
      loading.value = false
    }
  }
  
  // 轮询回测状态
  const pollBacktestStatus = async (resultId) => {
    const maxAttempts = 300 // 最多轮询5分钟
    let attempts = 0
    
    const poll = async () => {
      try {
        if (attempts >= maxAttempts) {
          runningBacktests.value.delete(resultId)
          return
        }
        
        const response = await backtestService.getBacktestStatus(resultId)
        const status = response.data.status
        
        // 更新运行状态
        if (runningBacktests.value.has(resultId)) {
          const backtest = runningBacktests.value.get(resultId)
          backtest.status = status
          runningBacktests.value.set(resultId, backtest)
        }
        
        if (status === 'completed' || status === 'failed') {
          // 回测完成，获取结果
          await fetchBacktestResult(resultId)
          runningBacktests.value.delete(resultId)
        } else if (status === 'running') {
          // 继续轮询
          attempts++
          setTimeout(poll, 2000) // 2秒后再次轮询
        }
      } catch (err) {
        console.error('轮询回测状态失败:', err)
        runningBacktests.value.delete(resultId)
      }
    }
    
    poll()
  }
  
  // 获取回测结果列表
  const fetchBacktestResults = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await backtestService.getBacktestResults()
      backtestResults.value = response.data.results || []
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取特定回测结果
  const fetchBacktestResult = async (resultId) => {
    try {
      const response = await backtestService.getBacktestResult(resultId)
      const result = response.data
      
      // 更新当前结果
      currentResult.value = result
      
      // 更新结果列表
      const index = backtestResults.value.findIndex(r => r.id === resultId)
      if (index >= 0) {
        backtestResults.value[index] = result
      } else {
        backtestResults.value.unshift(result)
      }
      
      return result
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  // 获取回测配置
  const fetchBacktestConfigs = async () => {
    try {
      const response = await backtestService.getBacktestConfigs()
      backtestConfigs.value = response.data || []
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  // 保存回测配置
  const saveBacktestConfig = async (config) => {
    try {
      const response = await backtestService.saveBacktestConfig(config)
      
      // 更新配置列表
      backtestConfigs.value.unshift(response.data)
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  // 设置当前结果
  const setCurrentResult = (result) => {
    currentResult.value = result
    // 保存到localStorage
    try {
      if (result) {
        localStorage.setItem('backtest-current-result', JSON.stringify(result))
      } else {
        localStorage.removeItem('backtest-current-result')
      }
    } catch (e) {
      console.warn('Failed to save backtest result to localStorage:', e)
    }
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  return {
    // 状态
    backtestResults,
    currentResult,
    backtestConfigs,
    loading,
    error,
    runningBacktests,
    
    // 计算属性
    latestResult,
    completedResults,
    runningResults,
    
    // 方法
    runBacktest,
    fetchBacktestResults,
    fetchBacktestResult,
    fetchBacktestConfigs,
    saveBacktestConfig,
    setCurrentResult,
    clearError
  }
})
