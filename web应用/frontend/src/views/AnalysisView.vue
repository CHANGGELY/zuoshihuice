<template>
  <div class="analysis-view">
    <div class="page-header">
      <h2>结果分析</h2>
      <p>深度分析回测结果，查看详细的性能指标和图表</p>
    </div>
    
    <div class="analysis-content">
      <el-row :gutter="24">
        <!-- 性能概览 -->
        <el-col :span="24">
          <el-card header="性能概览" class="overview-card">
            <div class="overview-metrics">
              <div class="metric-group">
                <h4>收益指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">总收益率:</span>
                    <span class="value text-green">+890.83%</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">年化收益率:</span>
                    <span class="value text-green">+3434%</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">月均收益率:</span>
                    <span class="value text-green">+1008.29%</span>
                  </div>
                </div>
              </div>
              
              <div class="metric-group">
                <h4>风险指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">最大回撤:</span>
                    <span class="value text-red">-67.22%</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">夏普比率:</span>
                    <span class="value">0.23</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">波动率:</span>
                    <span class="value">45.6%</span>
                  </div>
                </div>
              </div>
              
              <div class="metric-group">
                <h4>交易指标</h4>
                <div class="metric-list">
                  <div class="metric-item">
                    <span class="label">总交易次数:</span>
                    <span class="value">3,267 笔</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">胜率:</span>
                    <span class="value">65.4%</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">平均持仓时间:</span>
                    <span class="value">2.3 小时</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 权益曲线图 -->
        <el-col :span="24">
          <el-card header="权益曲线" class="chart-card">
            <div class="chart-placeholder">
              <el-icon size="48"><TrendCharts /></el-icon>
              <p>权益曲线图表开发中...</p>
              <p class="chart-desc">将显示资金权益随时间的变化趋势</p>
            </div>
          </el-card>
        </el-col>
        
        <!-- 交易分布 -->
        <el-col :span="12">
          <el-card header="交易分布" class="chart-card">
            <div class="chart-placeholder">
              <el-icon size="48"><PieChart /></el-icon>
              <p>交易分布图表开发中...</p>
              <p class="chart-desc">显示盈利/亏损交易的分布情况</p>
            </div>
          </el-card>
        </el-col>
        
        <!-- 月度收益 -->
        <el-col :span="12">
          <el-card header="月度收益" class="chart-card">
            <div class="chart-placeholder">
              <el-icon size="48"><DataLine /></el-icon>
              <p>月度收益图表开发中...</p>
              <p class="chart-desc">显示每月的收益表现</p>
            </div>
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
import { ref } from 'vue'
import {
  TrendCharts,
  PieChart,
  DataLine
} from '@element-plus/icons-vue'

// 详细统计数据
const detailedStats = ref([
  {
    metric: '初始资金',
    value: '607.88 USDT',
    description: '回测开始时的初始保证金'
  },
  {
    metric: '最终权益',
    value: '6,023.05 USDT',
    description: '回测结束时的总权益'
  },
  {
    metric: '总盈亏',
    value: '+5,415.17 USDT',
    description: '回测期间的总盈亏金额'
  },
  {
    metric: '总手续费',
    value: '33.84 USDT',
    description: '回测期间支付的总手续费'
  },
  {
    metric: '多头仓位',
    value: '36.36 ETH',
    description: '最终多头仓位数量'
  },
  {
    metric: '空头仓位',
    value: '37.39 ETH',
    description: '最终空头仓位数量'
  },
  {
    metric: '净仓位',
    value: '-1.03 ETH',
    description: '多空仓位的净值'
  },
  {
    metric: '保证金率',
    value: '2.63%',
    description: '当前保证金使用率'
  }
])
</script>

<style lang="scss" scoped>
.analysis-view {
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

.analysis-content {
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

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  text-align: center;
  
  .el-icon {
    margin-bottom: 16px;
    color: var(--text-tertiary);
  }
  
  p {
    margin: 8px 0;
    
    &.chart-desc {
      font-size: 12px;
      color: var(--text-tertiary);
    }
  }
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
