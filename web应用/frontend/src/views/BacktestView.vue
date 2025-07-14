<template>
  <div class="backtest-view">
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
      <h2>策略回测</h2>
      <p>配置回测参数，运行永续合约做市策略回测</p>
    </div>
    
    <div class="backtest-content">
      <!-- 参数配置面板 -->
      <div class="config-panel">
        <el-card header="回测参数配置">
          <el-form :model="backtestParams" label-width="120px" size="small">
            <el-form-item label="交易对">
              <el-select v-model="backtestParams.symbol" placeholder="选择交易对">
                <el-option
                  v-for="symbol in symbols"
                  :key="symbol.symbol"
                  :label="symbol.name"
                  :value="symbol.symbol"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="回测时间">
              <el-date-picker
                v-model="backtestParams.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <el-form-item label="初始资金">
              <el-input-number
                v-model="backtestParams.initialCapital"
                :min="1000"
                :max="1000000"
                :step="1000"
                controls-position="right"
              />
              <span class="unit">USDC</span>
            </el-form-item>
            
            <el-form-item label="杠杆倍数">
              <el-input-number
                v-model="backtestParams.leverage"
                :min="1"
                :max="125"
                :step="1"
                controls-position="right"
              />
              <span class="unit">倍</span>
            </el-form-item>
            
            <el-form-item label="价差阈值">
              <el-input-number
                v-model="backtestParams.spreadThreshold"
                :min="0.001"
                :max="0.01"
                :step="0.001"
                :precision="3"
                controls-position="right"
              />
              <span class="unit">%</span>
            </el-form-item>
            
            <el-form-item label="仓位比例">
              <el-input-number
                v-model="backtestParams.positionRatio"
                :min="0.1"
                :max="1.0"
                :step="0.1"
                :precision="1"
                controls-position="right"
              />
              <span class="unit">%</span>
            </el-form-item>
            
            <el-form-item label="订单比例">
              <el-input-number
                v-model="backtestParams.orderRatio"
                :min="0.01"
                :max="0.1"
                :step="0.01"
                :precision="2"
                controls-position="right"
              />
              <span class="unit">%</span>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="backtestLoading"
                @click="runBacktest"
                :disabled="!canRunBacktest"
              >
                <el-icon><VideoPlay /></el-icon>
                {{ backtestLoading ? '回测中...' : '开始回测' }}
              </el-button>
              
              <el-button @click="resetParams">
                <el-icon><Refresh /></el-icon>
                重置参数
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
      
      <!-- 结果展示面板 -->
      <div class="results-panel">
        <el-card header="回测结果">
          <div v-if="!backtestResults" class="no-results">
            <el-empty description="暂无回测结果，请先运行回测" />
          </div>
          
          <div v-else class="results-content">
            <!-- 核心指标 -->
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-label">总收益率</div>
                <div class="metric-value" :class="getPriceChangeClass(backtestResults.total_return)">
                  {{ formatPercent(backtestResults.total_return * 100) }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">最终权益</div>
                <div class="metric-value">
                  {{ formatNumber(backtestResults.final_equity) }} USDC
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">总交易次数</div>
                <div class="metric-value">
                  {{ backtestResults.total_trades }} 笔
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">胜率</div>
                <div class="metric-value">
                  {{ formatPercent(backtestResults.win_rate) }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value text-red">
                  {{ formatPercent(backtestResults.max_drawdown * 100) }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">
                  {{ formatNumber(backtestResults.sharpe_ratio, '0.00') }}
                </div>
              </div>
            </div>
            
            <!-- 调试信息 -->
            <div v-if="backtestResults" style="margin: 20px 0; padding: 10px; background: #f0f8ff; border: 1px solid #ccc; border-radius: 4px;">
              <h4>🔍 调试信息</h4>
              <p><strong>回测结果存在:</strong> {{ !!backtestResults }}</p>
              <p><strong>trades字段存在:</strong> {{ backtestResults && 'trades' in backtestResults }}</p>
              <p><strong>trades类型:</strong> {{ backtestResults && backtestResults.trades ? typeof backtestResults.trades : 'N/A' }}</p>
              <p><strong>trades长度:</strong> {{ backtestResults && backtestResults.trades ? backtestResults.trades.length : 'N/A' }}</p>
              <p><strong>hasValidTrades:</strong> {{ hasValidTrades }}</p>
              <p><strong>trades前3条:</strong></p>
              <pre v-if="backtestResults && backtestResults.trades">{{ JSON.stringify(backtestResults.trades.slice(0, 3), null, 2) }}</pre>
            </div>

            <!-- K线图表 -->
            <div class="trading-chart-section" v-if="hasValidTrades">
              <h3>回测K线图表</h3>
              <div class="chart-container">
                <BacktestKlineChart
                  :trades="backtestResults.trades"
                  :date-range="backtestParams.dateRange"
                  :symbol="backtestParams.symbol"
                />
              </div>
            </div>

            <!-- 交易图表 -->
            <div class="trading-chart-section" v-if="hasValidTrades">
              <h3>交易位置图表</h3>
              <div class="chart-container">
                <BacktestTradingChart
                  :trades="backtestResults.trades"
                  :equity-curve="backtestResults.equity_curve"
                  :symbol="backtestParams.symbol"
                  :date-range="backtestParams.dateRange"
                />
              </div>
            </div>

            <!-- 交易记录表格 -->
            <div class="trades-table-section" v-if="backtestResults.trades && backtestResults.trades.length > 0">
              <h3>交易记录 (最近20笔)</h3>
              <el-table
                :data="recentTrades"
                size="small"
                max-height="400"
                style="width: 100%"
              >
                <el-table-column prop="timestamp" label="时间" width="180">
                  <template #default="scope">
                    {{ formatDateTime(scope.row.timestamp) }}
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="类型" width="100">
                  <template #default="scope">
                    <el-tag
                      :type="getTradeTypeColor(scope.row.type)"
                      size="small"
                    >
                      {{ getTradeTypeName(scope.row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="价格" width="120">
                  <template #default="scope">
                    ${{ formatNumber(scope.row.price, '0.00') }}
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="数量" width="120">
                  <template #default="scope">
                    {{ formatNumber(scope.row.amount, '0.0000') }} ETH
                  </template>
                </el-table-column>
                <el-table-column prop="pnl" label="盈亏" width="120">
                  <template #default="scope">
                    <span :class="getPriceChangeClass(scope.row.pnl)">
                      {{ scope.row.pnl ? formatNumber(scope.row.pnl, '0.00') : '-' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="fee" label="手续费" width="100">
                  <template #default="scope">
                    {{ formatNumber(scope.row.fee || 0, '0.00') }}
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 操作按钮 -->
            <div class="result-actions">
              <el-button
                type="primary"
                :icon="PieChart"
                @click="$router.push({ name: 'analysis' })"
              >
                查看详细分析
              </el-button>

              <el-button
                :icon="Download"
                @click="exportResults"
              >
                导出结果
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useMarketStore } from '@/stores/market'
import { useBacktestStore } from '@/stores/backtest'
import { formatPercent, formatNumber, getPriceChangeClass } from '@/utils/format'
import { ElMessage } from 'element-plus'
import BacktestTradingChart from '@/components/BacktestTradingChart.vue'
import BacktestKlineChart from '@/components/BacktestKlineChart.vue'
import {
  VideoPlay,
  Refresh,
  PieChart,
  Download,
  TrendCharts
} from '@element-plus/icons-vue'

// Router
const router = useRouter()

// Store
const marketStore = useMarketStore()
const backtestStore = useBacktestStore()
const { symbols } = storeToRefs(marketStore)
const { loading: backtestLoading, currentResult: backtestResults, runningBacktests } = storeToRefs(backtestStore)

// 导航路由
const navRoutes = computed(() => {
  return router.getRoutes().filter(route =>
    route.meta?.title && route.name !== 'home' && route.name !== 'login' && route.name !== 'test'
  )
})

// 从localStorage恢复回测参数
const loadBacktestParams = () => {
  try {
    const stored = localStorage.getItem('backtest-params')
    if (stored) {
      const params = JSON.parse(stored)
      console.log('从localStorage恢复参数:', params)
      return { ...params }
    }
  } catch (e) {
    console.warn('Failed to load backtest params from localStorage:', e)
  }
  // 默认参数 - 5倍杠杆，一个月时间范围
  const defaultParams = {
    symbol: 'ETHUSDT',
    dateRange: ['2025-05-15', '2025-06-15'], // 使用数据最后一个月
    initialCapital: 10000,
    leverage: 5, // 5倍杠杆
    spreadThreshold: 0.002,
    positionRatio: 0.8,
    orderRatio: 0.02
  }
  console.log('使用默认参数:', defaultParams)
  return defaultParams
}

// 回测参数
const backtestParams = ref(loadBacktestParams())

// 计算属性
const canRunBacktest = computed(() => {
  return backtestParams.value.symbol &&
         backtestParams.value.dateRange &&
         backtestParams.value.dateRange.length === 2 &&
         !backtestLoading.value
})

// 检查是否有有效的交易数据
const hasValidTrades = computed(() => {
  return backtestResults.value &&
         backtestResults.value.trades &&
         Array.isArray(backtestResults.value.trades) &&
         backtestResults.value.trades.length > 0
})

// 方法
const runBacktest = async () => {
  try {
    // 验证参数
    if (!backtestParams.value.dateRange || backtestParams.value.dateRange.length !== 2) {
      ElMessage.error('请选择回测时间范围')
      return
    }

    // 准备回测参数 - 匹配FastAPI后端格式
    const params = {
      symbol: backtestParams.value.symbol,
      startDate: backtestParams.value.dateRange[0],
      endDate: backtestParams.value.dateRange[1],
      initialCapital: backtestParams.value.initialCapital,
      leverage: backtestParams.value.leverage,
      spreadThreshold: backtestParams.value.spreadThreshold,
      positionRatio: backtestParams.value.positionRatio,
      orderRatio: backtestParams.value.orderRatio
    }

    // 运行回测
    const result = await backtestStore.runBacktest(params)

    // 处理回测结果 - 持久化到store
    if (result.success && result.data) {
      // 设置当前结果到store，实现持久化
      backtestStore.setCurrentResult(result.data)
      const tradeCount = result.data.total_trades || 0
      ElMessage.success(`回测完成！共执行 ${tradeCount} 笔交易`)
    } else {
      ElMessage.error(result.error || '回测失败，请检查参数设置')
      backtestStore.setCurrentResult(null)
    }

  } catch (error) {
    ElMessage.error('回测启动失败：' + error.message)
  }
}

const checkBacktestStatus = async (resultId) => {
  try {
    const result = await backtestStore.fetchBacktestResult(resultId)
    if (result.status === 'completed') {
      ElMessage.success('回测完成！')
    } else if (result.status === 'failed') {
      ElMessage.error('回测失败')
    }
  } catch (error) {
    console.error('检查回测状态失败:', error)
  }
}

const resetParams = () => {
  // 使用新的默认参数
  backtestParams.value = {
    symbol: 'ETHUSDT',
    dateRange: ['2025-05-15', '2025-06-15'], // 使用数据最后一个月
    initialCapital: 10000,
    leverage: 5, // 5倍杠杆
    spreadThreshold: 0.002,
    positionRatio: 0.8,
    orderRatio: 0.02
  }
  ElMessage.success('参数已重置')
}

// 计算属性：最近的交易记录
const recentTrades = computed(() => {
  if (!backtestResults.value?.trades) return []
  return backtestResults.value.trades.slice(-20).reverse()
})

// 格式化日期时间
const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取交易类型颜色
const getTradeTypeColor = (type) => {
  const colorMap = {
    'open_long': 'success',
    'close_long': 'warning',
    'open_short': 'danger',
    'close_short': 'info',
    'buy_long': 'success',
    'sell_long': 'warning',
    'sell_short': 'danger',
    'buy_short': 'info'
  }
  return colorMap[type] || 'info'
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

// 生成模拟回测数据用于演示
const generateMockBacktestData = (params) => {
  const startDate = new Date(params.start_date)
  const endDate = new Date(params.end_date)
  const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))

  // 生成模拟交易记录
  const trades = []
  const equityCurve = []
  let currentPrice = 3000 // ETH起始价格
  let equity = params.initial_balance

  for (let i = 0; i < days * 10; i++) { // 每天约10笔交易
    const timestamp = startDate.getTime() / 1000 + i * 8640 // 每2.4小时一笔交易

    // 价格随机波动
    currentPrice += (Math.random() - 0.5) * 100
    currentPrice = Math.max(2500, Math.min(3500, currentPrice))

    // 随机生成交易类型
    const tradeTypes = ['buy_long', 'sell_long', 'sell_short', 'buy_short']
    const tradeType = tradeTypes[Math.floor(Math.random() * tradeTypes.length)]

    const amount = 0.01 + Math.random() * 0.1 // 0.01-0.11 ETH
    const fee = amount * currentPrice * 0.0005 // 0.05% 手续费
    const pnl = (Math.random() - 0.5) * 50 // 随机盈亏

    trades.push({
      timestamp: timestamp,
      type: tradeType,
      price: currentPrice,
      amount: amount,
      fee: fee,
      pnl: pnl
    })

    // 更新权益
    equity += pnl - fee
    equityCurve.push({
      timestamp: timestamp,
      equity: equity,
      price: currentPrice
    })
  }

  const finalEquity = equity
  const totalReturn = (finalEquity - params.initial_balance) / params.initial_balance
  const maxDrawdown = 0.15 // 模拟最大回撤
  const profitableTrades = trades.filter(t => t.pnl > 0).length

  return {
    total_return: totalReturn,
    max_drawdown: maxDrawdown,
    sharpe_ratio: 0.8,
    total_trades: trades.length,
    win_rate: profitableTrades / trades.length,
    final_capital: finalEquity,
    trades: trades,
    equity_curve: equityCurve
  }
}

const exportResults = () => {
  if (!backtestResults.value) return

  // 模拟导出功能
  ElMessage.success('结果导出功能开发中...')
}

// 监听参数变化，保存到localStorage
watch(backtestParams, (newParams) => {
  try {
    localStorage.setItem('backtest-params', JSON.stringify(newParams))
    console.log('参数已保存到localStorage:', newParams)
  } catch (e) {
    console.warn('Failed to save backtest params to localStorage:', e)
  }
}, { deep: true })

// 生命周期
onMounted(async () => {
  // 确保交易对数据已加载
  if (symbols.value.length === 0) {
    await marketStore.fetchSymbols()
  }

  // 加载回测结果
  await backtestStore.fetchBacktestResults()

  console.log('页面加载完成，当前回测参数:', backtestParams.value)
})
</script>

<style lang="scss" scoped>
.backtest-view {
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

.backtest-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
  padding: 0 24px;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.config-panel,
.results-panel {
  .el-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    
    :deep(.el-card__header) {
      background: var(--bg-tertiary);
      border-bottom: 1px solid var(--border-color);
      font-weight: 600;
      color: var(--text-primary);
    }
  }
}

.config-panel {
  .el-form {
    .el-form-item {
      margin-bottom: 20px;
      
      .unit {
        margin-left: 8px;
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
  }
}

.no-results {
  padding: 40px 0;
  text-align: center;
}

.results-content {
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
    
    .metric-item {
      padding: 16px;
      background: var(--bg-tertiary);
      border-radius: 6px;
      border: 1px solid var(--border-color);
      text-align: center;
      
      .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 8px;
      }
      
      .metric-value {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }
  }
  
  .result-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
  }
}

.trading-chart-section {
  margin-top: 24px;

  h3 {
    margin: 0 0 16px 0;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
  }
}

.trades-table-section {
  margin-top: 24px;

  h3 {
    margin: 0 0 16px 0;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
  }

  .el-table {
    border-radius: 8px;
    overflow: hidden;

    :deep(.el-table__header) {
      background: var(--bg-tertiary);
    }

    :deep(.el-table__row) {
      &:hover {
        background: var(--bg-hover);
      }
    }
  }
}

.result-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
