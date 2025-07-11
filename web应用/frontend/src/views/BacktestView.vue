<template>
  <div class="backtest-view">
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
                <el-icon><Play /></el-icon>
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
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMarketStore } from '@/stores/market'
import { useBacktestStore } from '@/stores/backtest'
import { formatPercent, formatNumber, getPriceChangeClass } from '@/utils/format'
import { ElMessage } from 'element-plus'
import {
  Play,
  Refresh,
  PieChart,
  Download
} from '@element-plus/icons-vue'

// Store
const marketStore = useMarketStore()
const backtestStore = useBacktestStore()
const { symbols } = storeToRefs(marketStore)
const { loading: backtestLoading, currentResult: backtestResults, runningBacktests } = storeToRefs(backtestStore)

// 回测参数
const backtestParams = ref({
  symbol: 'ETHUSDT',
  dateRange: ['2024-06-15', '2024-07-14'],
  initialCapital: 10000,
  leverage: 125,
  spreadThreshold: 0.002,
  positionRatio: 0.8,
  orderRatio: 0.02
})

// 计算属性
const canRunBacktest = computed(() => {
  return backtestParams.value.symbol && 
         backtestParams.value.dateRange && 
         backtestParams.value.dateRange.length === 2 &&
         !backtestLoading.value
})

// 方法
const runBacktest = async () => {
  try {
    // 验证参数
    if (!backtestParams.value.dateRange || backtestParams.value.dateRange.length !== 2) {
      ElMessage.error('请选择回测时间范围')
      return
    }

    // 准备回测参数
    const params = {
      name: `回测_${new Date().toLocaleString()}`,
      symbol: backtestParams.value.symbol,
      start_date: backtestParams.value.dateRange[0],
      end_date: backtestParams.value.dateRange[1],
      initial_balance: backtestParams.value.initialCapital,
      leverage: backtestParams.value.leverage,
      bid_spread: backtestParams.value.spreadThreshold,
      ask_spread: backtestParams.value.spreadThreshold,
      position_size_ratio: backtestParams.value.orderRatio,
      max_position_value_ratio: backtestParams.value.positionRatio
    }

    // 运行回测
    const result = await backtestStore.runBacktest(params)

    ElMessage.success('回测已启动，请稍后查看结果')

    // 等待回测完成
    setTimeout(() => {
      checkBacktestStatus(result.result_id)
    }, 2000)

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
  backtestParams.value = {
    symbol: 'ETHUSDT',
    dateRange: ['2024-06-15', '2024-07-14'],
    initialCapital: 10000,
    leverage: 125,
    spreadThreshold: 0.002,
    positionRatio: 0.8,
    orderRatio: 0.02
  }
}

const exportResults = () => {
  if (!backtestResults.value) return
  
  // 模拟导出功能
  ElMessage.success('结果导出功能开发中...')
}

// 生命周期
onMounted(async () => {
  // 确保交易对数据已加载
  if (symbols.value.length === 0) {
    await marketStore.fetchSymbols()
  }

  // 加载回测结果
  await backtestStore.fetchBacktestResults()
})
</script>

<style lang="scss" scoped>
.backtest-view {
  padding: 20px;
  background: var(--bg-primary);
  min-height: 100vh;
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
</style>
