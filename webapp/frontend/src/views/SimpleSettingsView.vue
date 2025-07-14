<template>
  <div class="settings-view">
    <div class="header">
      <h1>系统设置</h1>
      <div class="nav-buttons">
        <el-button @click="$router.push('/trading')">交易图表</el-button>
        <el-button @click="$router.push('/backtest')">策略回测</el-button>
        <el-button @click="$router.push('/analysis')">结果分析</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    
    <div class="content">
      <div class="settings-panel">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 基本设置 -->
          <el-tab-pane label="基本设置" name="basic">
            <el-form :model="basicSettings" label-width="120px" size="default">
              <el-form-item label="系统主题">
                <el-radio-group v-model="basicSettings.theme">
                  <el-radio value="light">浅色主题</el-radio>
                  <el-radio value="dark">深色主题</el-radio>
                  <el-radio value="auto">跟随系统</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="语言设置">
                <el-select v-model="basicSettings.language" placeholder="选择语言">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="时区设置">
                <el-select v-model="basicSettings.timezone" placeholder="选择时区">
                  <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                  <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                  <el-option label="伦敦时间 (UTC+0)" value="Europe/London" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="自动保存">
                <el-switch v-model="basicSettings.autoSave" />
                <span class="setting-desc">自动保存回测参数和结果</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
                <el-button @click="resetBasicSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 交易设置 -->
          <el-tab-pane label="交易设置" name="trading">
            <el-form :model="tradingSettings" label-width="120px" size="default">
              <el-form-item label="默认交易对">
                <el-select v-model="tradingSettings.defaultSymbol" placeholder="选择默认交易对">
                  <el-option label="ETH/USDC" value="ETHUSDC" />
                  <el-option label="BTC/USDT" value="BTCUSDT" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="默认杠杆">
                <el-input-number 
                  v-model="tradingSettings.defaultLeverage" 
                  :min="1" 
                  :max="125" 
                  :step="1"
                />
              </el-form-item>
              
              <el-form-item label="风险限制">
                <el-input-number 
                  v-model="tradingSettings.riskLimit" 
                  :min="0.01" 
                  :max="1" 
                  :step="0.01"
                  :precision="2"
                />
                <span class="setting-desc">单笔交易最大风险比例</span>
              </el-form-item>
              
              <el-form-item label="滑点容忍">
                <el-input-number 
                  v-model="tradingSettings.slippageTolerance" 
                  :min="0.0001" 
                  :max="0.01" 
                  :step="0.0001"
                  :precision="4"
                />
                <span class="setting-desc">最大可接受滑点</span>
              </el-form-item>
              
              <el-form-item label="启用止损">
                <el-switch v-model="tradingSettings.enableStopLoss" />
              </el-form-item>
              
              <el-form-item label="启用止盈">
                <el-switch v-model="tradingSettings.enableTakeProfit" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveTradingSettings">保存设置</el-button>
                <el-button @click="resetTradingSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 数据设置 -->
          <el-tab-pane label="数据设置" name="data">
            <el-form :model="dataSettings" label-width="120px" size="default">
              <el-form-item label="数据源">
                <el-radio-group v-model="dataSettings.dataSource">
                  <el-radio value="local">本地数据</el-radio>
                  <el-radio value="api">API接口</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="缓存大小">
                <el-input-number 
                  v-model="dataSettings.cacheSize" 
                  :min="100" 
                  :max="10000" 
                  :step="100"
                />
                <span class="setting-desc">MB</span>
              </el-form-item>
              
              <el-form-item label="数据更新频率">
                <el-select v-model="dataSettings.updateFrequency" placeholder="选择更新频率">
                  <el-option label="实时" value="realtime" />
                  <el-option label="每分钟" value="1min" />
                  <el-option label="每5分钟" value="5min" />
                  <el-option label="每小时" value="1hour" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="历史数据范围">
                <el-input-number 
                  v-model="dataSettings.historyRange" 
                  :min="30" 
                  :max="365" 
                  :step="30"
                />
                <span class="setting-desc">天</span>
              </el-form-item>
              
              <el-form-item label="数据压缩">
                <el-switch v-model="dataSettings.compression" />
                <span class="setting-desc">启用数据压缩以节省存储空间</span>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveDataSettings">保存设置</el-button>
                <el-button @click="resetDataSettings">重置</el-button>
                <el-button type="warning" @click="clearCache">清除缓存</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 系统信息 -->
          <el-tab-pane label="系统信息" name="system">
            <div class="system-info">
              <div class="info-group">
                <h3>版本信息</h3>
                <div class="info-item">
                  <span class="label">系统版本:</span>
                  <span class="value">v1.0.0</span>
                </div>
                <div class="info-item">
                  <span class="label">构建时间:</span>
                  <span class="value">2024-07-12 10:30:00</span>
                </div>
                <div class="info-item">
                  <span class="label">Git提交:</span>
                  <span class="value">abc123def456</span>
                </div>
              </div>
              
              <div class="info-group">
                <h3>运行状态</h3>
                <div class="info-item">
                  <span class="label">运行时间:</span>
                  <span class="value">2天 5小时 30分钟</span>
                </div>
                <div class="info-item">
                  <span class="label">内存使用:</span>
                  <span class="value">256MB / 1GB</span>
                </div>
                <div class="info-item">
                  <span class="label">CPU使用率:</span>
                  <span class="value">15%</span>
                </div>
              </div>
              
              <div class="info-group">
                <h3>数据统计</h3>
                <div class="info-item">
                  <span class="label">总回测次数:</span>
                  <span class="value">1,247</span>
                </div>
                <div class="info-item">
                  <span class="label">数据记录数:</span>
                  <span class="value">2,345,678</span>
                </div>
                <div class="info-item">
                  <span class="label">缓存命中率:</span>
                  <span class="value">89.5%</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('basic')

