<template>
  <div class="backtest-kline-chart">
    <div class="chart-header">
      <h4>回测K线图表</h4>
      <div class="chart-controls">
        <el-select v-model="selectedTimeframe" size="small" style="width: 100px" @change="loadKlineData">
          <el-option label="1分钟" value="1m" />
          <el-option label="5分钟" value="5m" />
          <el-option label="15分钟" value="15m" />
          <el-option label="1小时" value="1h" />
          <el-option label="4小时" value="4h" />
          <el-option label="1天" value="1d" />
        </el-select>
        <el-button size="small" @click="loadKlineData" :loading="loading">
          刷新数据
        </el-button>
      </div>
    </div>
    
    <div class="chart-container" ref="chartContainer"></div>
    
    <!-- 图例 -->
    <div class="chart-legend">
      <div class="legend-item">
        <span class="legend-color" style="background: #67C23A;"></span>
        <span>开多 ({{ openLongCount }})</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #E6A23C;"></span>
        <span>平多 ({{ closeLongCount }})</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #F56C6C;"></span>
        <span>开空 ({{ openShortCount }})</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #409EFF;"></span>
        <span>平空 ({{ closeShortCount }})</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { createChart } from 'lightweight-charts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  trades: {
    type: Array,
    default: () => []
  },
  dateRange: {
    type: Array,
    default: () => []
  },
  symbol: {
    type: String,
    default: 'ETH/USDC'
  }
})

const chartContainer = ref(null)
const selectedTimeframe = ref('1h')
const loading = ref(false)
const klineData = ref([])
let chart = null
let candlestickSeries = null
let tradeMarkers = []

// 计算交易数量
const openLongCount = computed(() => props.trades.filter(t => isOpenLong(t.action || t.type)).length)
const closeLongCount = computed(() => props.trades.filter(t => isCloseLong(t.action || t.type)).length)
const openShortCount = computed(() => props.trades.filter(t => isOpenShort(t.action || t.type)).length)
const closeShortCount = computed(() => props.trades.filter(t => isCloseShort(t.action || t.type)).length)

// 判断交易类型
const isOpenLong = (action) => {
  return action && (action.includes('开多') || action.includes('open_long') || action.includes('buy_long'))
}

const isCloseLong = (action) => {
  return action && (action.includes('平多') || action.includes('close_long') || action.includes('sell_long'))
}

const isOpenShort = (action) => {
  return action && (action.includes('开空') || action.includes('open_short') || action.includes('sell_short'))
}

const isCloseShort = (action) => {
  return action && (action.includes('平空') || action.includes('close_short') || action.includes('buy_short'))
}

// 获取交易标记颜色和形状
const getTradeMarker = (trade) => {
  const action = trade.action || trade.type
  let timestamp = trade.timestamp
  const price = trade.price

  // 确保时间戳格式正确（lightweight-charts期望Unix时间戳）
  if (timestamp && timestamp > 1000000000000) {
    // 如果是毫秒时间戳，转换为秒
    timestamp = Math.floor(timestamp / 1000)
  }

  console.log('处理交易标记:', { action, timestamp, price })

  if (isOpenLong(action)) {
    return {
      time: timestamp,
      position: 'belowBar',
      color: '#67C23A',
      shape: 'arrowUp',
      text: '开多',
      size: 1
    }
  } else if (isCloseLong(action)) {
    return {
      time: timestamp,
      position: 'aboveBar',
      color: '#E6A23C',
      shape: 'arrowDown',
      text: '平多',
      size: 1
    }
  } else if (isOpenShort(action)) {
    return {
      time: timestamp,
      position: 'aboveBar',
      color: '#F56C6C',
      shape: 'arrowDown',
      text: '开空',
      size: 1
    }
  } else if (isCloseShort(action)) {
    return {
      time: timestamp,
      position: 'belowBar',
      color: '#409EFF',
      shape: 'arrowUp',
      text: '平空',
      size: 1
    }
  }

  return null
}

// 加载K线数据
const loadKlineData = async () => {
  try {
    loading.value = true
    
    const params = {
      timeframe: selectedTimeframe.value,
      limit: 2000
    }
    
    // 如果有日期范围，添加时间过滤
    if (props.dateRange && props.dateRange.length === 2) {
      params.start_time = props.dateRange[0] + ' 00:00:00'
      params.end_time = props.dateRange[1] + ' 23:59:59'
    }
    
    const response = await axios.get('/api/market-data/local-klines/', { params })
    
    if (response.data.success) {
      klineData.value = response.data.data
      updateChart()
    } else {
      ElMessage.error('获取K线数据失败')
    }
  } catch (error) {
    console.error('加载K线数据失败:', error)
    ElMessage.error('加载K线数据失败')
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return
  
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 500,
    layout: {
      backgroundColor: '#ffffff',
      textColor: '#333',
    },
    grid: {
      vertLines: {
        color: '#f0f0f0',
      },
      horzLines: {
        color: '#f0f0f0',
      },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      borderColor: '#cccccc',
    },
    timeScale: {
      borderColor: '#cccccc',
      timeVisible: true,
      secondsVisible: false,
    },
  })
  
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  })
}

// 更新图表
const updateChart = () => {
  if (!chart || !candlestickSeries) return
  
  // 设置K线数据
  const chartData = klineData.value.map(item => ({
    time: item.time,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close
  }))
  
  candlestickSeries.setData(chartData)
  
  // 添加交易标记
  updateTradeMarkers()
}

// 更新交易标记
const updateTradeMarkers = () => {
  if (!candlestickSeries) {
    console.warn('K线图表未初始化，无法添加交易标记')
    return
  }

  if (!props.trades.length) {
    console.log('没有交易数据，清空交易标记')
    candlestickSeries.setMarkers([])
    return
  }

  console.log(`开始处理 ${props.trades.length} 条交易记录`)
  const markers = []

  props.trades.forEach((trade, index) => {
    const marker = getTradeMarker(trade)
    if (marker) {
      markers.push(marker)
      console.log(`交易 ${index + 1}: ${trade.action} 标记已添加`)
    } else {
      console.warn(`交易 ${index + 1}: ${trade.action} 无法识别，跳过`)
    }
  })

  console.log(`总共生成 ${markers.length} 个交易标记`)
  candlestickSeries.setMarkers(markers)
  tradeMarkers = markers
}

// 监听窗口大小变化
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth
    })
  }
}

// 监听交易数据变化
watch(() => props.trades, () => {
  updateTradeMarkers()
}, { deep: true })

// 监听日期范围变化
watch(() => props.dateRange, () => {
  loadKlineData()
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initChart()
    loadKlineData()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.backtest-kline-chart {
  width: 100%;
  margin-top: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h4 {
    margin: 0;
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 600;
  }
  
  .chart-controls {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}

.chart-container {
  width: 100%;
  height: 500px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #fff;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-secondary);
    
    .legend-color {
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }
  }
}
</style>
