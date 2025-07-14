import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value
  })
  
  const isAdmin = computed(() => {
    return user.value?.is_staff || false
  })
  
  // 设置认证信息
  const setAuth = (authData) => {
    user.value = authData.user
    token.value = authData.token
    localStorage.setItem('token', authData.token)
    localStorage.setItem('user', JSON.stringify(authData.user))
  }
  
  // 清除认证信息
  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  // 用户注册
  const register = async (userData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.register(userData)
      setAuth(response.data)
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 用户登录
  const login = async (credentials) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.login(credentials)
      setAuth(response.data)
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 用户登出
  const logout = async () => {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (err) {
      console.error('登出请求失败:', err)
    } finally {
      clearAuth()
    }
  }
  
  // 获取用户信息
  const fetchProfile = async () => {
    try {
      if (!token.value) return null
      
      const response = await authService.getProfile()
      user.value = response.data.user
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      return response.data.user
    } catch (err) {
      // Token可能已过期，清除认证信息
      clearAuth()
      throw err
    }
  }
  
  // 更新用户信息
  const updateProfile = async (userData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.updateProfile(userData)
      user.value = response.data.user
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      return response.data.user
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 初始化认证状态
  const initAuth = async () => {
    try {
      // 从localStorage恢复用户信息
      const savedUser = localStorage.getItem('user')
      if (savedUser && token.value) {
        user.value = JSON.parse(savedUser)
        
        // 验证token是否有效
        try {
          await fetchProfile()
        } catch (err) {
          // Token无效，清除认证信息
          clearAuth()
        }
      }
    } catch (err) {
      console.error('初始化认证状态失败:', err)
      clearAuth()
    }
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  return {
    // 状态
    user,
    token,
    loading,
    error,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    
    // 方法
    register,
    login,
    logout,
    fetchProfile,
    updateProfile,
    initAuth,
    clearError,
    setAuth,
    clearAuth
  }
})
