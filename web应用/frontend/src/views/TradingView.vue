<template>
  <div class="trading-view">
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

        <el-button
          size="small"
          :icon="isDark ? Sunny : Moon"
          @click="toggleTheme"
          circle
        />

        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <el-button size="small" circle>
            <el-icon><User /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <strong>{{ user?.username || '用户' }}</strong>
              </el-dropdown-item>
              <el-dropdown-item divided command="profile">
                <el-icon><Setting /></el-icon>
                个人设置
              </el-dropdown-item>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧图表区域 -->
      <div class="chart-section">
        <TradingChart
          :height="chartHeight"
          :show-trades="showTrades"
          :trades="currentTrades"
        />
      </div>
      
      <!-- 右侧信息面板 -->
      <div class="info-panel">
        <!-- 市场概览 -->
        <el-card class="info-card" header="市场概览">
          <div class="market-overview">
            <div class="overview-item" v-if="marketStats.symbol">
              <div class="item-label">交易对</div>
              <div class="item-value">{{ currentSymbolInfo.name || marketStats.symbol }}</div>
            </div>
            
            <div class="overview-item" v-if="marketStats.last_price">
              <div class="item-label">最新价格</div>
              <div class="item-value" :class="getPriceChangeClass(marketStats.price_24h_change)">
                {{ formatPrice(marketStats.last_price) }}
              </div>
            </div>
            
            <div class="overview-item" v-if="marketStats.price_24h_change !== undefined">
              <div class="item-label">24h涨跌幅</div>
              <div class="item-value" :class="getPriceChangeClass(marketStats.price_24h_change)">
                {{ formatPercent(marketStats.price_24h_change) }}
              </div>
            </div>
            
            <div class="overview-item" v-if="marketStats.volume_24h">
              <div class="item-label">24h成交量</div>
              <div class="item-value">{{ formatVolume(marketStats.volume_24h) }}</div>
            </div>
            
            <div class="overview-item" v-if="marketStats.high_24h">
              <div class="item-label">24h最高</div>
              <div class="item-value">{{ formatPrice(marketStats.high_24h) }}</div>
            </div>
            
            <div class="overview-item" v-if="marketStats.low_24h">
              <div class="item-label">24h最低</div>
              <div class="item-value">{{ formatPrice(marketStats.low_24h) }}</div>
            </div>
          </div>
        </el-card>
        
        <!-- 系统状态 -->
        <el-card class="info-card" header="系统状态">
          <div class="system-status">
            <div class="status-item">
              <div class="status-label">数据连接</div>
              <div class="status-value">
                <el-tag :type="loading ? 'warning' : 'success'" size="small">
                  {{ loading ? '加载中' : '正常' }}
                </el-tag>
              </div>
            </div>
            
            <div class="status-item">
              <div class="status-label">数据量</div>
              <div class="status-value">{{ klineData.length }} 条K线</div>
            </div>
            
            <div class="status-item">
              <div class="status-label">时间周期</div>
              <div class="status-value">{{ currentTimeframeInfo.label || currentTimeframe }}</div>
            </div>
            
            <div class="status-item" v-if="systemInfo.platform">
              <div class="status-label">平台版本</div>
              <div class="status-value">{{ systemInfo.platform.version }}</div>
            </div>
          </div>
        </el-card>
        
        <!-- 图表控制 -->
        <el-card class="info-card" header="图表控制">
          <div class="chart-controls">
            <div class="control-item">
              <span class="control-label">显示交易标记</span>
              <el-switch
                v-model="showTrades"
                :disabled="!latestResult || !latestResult.trades"
              />
            </div>

            <div class="control-item" v-if="latestResult">
              <span class="control-label">回测结果</span>
              <el-tag :type="latestResult.status === 'completed' ? 'success' : 'info'" size="small">
                {{ latestResult.status === 'completed' ? '已完成' : '进行中' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="info-card" header="快速操作">
          <div class="quick-actions">
            <el-button
              type="primary"
              size="small"
              :icon="DataAnalysis"
              @click="$router.push({ name: 'backtest' })"
              block
            >
              开始回测
            </el-button>

            <el-button
              size="small"
              :icon="PieChart"
              @click="$router.push({ name: 'analysis' })"
              block
            >
              查看分析
            </el-button>

            <el-button
              size="small"
              :icon="Setting"
              @click="$router.push({ name: 'settings' })"
              block
            >
              系统设置
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useSystemStore } from '@/stores/system'
import { useMarketStore } from '@/stores/market'
import { useBacktestStore } from '@/stores/backtest'
import { useAuthStore } from '@/stores/auth'
import TradingChart from '@/components/TradingChart.vue'
import { formatPrice, formatPercent, formatVolume, getPriceChangeClass } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  DataAnalysis,
  PieChart,
  Setting,
  Sunny,
  Moon,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

// Router
const router = useRouter()

// Stores
const systemStore = useSystemStore()
const marketStore = useMarketStore()
const backtestStore = useBacktestStore()
const authStore = useAuthStore()

// 从store获取数据
const { systemInfo, isDark } = storeToRefs(systemStore)
const { user } = storeToRefs(authStore)
const {
  marketStats,
  klineData,
  loading,
  currentSymbol,
  currentTimeframe,
  currentSymbolInfo,
  currentTimeframeInfo
} = storeToRefs(marketStore)
const { latestResult } = storeToRefs(backtestStore)

// 响应式数据
const chartHeight = ref(600)
const showTrades = ref(false)

// 计算属性
const currentTrades = computed(() => {
  if (!showTrades.value || !latestResult.value || !latestResult.value.trades) {
    return []
  }
  return latestResult.value.trades
})

// 导航路由
const navRoutes = computed(() => {
  return router.getRoutes().filter(route => 
    route.meta?.title && route.name !== 'home'
  )
})

// 方法
const toggleTheme = () => {
  systemStore.toggleTheme()
}

const updateChartHeight = () => {
  const windowHeight = window.innerHeight
  const navbarHeight = 60
  const padding = 40
  chartHeight.value = Math.max(400, windowHeight - navbarHeight - padding)
}

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '确认退出',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}

