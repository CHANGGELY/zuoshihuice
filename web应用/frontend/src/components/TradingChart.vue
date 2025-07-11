<template>
  <div class="trading-chart">
    <!-- 图表工具栏 -->
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="currentSymbol"
          placeholder="选择交易对"
          size="small"
          style="width: 120px"
          @change="handleSymbolChange"
        >
          <el-option
            v-for="symbol in symbols"
            :key="symbol.symbol"
            :label="symbol.name"
            :value="symbol.symbol"
          />
        </el-select>
        
        <div class="timeframe-buttons">
          <el-button-group>
            <el-button
              v-for="tf in timeframes"
              :key="tf.value"
              :type="currentTimeframe === tf.value ? 'primary' : ''"
              size="small"
              @click="handleTimeframeChange(tf.value)"
            >
              {{ tf.label }}
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <div class="toolbar-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateRangeChange"
        />
        
        <el-button
          size="small"
          :icon="Refresh"
          @click="refreshData"
          :loading="loading"
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 市场统计信息 -->
    <div class="market-stats" v-if="marketStats.symbol">
      <div class="stats-item">
        <span class="label">最新价:</span>
        <span class="value" :class="getPriceChangeClass(marketStats.price_24h_change)">
          {{ formatPrice(marketStats.last_price) }}
        </span>
      </div>
      <div class="stats-item">
        <span class="label">24h涨跌:</span>
        <span class="value" :class="getPriceChangeClass(marketStats.price_24h_change)">
          {{ formatPercent(marketStats.price_24h_change) }}
        </span>
      </div>
      <div class="stats-item">
        <span class="label">24h最高:</span>
        <span class="value">{{ formatPrice(marketStats.high_24h) }}</span>
      </div>
      <div class="stats-item">
        <span class="label">24h最低:</span>
        <span class="value">{{ formatPrice(marketStats.low_24h) }}</span>
      </div>
      <div class="stats-item">
        <span class="label">24h成交量:</span>
        <span class="value">{{ formatVolume(marketStats.volume_24h) }}</span>
      </div>
    </div>
    
    <!-- 图表容器 -->
    <div class="chart-container">
      <div ref="chartContainer" class="chart-wrapper"></div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="chart-loading">
        <el-loading-spinner />
        <span>加载中...</span>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="error" class="chart-error">
        <el-icon><Warning /></el-icon>
        <span>{{ error }}</span>
        <el-button size="small" @click="refreshData">重试</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, storeToRefs } from 'vue'
import { createChart } from 'lightweight-charts'
import { useMarketStore } from '@/stores/market'
import { Refresh, Warning } from '@element-plus/icons-vue'
import { formatPrice, formatPercent, formatVolume } from '@/utils/format'

// Props
const props = defineProps({
  height: {
    type: Number,
    default: 600
  },
  showTrades: {
    type: Boolean,
    default: false
  },
  trades: {
    type: Array,
    default: () => []
  }
})

// Store
const marketStore = useMarketStore()

// 响应式数据
const chartContainer = ref(null)
const chart = ref(null)
const candlestickSeries = ref(null)
const volumeSeries = ref(null)

// 从store获取数据
const { 
  klineData, 
  marketStats, 
  symbols, 
  timeframes, 
  loading, 
  error,
  currentSymbol,
  currentTimeframe,
  dateRange
} = storeToRefs(marketStore)

// 方法
const initChart = () => {
  if (!chartContainer.value) return
  
  // 创建图表
  chart.value = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: props.height,
    layout: {
      background: { color: '#0b0e11' },
      textColor: '#f0f3fa',
      fontSize: 12,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    grid: {
      vertLines: { color: 'rgba(43, 49, 57, 0.5)' },
      horzLines: { color: 'rgba(43, 49, 57, 0.5)' }
    },
    crosshair: {
      mode: 0, // Normal crosshair mode
      vertLine: {
        color: '#758696',
        width: 1,
        style: 2, // Dashed
        labelBackgroundColor: '#2b3139'
      },
      horzLine: {
        color: '#758696',
        width: 1,
        style: 2, // Dashed
        labelBackgroundColor: '#2b3139'
      }
    },
    timeScale: {
      borderColor: '#2b3139',
      timeVisible: true,
      secondsVisible: false
    },
    rightPriceScale: {
      borderColor: '#2b3139',
      scaleMargins: {
        top: 0.1,
        bottom: 0.2
      }
    }
  })
  
  // 创建K线系列
  candlestickSeries.value = chart.value.addCandlestickSeries({
    upColor: '#02c076',
    downColor: '#f84960',
    borderUpColor: '#02c076',
    borderDownColor: '#f84960',
    wickUpColor: '#02c076',
    wickDownColor: '#f84960'
  })
  
  // 创建成交量系列
  volumeSeries.value = chart.value.addHistogramSeries({
    color: '#26a69a',
    priceFormat: {
      type: 'volume'
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })
}

