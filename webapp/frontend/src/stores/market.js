import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { marketService } from '@/services/market'

export const useMarketStore = defineStore('market', () => {
  // 状态
  const klineData = ref([])
  const marketStats = ref({})
  const symbols = ref([])
  const timeframes = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 当前选择
  const currentSymbol = ref('ETHUSDT')
  const currentTimeframe = ref('1m')
  const dateRange = ref([])
  
  // 计算属性
  const currentSymbolInfo = computed(() => {
    return symbols.value.find(s => s.symbol === currentSymbol.value) || {}
  })
  
  const currentTimeframeInfo = computed(() => {
    return timeframes.value.find(t => t.value === currentTimeframe.value) || {}
  })
  
  // 获取K线数据
  const fetchKlineData = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const requestParams = {
        symbol: currentSymbol.value,
        timeframe: currentTimeframe.value,
        limit: 1000,
        ...params
      }
      
      // 如果有日期范围，添加到参数中
      if (dateRange.value && dateRange.value.length === 2) {
        requestParams.start_date = dateRange.value[0]
        requestParams.end_date = dateRange.value[1]
      }
      
      const response = await marketService.getKlineData(requestParams)
      klineData.value = response.data.klines || []
      
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('获取K线数据失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取市场统计
  const fetchMarketStats = async (symbol = currentSymbol.value) => {
    try {
      const response = await marketService.getMarketStats({ symbol })
      marketStats.value = response.data
      return response.data
    } catch (err) {
      console.error('获取市场统计失败:', err)
      throw err
    }
  }
  
  // 获取支持的交易对
  const fetchSymbols = async () => {
    try {
      const response = await marketService.getSymbols()
      symbols.value = response.data || []
      return response.data
    } catch (err) {
      console.error('获取交易对失败:', err)
      throw err
    }
  }
  
  // 获取支持的时间周期
  const fetchTimeframes = async () => {
    try {
      const response = await marketService.getTimeframes()
      timeframes.value = response.data || []
      return response.data
    } catch (err) {
      console.error('获取时间周期失败:', err)
      throw err
    }
  }
  
  // 切换交易对
  const changeSymbol = async (symbol) => {
    if (symbol !== currentSymbol.value) {
      currentSymbol.value = symbol
      await Promise.all([
        fetchKlineData(),
        fetchMarketStats(symbol)
      ])
    }
  }
  
  // 切换时间周期
  const changeTimeframe = async (timeframe) => {
    if (timeframe !== currentTimeframe.value) {
      currentTimeframe.value = timeframe
      await fetchKlineData()
    }
  }
  
  // 设置日期范围
  const setDateRange = async (range) => {
    dateRange.value = range
    await fetchKlineData()
  }
  
  // 初始化数据
  const initializeData = async () => {
    try {
      await Promise.all([
        fetchSymbols(),
        fetchTimeframes()
      ])
      
      // 获取初始数据
      await Promise.all([
        fetchKlineData(),
        fetchMarketStats()
      ])
    } catch (err) {
      console.error('初始化市场数据失败:', err)
    }
  }
  
  return {
    // 状态
    klineData,
    marketStats,
    symbols,
    timeframes,
    loading,
    error,
    currentSymbol,
    currentTimeframe,
    dateRange,
    
    // 计算属性
    currentSymbolInfo,
    currentTimeframeInfo,
    
    // 方法
    fetchKlineData,
    fetchMarketStats,
    fetchSymbols,
    fetchTimeframes,
    changeSymbol,
    changeTimeframe,
    setDateRange,
    initializeData
  }
})
