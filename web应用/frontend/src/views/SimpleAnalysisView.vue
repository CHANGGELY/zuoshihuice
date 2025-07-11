<template>
  <div class="analysis-view">
    <div class="header">
      <h1>结果分析</h1>
      <div class="nav-buttons">
        <el-button @click="$router.push('/trading')">交易图表</el-button>
        <el-button @click="$router.push('/backtest')">策略回测</el-button>
        <el-button @click="$router.push('/settings')">系统设置</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    
    <div class="content">
      <div class="chart-section">
        <h2>收益曲线</h2>
        <div ref="equityChart" class="chart-container"></div>
      </div>
      
      <div class="stats-section">
        <h2>详细统计</h2>
        <div class="stats-grid">
          <div class="stat-group">
            <h3>收益指标</h3>
            <div class="stat-item">
              <span class="label">总收益率:</span>
              <span class="value positive">+15.67%</span>
            </div>
            <div class="stat-item">
              <span class="label">年化收益率:</span>
              <span class="value positive">+23.45%</span>
            </div>
            <div class="stat-item">
              <span class="label">最大回撤:</span>
              <span class="value negative">-8.32%</span>
            </div>
            <div class="stat-item">
              <span class="label">夏普比率:</span>
              <span class="value">1.85</span>
            </div>
          </div>
          
          <div class="stat-group">
            <h3>交易统计</h3>
            <div class="stat-item">
              <span class="label">总交易次数:</span>
              <span class="value">1,247</span>
            </div>
            <div class="stat-item">
              <span class="label">盈利交易:</span>
              <span class="value positive">756 (60.6%)</span>
            </div>
            <div class="stat-item">
              <span class="label">亏损交易:</span>
              <span class="value negative">491 (39.4%)</span>
            </div>
            <div class="stat-item">
              <span class="label">平均持仓时间:</span>
              <span class="value">2.3小时</span>
            </div>
          </div>
          
          <div class="stat-group">
            <h3>风险指标</h3>
            <div class="stat-item">
              <span class="label">波动率:</span>
              <span class="value">12.45%</span>
            </div>
            <div class="stat-item">
              <span class="label">最大连续亏损:</span>
              <span class="value negative">5次</span>
            </div>
            <div class="stat-item">
              <span class="label">最大单笔亏损:</span>
              <span class="value negative">-$234.56</span>
            </div>
            <div class="stat-item">
              <span class="label">VaR (95%):</span>
              <span class="value">-$156.78</span>
            </div>
          </div>
          
          <div class="stat-group">
            <h3>资金管理</h3>
            <div class="stat-item">
              <span class="label">初始资金:</span>
              <span class="value">$10,000</span>
            </div>
            <div class="stat-item">
              <span class="label">最终资金:</span>
              <span class="value positive">$11,567</span>
            </div>
            <div class="stat-item">
              <span class="label">最高资金:</span>
              <span class="value">$12,234</span>
            </div>
            <div class="stat-item">
              <span class="label">最低资金:</span>
              <span class="value">$9,168</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="trades-section">
        <h2>交易记录</h2>
        <el-table :data="recentTrades" style="width: 100%" size="small">
          <el-table-column prop="time" label="时间" width="180" />
          <el-table-column prop="type" label="类型" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="120" />
          <el-table-column prop="quantity" label="数量" width="120" />
          <el-table-column prop="pnl" label="盈亏" width="120">
            <template #default="scope">
              <span :class="scope.row.pnl >= 0 ? 'positive' : 'negative'">
                {{ scope.row.pnl >= 0 ? '+' : '' }}${{ scope.row.pnl.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="交易原因" />
        </el-table>
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
const equityChart = ref()

let chart = null

const recentTrades = ref([
  {
    time: '2024-07-12 14:30:15',
    type: '买入',
    price: '$3,456.78',
    quantity: '0.5 ETH',
    pnl: 23.45,
    reason: '价差超过阈值'
  },
  {
    time: '2024-07-12 14:25:32',
    type: '卖出',
    price: '$3,445.23',
    quantity: '0.5 ETH',
    pnl: -12.34,
    reason: '止损触发'
  },
  {
    time: '2024-07-12 14:20:18',
    type: '买入',
    price: '$3,467.89',
    quantity: '0.3 ETH',
    pnl: 45.67,
    reason: '价差超过阈值'
  },
  {
    time: '2024-07-12 14:15:45',
    type: '卖出',
    price: '$3,434.56',
    quantity: '0.8 ETH',
    pnl: 78.90,
    reason: '获利了结'
  },
  {
    time: '2024-07-12 14:10:22',
    type: '买入',
    price: '$3,423.45',
    quantity: '0.6 ETH',
    pnl: -5.67,
    reason: '价差超过阈值'
  }
])

const generateEquityData = () => {
  const data = []
  let equity = 10000
  const now = new Date()
  
  for (let i = 30; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
    const change = (Math.random() - 0.45) * 200 // 略微向上的趋势
    equity += change
    
    data.push({
      time: Math.floor(time.getTime() / 1000),
      value: parseFloat(equity.toFixed(2))
    })
  }
  
  return data
}

const initEquityChart = () => {
  if (!equityChart.value) return
  
  chart = createChart(equityChart.value, {
    width: equityChart.value.clientWidth,
    height: 300,
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
  
  const lineSeries = chart.addLineSeries({
    color: '#02c076',
    lineWidth: 2,
  })
  
  const data = generateEquityData()
  lineSeries.setData(data)
  
  chart.timeScale().fitContent()
}

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}

const handleResize = () => {
  if (chart && equityChart.value) {
    chart.applyOptions({
      width: equityChart.value.clientWidth,
    })
  }
}

onMounted(() => {
  initEquityChart()
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
.analysis-view {
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
  grid-template-columns: 1fr;
  gap: 20px;
}

.chart-section, .stats-section, .trades-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-container {
  width: 100%;
  height: 300px;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.stat-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.stat-group h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 2px solid #02c076;
  padding-bottom: 5px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px 0;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  font-weight: bold;
  font-size: 14px;
  color: #333;
}

.value.positive {
  color: #02c076;
}

.value.negative {
  color: #f84960;
}

.positive {
  color: #02c076;
}

.negative {
  color: #f84960;
}

h1, h2 {
  color: #333;
  margin-top: 0;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
