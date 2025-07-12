<template>
  <div class="backtest-view">
    <div class="header">
      <h1>策略回测</h1>
      <div class="nav-buttons">
        <el-button @click="$router.push('/trading')">交易图表</el-button>
        <el-button @click="$router.push('/analysis')">结果分析</el-button>
        <el-button @click="$router.push('/settings')">系统设置</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    
    <div class="content">
      <div class="parameter-panel">
        <h2>策略参数</h2>
        <el-form :model="backtestParams" label-width="120px" size="default">
          <el-form-item label="策略选择">
            <el-select v-model="backtestParams.strategy" placeholder="选择策略">
              <el-option label="网格做市策略" value="grid_making" />
            </el-select>
          </el-form-item>

          <el-form-item label="交易对">
            <el-select v-model="backtestParams.symbol" placeholder="选择交易对">
              <el-option label="ETH/USDC" value="ETHUSDC" />
              <el-option label="BTC/USDT" value="BTCUSDT" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="时间周期">
            <el-select v-model="backtestParams.timeframe" placeholder="选择时间周期">
              <el-option label="1分钟" value="1m" />
              <el-option label="5分钟" value="5m" />
              <el-option label="15分钟" value="15m" />
              <el-option label="1小时" value="1h" />
              <el-option label="4小时" value="4h" />
              <el-option label="1天" value="1d" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="初始资金">
            <el-input-number 
              v-model="backtestParams.initialCapital" 
              :min="1000" 
              :max="1000000" 
              :step="1000"
              placeholder="初始资金"
            />
          </el-form-item>
          
          <el-form-item label="杠杆倍数">
            <el-input-number 
              v-model="backtestParams.leverage" 
              :min="1" 
              :max="125" 
              :step="1"
              placeholder="杠杆倍数"
            />
          </el-form-item>
          
          <el-form-item label="价差阈值">
            <el-input-number 
              v-model="backtestParams.spreadThreshold" 
              :min="0.0001" 
              :max="0.01" 
              :step="0.0001"
              :precision="4"
              placeholder="价差阈值"
            />
          </el-form-item>
          
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="backtestParams.startDate"
              type="date"
              placeholder="选择开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="backtestParams.endDate"
              type="date"
              placeholder="选择结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="startBacktest" :loading="isRunning">
              {{ isRunning ? '回测中...' : '开始回测' }}
            </el-button>
            <el-button @click="resetParams">重置参数</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="result-panel">
        <h2>回测结果</h2>
        <div v-if="backtestResult" class="result-content">
          <div class="metrics-grid">
            <div class="metric-card">
              <h3>总收益率</h3>
              <div class="metric-value" :class="backtestResult.totalReturn >= 0 ? 'positive' : 'negative'">
                {{ (backtestResult.totalReturn * 100).toFixed(2) }}%
              </div>
            </div>
            <div class="metric-card">
              <h3>最大回撤</h3>
              <div class="metric-value negative">
                {{ (backtestResult.maxDrawdown * 100).toFixed(2) }}%
              </div>
            </div>
            <div class="metric-card">
              <h3>夏普比率</h3>
              <div class="metric-value">
                {{ backtestResult.sharpeRatio.toFixed(2) }}
              </div>
            </div>
            <div class="metric-card">
              <h3>交易次数</h3>
              <div class="metric-value">
                {{ backtestResult.totalTrades }}
              </div>
            </div>
            <div class="metric-card">
              <h3>胜率</h3>
              <div class="metric-value">
                {{ (backtestResult.winRate * 100).toFixed(1) }}%
              </div>
            </div>
            <div class="metric-card">
              <h3>最终资金</h3>
              <div class="metric-value">
                ${{ backtestResult.finalCapital.toLocaleString() }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-result">
          <p>暂无回测结果，请设置参数并开始回测</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const isRunning = ref(false)
const backtestResult = ref(null)

const backtestParams = reactive({
  strategy: 'grid_making',
  symbol: 'ETHUSDC',
  timeframe: '1h',
  initialCapital: 10000,
  leverage: 10,
  spreadThreshold: 0.002,
  startDate: '2024-01-01',
  endDate: '2024-12-31'
})

const startBacktest = async () => {
  isRunning.value = true

  try {
    ElMessage.info('开始回测，请稍候...')

    // 调用后端回测API
    const response = await axios.post('/api/market-data/backtest/', {
      strategy: backtestParams.strategy,
      symbol: backtestParams.symbol,
      timeframe: backtestParams.timeframe,
      initial_capital: backtestParams.initialCapital,
      leverage: backtestParams.leverage,
      bid_spread: backtestParams.spreadThreshold,
      ask_spread: backtestParams.spreadThreshold,
      start_date: backtestParams.startDate,
      end_date: backtestParams.endDate
    })

    if (response.data.success) {
      const result = response.data.data
      backtestResult.value = {
        totalReturn: result.total_return,
        maxDrawdown: result.max_drawdown,
        sharpeRatio: result.sharpe_ratio,
        totalTrades: result.total_trades,
        winRate: result.win_rate,
        finalCapital: result.final_capital,
        trades: result.trades || [],
        equityCurve: result.equity_curve || []
      }
      ElMessage.success('回测完成！')
    } else {
      throw new Error(response.data.error || '回测失败')
    }
  } catch (error) {
    console.error('回测失败:', error)
    ElMessage.error('回测失败：' + (error.response?.data?.error || error.message))
  } finally {
    isRunning.value = false
  }
}

const resetParams = () => {
  Object.assign(backtestParams, {
    symbol: 'ETHUSDC',
    timeframe: '1h',
    initialCapital: 10000,
    leverage: 10,
    spreadThreshold: 0.002,
    startDate: '2024-01-01',
    endDate: '2024-12-31'
  })
  backtestResult.value = null
  ElMessage.info('参数已重置')
}

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.backtest-view {
  padding: 20px;
  min-height: 100vh;
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
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.parameter-panel, .result-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
}

.metric-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.metric-value.positive {
  color: #02c076;
}

.metric-value.negative {
  color: #f84960;
}

.no-result {
  text-align: center;
  padding: 40px;
  color: #666;
}

h1, h2 {
  color: #333;
  margin-top: 0;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>
