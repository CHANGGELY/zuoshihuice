import api from './api'

// 认证服务
export const authService = {
  // 用户注册
  register: (userData) => api.post('/auth/register/', userData),
  
  // 用户登录
  login: (credentials) => api.post('/auth/login/', credentials),
  
  // 用户登出
  logout: () => api.post('/auth/logout/'),
  
  // 获取用户信息
  getProfile: () => api.get('/auth/profile/'),
  
  // 更新用户信息
  updateProfile: (userData) => api.put('/auth/profile/', userData),
}
