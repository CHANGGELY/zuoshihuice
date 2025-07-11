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
      <div class="chart-container">
        <div class="chart-header">
          <h2>K线图表</h2>
          <div class="chart-controls">
            <el-select v-model="selectedTimeframe" @change="changeTimeframe" size="small">
              <el-option label="1分钟" value="1m" />
              <el-option label="5分钟" value="5m" />
              <el-option label="15分钟" value="15m" />
              <el-option label="1小时" value="1h" />
              <el-option label="4小时" value="4h" />
              <el-option label="1天" value="1d" />
            </el-select>
            <el-button @click="refreshChart" size="small">刷新</el-button>
          </div>
        </div>
        <div ref="chartContainer" class="chart-content"></div>
      </div>
      
      <div class="info-panel">
        <h3>市场信息</h3>
        <div class="market-info">
          <p><strong>交易对：</strong>ETH/USDC</p>
          <p><strong>当前价格：</strong>$3,456.78</p>
          <p><strong>24h涨跌：</strong><span class="text-green">+2.34%</span></p>
          <p><strong>24h成交量：</strong>1,234,567 ETH</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createChart } from 'lightweight-charts'

const router = useRouter()
const chartContainer = ref()
const selectedTimeframe = ref('1h')

let chart = null
let candlestickSeries = null

// 模拟K线数据
const generateMockData = () => {
  const data = []
  const basePrice = 3456.78
  let currentPrice = basePrice
  const now = new Date()

  for (let i = 100; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000) // 每小时一根K线
    const change = (Math.random() - 0.5) * 100 // 随机变化

    const open = currentPrice
    const close = open + change
    const high = Math.max(open, close) + Math.random() * 50
    const low = Math.min(open, close) - Math.random() * 50

    data.push({
      time: Math.floor(time.getTime() / 1000),
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2))
    })

    currentPrice = close
  }

  return data.sort((a, b) => a.time - b.time)
}

const initChart = () => {
  if (!chartContainer.value) return

  // 创建图表
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#ffffff' },
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
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

  // 创建K线系列
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#02c076',
    downColor: '#f84960',
    borderDownColor: '#f84960',
    borderUpColor: '#02c076',
    wickDownColor: '#f84960',
    wickUpColor: '#02c076',
  })

  // 设置数据
  const data = generateMockData()
  candlestickSeries.setData(data)

  // 自适应大小
  chart.timeScale().fitContent()
}

const changeTimeframe = (timeframe) => {
  ElMessage.info(`切换到 ${timeframe} 时间周期`)
  // 这里可以重新加载对应时间周期的数据
  refreshChart()
}

const refreshChart = () => {
  if (candlestickSeries) {
    const newData = generateMockData()
    candlestickSeries.setData(newData)
    chart.timeScale().fitContent()
    ElMessage.success('图表已刷新')
  }
}

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}

// 响应式调整图表大小
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.applyOptions({
      width: chartContainer.value.clientWidth,
    })
  }
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

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chart-content {
  width: 100%;
  height: 400px;
  border-radius: 4px;
  overflow: hidden;
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
