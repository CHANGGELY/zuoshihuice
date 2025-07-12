<template>
  <div class="backtest-trading-chart">
    <div class="chart-header">
      <h4>交易位置图表</h4>
      <div class="chart-controls">
        <el-button-group size="small">
          <el-button 
            :type="chartType === 'equity' ? 'primary' : ''"
            @click="chartType = 'equity'"
          >
            权益曲线
          </el-button>
          <el-button 
            :type="chartType === 'trades' ? 'primary' : ''"
            @click="chartType = 'trades'"
          >
            交易位置
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <div class="chart-container">
      <!-- 权益曲线图 -->
      <div v-if="chartType === 'equity'" ref="equityChartRef" class="chart-canvas"></div>
      
      <!-- 交易位置图 -->
      <div v-if="chartType === 'trades'" ref="tradesChartRef" class="chart-canvas"></div>
    </div>
    
    <!-- 图例 -->
    <div class="chart-legend">
      <div class="legend-item">
        <span class="legend-color" style="background: #67C23A;"></span>
        <span>开多</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #E6A23C;"></span>
        <span>平多</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #F56C6C;"></span>
        <span>开空</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background: #409EFF;"></span>
        <span>平空</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  trades: {
    type: Array,
    default: () => []
  },
  equityCurve: {
    type: Array,
    default: () => []
  },
  symbol: {
    type: String,
    default: 'ETH/USDC'
  },
  dateRange: {
    type: Array,
    default: () => []
  }
})

const chartType = ref('equity')
const equityChartRef = ref(null)
const tradesChartRef = ref(null)
let equityChart = null
let tradesChart = null

// 初始化权益曲线图
const initEquityChart = () => {
  if (!equityChartRef.value || !props.equityCurve.length) return
  
  equityChart = echarts.init(equityChartRef.value)
  
  const option = {
    title: {
      text: '权益曲线',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `时间: ${data.name}<br/>权益: $${data.value.toFixed(2)}`
      }
    },
    xAxis: {
      type: 'category',
      data: props.equityCurve.map(item => {
        const date = new Date(item.timestamp * 1000)
        return date.toLocaleDateString()
      }),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '权益 (USDC)',
      axisLabel: {
        formatter: '${value}'
      }
    },
    series: [{
      name: '权益',
      type: 'line',
      data: props.equityCurve.map(item => item.equity),
      smooth: true,
      lineStyle: {
        color: '#409EFF',
        width: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(64, 158, 255, 0.3)'
          }, {
            offset: 1, color: 'rgba(64, 158, 255, 0.1)'
          }]
        }
      }
    }],
    grid: {
      left: '10%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    }
  }
  
  equityChart.setOption(option)
}

// 初始化交易位置图
const initTradesChart = () => {
  if (!tradesChartRef.value || !props.trades.length) return
  
  tradesChart = echarts.init(tradesChartRef.value)
  
  // 处理交易数据
  const tradeData = props.trades.map(trade => ({
    timestamp: trade.timestamp,
    price: trade.price,
    type: trade.type,
    amount: trade.amount,
    time: new Date(trade.timestamp * 1000).toLocaleString()
  }))
  
  // 按类型分组
  const openLong = tradeData.filter(t => t.type.includes('long') && (t.type.includes('open') || t.type.includes('buy')))
  const closeLong = tradeData.filter(t => t.type.includes('long') && (t.type.includes('close') || t.type.includes('sell')))
  const openShort = tradeData.filter(t => t.type.includes('short') && (t.type.includes('open') || t.type.includes('sell')))
  const closeShort = tradeData.filter(t => t.type.includes('short') && (t.type.includes('close') || t.type.includes('buy')))
  
  const option = {
    title: {
      text: '交易位置分布',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const data = params.data[2]
        return `时间: ${data.time}<br/>类型: ${getTradeTypeName(data.type)}<br/>价格: $${data.price.toFixed(2)}<br/>数量: ${data.amount.toFixed(4)} ETH`
      }
    },
    xAxis: {
      type: 'time',
      name: '时间',
      axisLabel: {
        formatter: function(value) {
          return new Date(value).toLocaleDateString()
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '价格 (USDC)',
      axisLabel: {
        formatter: '${value}'
      }
    },
    series: [
      {
        name: '开多',
        type: 'scatter',
        data: openLong.map(t => [t.timestamp * 1000, t.price, t]),
        symbolSize: 8,
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '平多',
        type: 'scatter',
        data: closeLong.map(t => [t.timestamp * 1000, t.price, t]),
        symbolSize: 8,
        itemStyle: {
          color: '#E6A23C'
        }
      },
      {
        name: '开空',
        type: 'scatter',
        data: openShort.map(t => [t.timestamp * 1000, t.price, t]),
        symbolSize: 8,
        itemStyle: {
          color: '#F56C6C'
        }
      },
      {
        name: '平空',
        type: 'scatter',
        data: closeShort.map(t => [t.timestamp * 1000, t.price, t]),
        symbolSize: 8,
        itemStyle: {
          color: '#409EFF'
        }
      }
    ],
    grid: {
      left: '10%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    legend: {
      data: ['开多', '平多', '开空', '平空'],
      bottom: 10
    }
  }
  
  tradesChart.setOption(option)
}

// 获取交易类型名称
const getTradeTypeName = (type) => {
  const nameMap = {
    'open_long': '开多',
    'close_long': '平多',
    'open_short': '开空',
    'close_short': '平空',
    'buy_long': '开多',
    'sell_long': '平多',
    'sell_short': '开空',
    'buy_short': '平空'
  }
  return nameMap[type] || type
}

// 监听图表类型变化
watch(chartType, async (newType) => {
  await nextTick()
  if (newType === 'equity') {
    initEquityChart()
  } else {
    initTradesChart()
  }
})

// 监听数据变化
watch(() => props.trades, () => {
  if (chartType.value === 'trades') {
    nextTick(() => initTradesChart())
  }
}, { deep: true })

watch(() => props.equityCurve, () => {
  if (chartType.value === 'equity') {
    nextTick(() => initEquityChart())
  }
}, { deep: true })

// 监听窗口大小变化
const handleResize = () => {
  if (equityChart) equityChart.resize()
  if (tradesChart) tradesChart.resize()
}

onMounted(() => {
  nextTick(() => {
    initEquityChart()
  })
  window.addEventListener('resize', handleResize)
})

// 清理
onUnmounted(() => {
  if (equityChart) equityChart.dispose()
  if (tradesChart) tradesChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.backtest-trading-chart {
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
}

.chart-container {
  width: 100%;
  height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #fff;
}

.chart-canvas {
  width: 100%;
  height: 100%;
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
