<template>
  <div class="analysis-view">
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
      <div class="navbar-left">
        <h1 class="app-title">
          <el-icon><TrendCharts /></el-icon>
          永续合约做市策略回测平台
        </h1>
      </div>

      <div class="navbar-right">
        <el-button-group>
          <el-button
            v-for="route in navRoutes"
            :key="route.name"
            :type="$route.name === route.name ? 'primary' : ''"
            size="small"
            @click="$router.push({ name: route.name })"
          >
            <el-icon><component :is="route.meta.icon" /></el-icon>
            {{ route.meta.title }}
          </el-button>
        </el-button-group>
      </div>
    </div>

    <div class="page-header">
      <h2>结果分析</h2>
      <p>深度分析回测结果，查看详细的性能指标和图表</p>
    </div>
    
    <div class="analysis-content">
      <!-- 无数据提示 -->
      <div v-if="!hasResults" class="no-data-tip">
        <el-alert
          title="暂无回测结果"
          description="请先在策略回测页面运行回测，然后返回查看分析结果"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <el-row :gutter="24" v-if="hasResults">
        <!-- 性能概览 -->
        <el-col :span="24">
          <el-card header="性能概览" class="overview-card">
            <div class="overview-metrics">
              <div class="metric-group">
                <h4>收益指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">总收益率:</span>
                    <span class="value" :class="totalReturn >= 0 ? 'text-green' : 'text-red'">
                      {{ formatPercent(totalReturn / 100) }}
                    </span>
                  </div>
                  <div class="metric-item">
                    <span class="label">胜率:</span>
                    <span class="value text-blue">{{ formatPercent(winRate) }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">交易次数:</span>
                    <span class="value">{{ formatNumber(totalTrades) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="metric-group">
                <h4>风险指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">最大回撤:</span>
                    <span class="value text-red">{{ formatPercent(maxDrawdown / 100) }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">夏普比率:</span>
                    <span class="value">{{ sharpeRatio.toFixed(2) }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">初始资金:</span>
                    <span class="value">${{ formatNumber(initialCapital) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="metric-group">
                <h4>资金指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">最终权益:</span>
                    <span class="value text-green">${{ formatNumber(finalEquity) }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">净盈亏:</span>
                    <span class="value" :class="(finalEquity - initialCapital) >= 0 ? 'text-green' : 'text-red'">
                      ${{ formatNumber(finalEquity - initialCapital) }}
                    </span>
                  </div>
                  <div class="metric-item">
                    <span class="label">回测状态:</span>
                    <span class="value text-blue">{{ hasResults ? '已完成' : '暂无数据' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 权益曲线图 -->
        <el-col :span="24">
          <el-card header="权益曲线" class="chart-card">
            <div ref="equityChartRef" class="chart-container" style="height: 400px;"></div>
          </el-card>
        </el-col>
        
        <!-- 交易分布 -->
        <el-col :span="12">
          <el-card header="交易分布" class="chart-card">
            <div ref="tradeDistributionChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <!-- 月度收益 -->
        <el-col :span="12">
          <el-card header="月度收益" class="chart-card">
            <div ref="monthlyReturnsChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <!-- 详细统计 -->
        <el-col :span="24">
          <el-card header="详细统计" class="stats-card">
            <el-table :data="detailedStats" stripe>
              <el-table-column prop="metric" label="指标" width="200" />
              <el-table-column prop="value" label="数值" />
              <el-table-column prop="description" label="说明" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useBacktestStore } from '@/stores/backtest'
import { formatPercent, formatNumber } from '@/utils/format'
import * as echarts from 'echarts'
import {
  TrendCharts,
  PieChart,
  DataLine
} from '@element-plus/icons-vue'

// 图表引用
const equityChartRef = ref(null)
const tradeDistributionChartRef = ref(null)
const monthlyReturnsChartRef = ref(null)

// 图表实例
let equityChart = null
let tradeDistributionChart = null
let monthlyReturnsChart = null

// Router
const router = useRouter()

// Store
const backtestStore = useBacktestStore()
const { currentResult } = storeToRefs(backtestStore)

// 导航路由
const navRoutes = computed(() => {
  return router.getRoutes().filter(route =>
    route.meta?.title && route.name !== 'home' && route.name !== 'login' && route.name !== 'test'
  )
})

// 计算属性 - 基于真实回测结果
const hasResults = computed(() => {
  return currentResult.value && Object.keys(currentResult.value).length > 0
})

const totalReturn = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.total_return || 0
})

const maxDrawdown = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.max_drawdown || 0
})

const sharpeRatio = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.sharpe_ratio || 0
})

const winRate = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.win_rate || 0
})

const totalTrades = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.total_trades || 0
})

const finalEquity = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.final_equity || 0
})

const initialCapital = computed(() => {
  if (!hasResults.value) return 0
  return currentResult.value.initial_capital || 10000
})

// 详细统计数据 - 基于真实回测结果
const detailedStats = computed(() => {
  if (!hasResults.value) return []

  const result = currentResult.value
  return [
    {
      metric: '初始资金',
      value: `$${formatNumber(initialCapital.value)}`,
      description: '回测开始时的初始资金'
    },
    {
      metric: '最终权益',
      value: `$${formatNumber(finalEquity.value)}`,
      description: '回测结束时的总权益'
    },
    {
      metric: '总盈亏',
      value: `${finalEquity.value >= initialCapital.value ? '+' : ''}$${formatNumber(finalEquity.value - initialCapital.value)}`,
      description: '回测期间的总盈亏金额'
    },
    {
      metric: '胜率',
      value: `${formatPercent(winRate.value)}`,
      description: '盈利交易占总交易的比例'
    },
    {
      metric: '总交易次数',
      value: `${formatNumber(totalTrades.value)} 笔`,
      description: '回测期间的总交易次数'
    },
    {
      metric: '最大回撤',
      value: `${formatPercent(maxDrawdown.value / 100)}`,
      description: '回测期间的最大资金回撤'
    },
    {
      metric: '夏普比率',
      value: `${sharpeRatio.value.toFixed(2)}`,
      description: '风险调整后的收益指标'
    },
    {
      metric: '总收益率',
      value: `${formatPercent(totalReturn.value / 100)}`,
      description: '回测期间的总收益率'
    }
  ]
})