const updateChartData = () => {
  if (!chart.value || !candlestickSeries.value || !volumeSeries.value) return

  if (klineData.value && klineData.value.length > 0) {
    // 转换K线数据格式
    const candleData = klineData.value.map(item => ({
      time: item.time,
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close)
    }))

    // 转换成交量数据格式
    const volumeData = klineData.value.map(item => ({
      time: item.time,
      value: parseFloat(item.volume),
      color: parseFloat(item.close) >= parseFloat(item.open)
        ? 'rgba(2, 192, 118, 0.5)'
        : 'rgba(248, 73, 96, 0.5)'
    }))

    // 设置数据
    candlestickSeries.value.setData(candleData)
    volumeSeries.value.setData(volumeData)

    // 添加交易标记
    if (props.showTrades && props.trades.length > 0) {
      addTradeMarkers()
    }

    // 自适应时间范围
    chart.value.timeScale().fitContent()
  }
}

const addTradeMarkers = () => {
  if (!chart.value || !props.trades.length) return

  // 清除现有标记
  candlestickSeries.value.setMarkers([])

  const markers = []

  props.trades.forEach(trade => {
    const tradeTime = new Date(trade.timestamp * 1000).toISOString().slice(0, 19)

    let color, shape, position, text

    if (trade.action.includes('开多')) {
      color = '#02c076'
      shape = 'arrowUp'
      position = 'belowBar'
      text = `开多 ${trade.amount}ETH @${trade.price}`
    } else if (trade.action.includes('开空')) {
      color = '#f84960'
      shape = 'arrowDown'
      position = 'aboveBar'
      text = `开空 ${trade.amount}ETH @${trade.price}`
    } else if (trade.action.includes('平多')) {
      color = '#fcd535'
      shape = 'circle'
      position = 'aboveBar'
      text = `平多 ${trade.amount}ETH @${trade.price}`
    } else if (trade.action.includes('平空')) {
      color = '#1890ff'
      shape = 'circle'
      position = 'belowBar'
      text = `平空 ${trade.amount}ETH @${trade.price}`
    } else {
      return // 跳过未知类型的交易
    }

    markers.push({
      time: tradeTime,
      position: position,
      color: color,
      shape: shape,
      text: text,
      size: 1
    })
  })

  // 设置标记
  candlestickSeries.value.setMarkers(markers)
}

const handleSymbolChange = (symbol) => {
  marketStore.changeSymbol(symbol)
}

const handleTimeframeChange = (timeframe) => {
  marketStore.changeTimeframe(timeframe)
}

const handleDateRangeChange = (range) => {
  marketStore.setDateRange(range)
}

const refreshData = () => {
  marketStore.fetchKlineData()
  marketStore.fetchMarketStats()
}

const getPriceChangeClass = (change) => {
  if (change > 0) return 'text-green'
  if (change < 0) return 'text-red'
  return ''
}

const handleResize = () => {
  if (chart.value && chartContainer.value) {
    chart.value.applyOptions({
      width: chartContainer.value.clientWidth
    })
  }
}

// 生命周期
onMounted(async () => {
  await nextTick()
  
  // 初始化市场数据
  await marketStore.initializeData()
  
  // 初始化图表
  initChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.remove()
  }
  window.removeEventListener('resize', handleResize)
})

// 监听数据变化
watch(klineData, updateChartData, { deep: true })
</script>

<style lang="scss" scoped>
.trading-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  
  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .timeframe-buttons {
    .el-button-group {
      .el-button {
        padding: 4px 8px;
        font-size: 12px;
      }
    }
  }
}

.market-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 12px;
  
  .stats-item {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .label {
      color: var(--text-secondary);
    }
    
    .value {
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.chart-container {
  flex: 1;
  position: relative;
  
  .chart-wrapper {
    width: 100%;
    height: 100%;
  }
  
  .chart-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: var(--text-secondary);
  }
  
  .chart-error {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: var(--text-secondary);
    text-align: center;
  }
}
</style>
