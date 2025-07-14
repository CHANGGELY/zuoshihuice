<template>
  <div class="trading-view">
    <div class="header">
      <h1>交易图表</h1>
      <div class="nav-buttons">
        <el-button @click="$router.push('/backtest')">策略回测</el-button>
        <el-button @click="$router.push('/analysis')">结果分析</el-button>
        <el-button @click="$router.push('/settings')">系统设置</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    
    <div class="content">
      <div class="chart-section">
        <h2>K线图表</h2>
        <div class="chart-controls">
          <el-select v-model="selectedTimeframe" @change="changeTimeframe" placeholder="选择时间周期">
            <el-option
              v-for="tf in timeframes"
              :key="tf.value"
              :label="tf.label"
              :value="tf.value"
            />
          </el-select>
          <el-button @click="refreshData">刷新</el-button>
        </div>

        <div class="chart-container">
          <div ref="chartContainer" style="width: 100%; height: 400px;"></div>

          <!-- 鼠标悬停信息 -->
          <div v-if="hoverInfo.visible" class="hover-info">
            <div class="hover-info-header">
              <strong>{{ hoverInfo.time }}</strong>
            </div>
            <div class="hover-info-content">
              <div class="info-row">
                <span>开盘:</span>
                <span>${{ hoverInfo.open.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>最高:</span>
                <span>${{ hoverInfo.high.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>最低:</span>
                <span>${{ hoverInfo.low.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>收盘:</span>
                <span>${{ hoverInfo.close.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>成交量:</span>
                <span>{{ hoverInfo.volume.toFixed(4) }} ETH</span>
              </div>
              <div class="info-row">
                <span>成交额:</span>
                <span>${{ hoverInfo.turnover.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>VWAP:</span>
                <span>${{ hoverInfo.vwap.toFixed(2) }}</span>
              </div>
              <div class="info-row">
                <span>涨跌幅:</span>
                <span :class="hoverInfo.priceChangePct >= 0 ? 'text-green' : 'text-red'">
                  {{ hoverInfo.priceChangePct >= 0 ? '+' : '' }}{{ hoverInfo.priceChangePct.toFixed(2) }}%
                </span>
              </div>
              <div class="info-row">
                <span>振幅:</span>
                <span>{{ hoverInfo.amplitude.toFixed(2) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="info-panel">
        <h2>市场信息</h2>
        <div class="market-info">
          <p><strong>交易对:</strong> {{ marketInfo.symbol }}</p>
          <p><strong>当前价格:</strong> ${{ marketInfo.price.toFixed(2) }}</p>
          <p><strong>24h涨跌:</strong>
            <span :class="marketInfo.changePercent >= 0 ? 'text-green' : 'text-red'">
              {{ marketInfo.changePercent >= 0 ? '+' : '' }}{{ marketInfo.changePercent.toFixed(2) }}%
            </span>
          </p>
          <p><strong>24h成交量:</strong> {{ marketInfo.volume24h.toLocaleString() }} ETH</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createChart } from 'lightweight-charts'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const chartContainer = ref(null)
const selectedTimeframe = ref('1h')
let chart = null
let candlestickSeries = null

const timeframes = [
  { label: '1分钟', value: '1m' },
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '1小时', value: '1h' },
  { label: '4小时', value: '4h' },
  { label: '1天', value: '1d' }
]

const marketInfo = ref({
  symbol: 'ETH/USDC',
  price: 3456.78,
  change: 82.34,
  changePercent: 2.34,
  volume24h: 1234567,
  high24h: 3500.00,
  low24h: 3400.00
})

// 鼠标悬停信息
const hoverInfo = ref({
  visible: false,
  time: '',
  open: 0,
  high: 0,
  low: 0,
  close: 0,
  volume: 0,
  turnover: 0,
  vwap: 0,
  priceChange: 0,
  priceChangePct: 0,
  amplitude: 0
})

// 获取真实K线数据
const fetchKlineData = async () => {
  try {
    const response = await axios.get('/api/market-data/local-klines/', {
      params: {
        timeframe: selectedTimeframe.value,
        limit: 1000
      }
    })

    if (response.data.success) {
      const klineData = response.data.data.map(item => ({
        time: item.time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume,
        turnover: item.turnover,
        vwap: item.vwap,
        priceChange: item.price_change,
        priceChangePct: item.price_change_pct,
        amplitude: item.amplitude
      }))

      if (candlestickSeries && klineData.length > 0) {
        candlestickSeries.setData(klineData)

        // 更新市场信息
        const latest = klineData[klineData.length - 1]
        marketInfo.value = {
          symbol: 'ETH/USDC',
          price: latest.close,
          change: latest.priceChange,
          changePercent: latest.priceChangePct,
          volume24h: klineData.slice(-1440).reduce((sum, item) => sum + item.volume, 0),
          high24h: Math.max(...klineData.slice(-1440).map(item => item.high)),
          low24h: Math.min(...klineData.slice(-1440).map(item => item.low))
        }
      }
    }
  } catch (error) {
    console.error('获取K线数据失败:', error)
    ElMessage.error('获取K线数据失败')
  }
}

// 初始化图表
const initChart = async () => {
  await nextTick()

  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#ffffff' },
      textColor: '#333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    crosshair: {
      mode: 1,
    },
    timeScale: {
      borderColor: '#cccccc',
      timeVisible: true,
      secondsVisible: false,
    },
    rightPriceScale: {
      borderColor: '#cccccc',
    },
  })

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#02c076',
    downColor: '#ff4757',
    borderDownColor: '#ff4757',
    borderUpColor: '#02c076',
    wickDownColor: '#ff4757',
    wickUpColor: '#02c076',
  })

  // 添加鼠标悬停事件
  chart.subscribeCrosshairMove((param) => {
    if (param.point === undefined || !param.time || param.point.x < 0 || param.point.y < 0) {
      hoverInfo.value.visible = false
      return
    }

    const data = param.seriesData.get(candlestickSeries)
    if (data) {
      const time = new Date(param.time * 1000)
      hoverInfo.value = {
        visible: true,
        time: time.toLocaleString('zh-CN'),
        open: data.open,
        high: data.high,
        low: data.low,
        close: data.close,
        volume: data.volume || 0,
        turnover: data.turnover || 0,
        vwap: data.vwap || 0,
        priceChange: data.priceChange || 0,
        priceChangePct: data.priceChangePct || 0,
        amplitude: data.amplitude || 0
      }
    }
  })

  // 加载数据
  await fetchKlineData()
}

// 切换时间周期
const changeTimeframe = async (timeframe) => {
  selectedTimeframe.value = timeframe
  await fetchKlineData()
}

// 刷新数据
const refreshData = async () => {
  await fetchKlineData()
  ElMessage.success('数据已刷新')
}

// 窗口大小调整
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth,
    })
  }
}

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.trading-view {
  padding: 20px;
  height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-buttons {
  display: flex;
  gap: 10px;
}

.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  height: calc(100vh - 140px);
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.chart-container {
  position: relative;
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
}

.hover-info {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-size: 12px;
  z-index: 1000;
  min-width: 200px;
}

.hover-info-header {
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #eee;
  font-size: 13px;
  color: #333;
}

.hover-info-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-row span:first-child {
  color: #666;
  font-weight: 500;
}

.info-row span:last-child {
  font-weight: 600;
  color: #333;
}

.info-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.market-info p {
  margin: 10px 0;
  font-size: 14px;
}

.text-green {
  color: #02c076;
}

h1 {
  color: #333;
  margin: 0;
}

h2, h3 {
  color: #333;
  margin-top: 0;
}
</style>