// 初始化权益曲线图
const initEquityChart = () => {
  if (!equityChartRef.value || !hasResults.value) return

  equityChart = echarts.init(equityChartRef.value)

  const equityHistory = currentResult.value.equity_history || []
  const xData = equityHistory.map(item => new Date(item[0] * 1000).toLocaleDateString())
  const yData = equityHistory.map(item => item[1])

  const option = {
    title: {
      text: '权益曲线',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const point = params[0]
        return `时间: ${point.axisValue}<br/>权益: $${formatNumber(point.value)}`
      }
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value) => `$${formatNumber(value)}`
      }
    },
    series: [{
      name: '权益',
      type: 'line',
      data: yData,
      smooth: true,
      lineStyle: { color: '#67C23A', width: 2 },
      areaStyle: { color: 'rgba(103, 194, 58, 0.1)' }
    }],
    grid: { left: '10%', right: '10%', bottom: '15%' }
  }

  equityChart.setOption(option)
}

// 初始化交易分布图
const initTradeDistributionChart = () => {
  if (!tradeDistributionChartRef.value || !hasResults.value) return

  tradeDistributionChart = echarts.init(tradeDistributionChartRef.value)

  const profitableTrades = currentResult.value.profitable_trades || 0
  const totalTradePairs = currentResult.value.total_trade_pairs || 0
  const losingTrades = totalTradePairs - profitableTrades

  const option = {
    title: {
      text: '交易分布',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '交易分布',
      type: 'pie',
      radius: '60%',
      data: [
        { value: profitableTrades, name: '盈利交易', itemStyle: { color: '#67C23A' } },
        { value: losingTrades, name: '亏损交易', itemStyle: { color: '#F56C6C' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  tradeDistributionChart.setOption(option)
}

// 初始化月度收益图
const initMonthlyReturnsChart = () => {
  if (!monthlyReturnsChartRef.value || !hasResults.value) return

  monthlyReturnsChart = echarts.init(monthlyReturnsChartRef.value)

  // 基于权益历史计算月度收益
  const equityHistory = currentResult.value.equity_history || []
  const monthlyData = {}

  equityHistory.forEach(([timestamp, equity]) => {
    const date = new Date(timestamp * 1000)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    if (!monthlyData[monthKey]) {
      monthlyData[monthKey] = { start: equity, end: equity }
    }
    monthlyData[monthKey].end = equity
  })

  const months = Object.keys(monthlyData).sort()
  const returns = months.map(month => {
    const { start, end } = monthlyData[month]
    return ((end - start) / start * 100).toFixed(2)
  })

  const option = {
    title: {
      text: '月度收益',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const point = params[0]
        return `月份: ${point.axisValue}<br/>收益率: ${point.value}%`
      }
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '月度收益率',
      type: 'bar',
      data: returns.map(value => ({
        value: parseFloat(value),
        itemStyle: { color: parseFloat(value) >= 0 ? '#67C23A' : '#F56C6C' }
      }))
    }],
    grid: { left: '10%', right: '10%', bottom: '15%' }
  }

  monthlyReturnsChart.setOption(option)
}

// 初始化所有图表
const initAllCharts = async () => {
  await nextTick()
  if (hasResults.value) {
    initEquityChart()
    initTradeDistributionChart()
    initMonthlyReturnsChart()
  }
}

// 监听数据变化，重新初始化图表
watch(hasResults, (newVal) => {
  if (newVal) {
    initAllCharts()
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  initAllCharts()
})
</script>

<style lang="scss" scoped>
.analysis-view {
  background: var(--bg-primary);
  min-height: 100vh;
}

.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);

  .navbar-left {
    .app-title {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: 8px;

      .el-icon {
        color: var(--el-color-primary);
      }
    }
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.page-header {
  padding: 20px 24px 0;
}

.page-header {
  margin-bottom: 24px;
  
  h2 {
    margin: 0 0 8px 0;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
  }
  
  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 14px;
  }
}

.analysis-content {
  padding: 0 24px;

  .el-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    margin-bottom: 24px;
    
    :deep(.el-card__header) {
      background: var(--bg-tertiary);
      border-bottom: 1px solid var(--border-color);
      font-weight: 600;
      color: var(--text-primary);
    }
  }
}

.overview-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  
  .metric-group {
    h4 {
      margin: 0 0 16px 0;
      color: var(--text-primary);
      font-size: 16px;
      font-weight: 600;
      border-bottom: 2px solid var(--binance-yellow);
      padding-bottom: 8px;
    }
    
    .metric-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      
      .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .label {
          color: var(--text-secondary);
          font-size: 14px;
        }
        
        .value {
          color: var(--text-primary);
          font-weight: 600;
          font-size: 14px;
        }
      }
    }
  }
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.stats-card {
  :deep(.el-table) {
    background: transparent;
    
    .el-table__header {
      background: var(--bg-tertiary);
      
      th {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border-bottom: 1px solid var(--border-color);
      }
    }
    
    .el-table__body {
      tr {
        background: var(--bg-secondary);
        
        &.el-table__row--striped {
          background: var(--bg-tertiary);
        }
        
        td {
          border-bottom: 1px solid var(--border-color);
          color: var(--text-primary);
        }
      }
    }
  }
}
</style>
