import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '@/services/api'

export const useSystemStore = defineStore('system', () => {
  // 状态
  const systemInfo = ref({})
  const systemStatus = ref({})
  const loading = ref(false)
  const error = ref(null)
  
  // 主题设置
  const isDark = ref(localStorage.getItem('theme') === 'dark')
  
  // 获取系统信息
  const fetchSystemInfo = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await apiService.getSystemInfo()
      systemInfo.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('获取系统信息失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 获取系统状态
  const fetchSystemStatus = async () => {
    try {
      const response = await apiService.getSystemStatus()
      systemStatus.value = response.data
    } catch (err) {
      console.error('获取系统状态失败:', err)
    }
  }
  
  // 切换主题
  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    
    // 切换Element Plus主题
    const html = document.documentElement
    if (isDark.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
  
  // 初始化主题
  const initTheme = () => {
    const html = document.documentElement
    if (isDark.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
  
  return {
    // 状态
    systemInfo,
    systemStatus,
    loading,
    error,
    isDark,
    
    // 方法
    fetchSystemInfo,
    fetchSystemStatus,
    toggleTheme,
    initTheme
  }
})
