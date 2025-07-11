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
        <h2>K线图表</h2>
        <div class="chart-placeholder">
          <p>这里将显示实时K线图表</p>
          <p>支持多时间周期：1分钟、5分钟、15分钟、1小时、4小时、1天</p>
          <p>数据范围：2019-11-01 到 2025-06-15</p>
        </div>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}
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

.chart-placeholder {
  height: 400px;
  border: 2px dashed #ddd;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
  margin-top: 20px;
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