// 生命周期
onMounted(async () => {
  // 初始化主题
  systemStore.initTheme()

  // 计算图表高度
  updateChartHeight()

  // 监听窗口大小变化
  window.addEventListener('resize', updateChartHeight)

  // 加载回测结果
  try {
    await backtestStore.fetchBacktestResults()
  } catch (error) {
    console.error('加载回测结果失败:', error)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateChartHeight)
})
</script>

<style lang="scss" scoped>
.trading-view {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.top-navbar {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  
  .navbar-left {
    .app-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      
      .el-icon {
        color: var(--binance-yellow);
      }
    }
  }
  
  .navbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

.chart-section {
  flex: 1;
  min-width: 0;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.info-panel {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  .info-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    
    :deep(.el-card__header) {
      background: var(--bg-tertiary);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    :deep(.el-card__body) {
      padding: 16px;
    }
  }
}

.market-overview {
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  .overview-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .item-label {
      color: var(--text-secondary);
      font-size: 12px;
    }
    
    .item-value {
      color: var(--text-primary);
      font-weight: 500;
      font-size: 14px;
    }
  }
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .status-label {
      color: var(--text-secondary);
      font-size: 12px;
    }
    
    .status-value {
      color: var(--text-primary);
      font-size: 12px;
    }
  }
}

.chart-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .control-item {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .control-label {
      color: var(--text-secondary);
      font-size: 12px;
    }
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .el-button {
    justify-content: flex-start;

    .el-icon {
      margin-right: 6px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .info-panel {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
    padding: 8px;
  }
  
  .info-panel {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    
    .info-card {
      min-width: 200px;
    }
  }
  
  .top-navbar {
    padding: 0 12px;
    
    .navbar-left .app-title {
      font-size: 16px;
    }
  }
}
</style>