const basicSettings = reactive({
  theme: 'light',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  autoSave: true
})

const tradingSettings = reactive({
  defaultSymbol: 'ETHUSDC',
  defaultLeverage: 10,
  riskLimit: 0.02,
  slippageTolerance: 0.001,
  enableStopLoss: true,
  enableTakeProfit: true
})

const dataSettings = reactive({
  dataSource: 'local',
  cacheSize: 1000,
  updateFrequency: '1min',
  historyRange: 180,
  compression: true
})

const saveBasicSettings = () => {
  ElMessage.success('基本设置已保存')
}

const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    theme: 'light',
    language: 'zh-CN',
    timezone: 'Asia/Shanghai',
    autoSave: true
  })
  ElMessage.info('基本设置已重置')
}

const saveTradingSettings = () => {
  ElMessage.success('交易设置已保存')
}

const resetTradingSettings = () => {
  Object.assign(tradingSettings, {
    defaultSymbol: 'ETHUSDC',
    defaultLeverage: 10,
    riskLimit: 0.02,
    slippageTolerance: 0.001,
    enableStopLoss: true,
    enableTakeProfit: true
  })
  ElMessage.info('交易设置已重置')
}

const saveDataSettings = () => {
  ElMessage.success('数据设置已保存')
}

const resetDataSettings = () => {
  Object.assign(dataSettings, {
    dataSource: 'local',
    cacheSize: 1000,
    updateFrequency: '1min',
    historyRange: 180,
    compression: true
  })
  ElMessage.info('数据设置已重置')
}

const clearCache = () => {
  ElMessage.success('缓存已清除')
}

const handleLogout = () => {
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.settings-view {
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
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.settings-panel {
  padding: 20px;
}

.setting-desc {
  margin-left: 10px;
  font-size: 12px;
  color: #666;
}

.system-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.info-group h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 2px solid #02c076;
  padding-bottom: 5px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px 0;
}

.info-item:last-child {
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

h1 {
  color: #333;
  margin: 0;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}
</style>
