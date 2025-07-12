<template>
  <div class="settings-view">
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
      <h2>系统设置</h2>
      <p>配置系统参数和个人偏好设置</p>
    </div>
    
    <div class="settings-content">
      <el-row :gutter="24">
        <!-- 界面设置 -->
        <el-col :span="12">
          <el-card header="界面设置">
            <el-form label-width="120px" size="small">
              <el-form-item label="主题模式">
                <el-switch
                  v-model="isDark"
                  @change="toggleTheme"
                  active-text="深色"
                  inactive-text="浅色"
                  :active-icon="Moon"
                  :inactive-icon="Sunny"
                />
              </el-form-item>
              
              <el-form-item label="语言设置">
                <el-select v-model="language" placeholder="选择语言">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="图表主题">
                <el-radio-group v-model="chartTheme">
                  <el-radio label="binance">币安风格</el-radio>
                  <el-radio label="tradingview">TradingView</el-radio>
                  <el-radio label="custom">自定义</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="默认时间周期">
                <el-select v-model="defaultTimeframe" placeholder="选择默认时间周期">
                  <el-option label="1分钟" value="1m" />
                  <el-option label="5分钟" value="5m" />
                  <el-option label="15分钟" value="15m" />
                  <el-option label="1小时" value="1h" />
                  <el-option label="4小时" value="4h" />
                  <el-option label="1天" value="1d" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <!-- 回测设置 -->
        <el-col :span="12">
          <el-card header="回测设置">
            <el-form label-width="120px" size="small">
              <el-form-item label="默认杠杆">
                <el-input-number
                  v-model="defaultLeverage"
                  :min="1"
                  :max="125"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="默认价差">
                <el-input-number
                  v-model="defaultSpread"
                  :min="0.001"
                  :max="0.01"
                  :step="0.001"
                  :precision="3"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="缓存时间">
                <el-input-number
                  v-model="cacheTimeout"
                  :min="60"
                  :max="3600"
                  :step="60"
                  controls-position="right"
                />
                <span class="unit">秒</span>
              </el-form-item>
              
              <el-form-item label="自动保存">
                <el-switch
                  v-model="autoSave"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <!-- 系统信息 -->
        <el-col :span="24">
          <el-card header="系统信息">
            <div class="system-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="平台名称">
                  {{ systemInfo.platform?.name || '永续合约做市策略回测平台' }}
                </el-descriptions-item>
                <el-descriptions-item label="版本号">
                  {{ systemInfo.platform?.version || '1.0.0' }}
                </el-descriptions-item>
                <el-descriptions-item label="支持交易对">
                  {{ systemInfo.supported_symbols?.join(', ') || 'ETH/USDC' }}
                </el-descriptions-item>
                <el-descriptions-item label="支持时间周期">
                  {{ systemInfo.timeframes?.join(', ') || '1m, 5m, 15m, 1h, 4h, 1d' }}
                </el-descriptions-item>
                <el-descriptions-item label="数据范围">
                  {{ formatDataRange() }}
                </el-descriptions-item>
                <el-descriptions-item label="最后更新">
                  {{ formatTime(systemInfo.timestamp) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </el-col>
        
        <!-- 操作按钮 -->
        <el-col :span="24">
          <el-card header="系统操作">
            <div class="action-buttons">
              <el-button type="primary" @click="saveSettings">
                <el-icon><Check /></el-icon>
                保存设置
              </el-button>
              
              <el-button @click="resetSettings">
                <el-icon><Refresh /></el-icon>
                重置设置
              </el-button>
              
              <el-button @click="exportSettings">
                <el-icon><Download /></el-icon>
                导出配置
              </el-button>
              
              <el-button @click="clearCache">
                <el-icon><Delete /></el-icon>
                清除缓存
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { formatTime } from '@/utils/format'
import { ElMessage } from 'element-plus'
import {
  Moon,
  Sunny,
  Check,
  Refresh,
  Download,
  Delete,
  TrendCharts
} from '@element-plus/icons-vue'

// Router
const router = useRouter()

// Store
const systemStore = useSystemStore()
const { systemInfo, isDark } = storeToRefs(systemStore)

// 导航路由
const navRoutes = computed(() => {
  return router.getRoutes().filter(route =>
    route.meta?.title && route.name !== 'home' && route.name !== 'login' && route.name !== 'test'
  )
})

// 设置项
const language = ref('zh-CN')
const chartTheme = ref('binance')
const defaultTimeframe = ref('1m')
const defaultLeverage = ref(125)
const defaultSpread = ref(0.002)
const cacheTimeout = ref(3600)
const autoSave = ref(true)

// 方法
const toggleTheme = () => {
  systemStore.toggleTheme()
}

const formatDataRange = () => {
  if (systemInfo.value.data_range) {
    return `${systemInfo.value.data_range.start} 至 ${systemInfo.value.data_range.end}`
  }
  return '2019-11-01 至 2025-06-15'
}

const saveSettings = () => {
  // 保存设置到localStorage
  const settings = {
    language: language.value,
    chartTheme: chartTheme.value,
    defaultTimeframe: defaultTimeframe.value,
    defaultLeverage: defaultLeverage.value,
    defaultSpread: defaultSpread.value,
    cacheTimeout: cacheTimeout.value,
    autoSave: autoSave.value
  }
  
  localStorage.setItem('userSettings', JSON.stringify(settings))
  ElMessage.success('设置已保存')
}

const resetSettings = () => {
  language.value = 'zh-CN'
  chartTheme.value = 'binance'
  defaultTimeframe.value = '1m'
  defaultLeverage.value = 125
  defaultSpread.value = 0.002
  cacheTimeout.value = 3600
  autoSave.value = true
  
  ElMessage.success('设置已重置')
}

const exportSettings = () => {
  const settings = {
    language: language.value,
    chartTheme: chartTheme.value,
    defaultTimeframe: defaultTimeframe.value,
    defaultLeverage: defaultLeverage.value,
    defaultSpread: defaultSpread.value,
    cacheTimeout: cacheTimeout.value,
    autoSave: autoSave.value
  }
  
  const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'trading-platform-settings.json'
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('配置已导出')
}

const clearCache = () => {
  // 清除缓存
  localStorage.removeItem('klineCache')
  localStorage.removeItem('backtestCache')
  
  ElMessage.success('缓存已清除')
}

const loadSettings = () => {
  try {
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      const settings = JSON.parse(saved)
      language.value = settings.language || 'zh-CN'
      chartTheme.value = settings.chartTheme || 'binance'
      defaultTimeframe.value = settings.defaultTimeframe || '1m'
      defaultLeverage.value = settings.defaultLeverage || 125
      defaultSpread.value = settings.defaultSpread || 0.002
      cacheTimeout.value = settings.cacheTimeout || 3600
      autoSave.value = settings.autoSave !== undefined ? settings.autoSave : true
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.settings-view {
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

.settings-content {
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
  
  .unit {
    margin-left: 8px;
    color: var(--text-secondary);
    font-size: 12px;
  }
}

.system-info {
  :deep(.el-descriptions) {
    .el-descriptions__header {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
    
    .el-descriptions__body {
      .el-descriptions__table {
        border-color: var(--border-color);
        
        .el-descriptions__cell {
          border-color: var(--border-color);
          
          &.is-bordered-label {
            background: var(--bg-tertiary);
            color: var(--text-primary);
          }
          
          &.is-bordered-content {
            background: var(--bg-secondary);
            color: var(--text-primary);
          }
        }
      }
    }
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
