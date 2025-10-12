// 认证服务

import { apiClient } from './api';
import { ApiResponse } from '../types';

// 登录请求接口
interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应接口
interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    username: string;
    email: string;
    full_name?: string;
  };
}

// 用户信息接口
interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

class AuthService {
  // 登录
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);
      
      if (response.success && response.data) {
        // 保存token到localStorage
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Login failed',
      };
    }
  }

  // 注册
  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }): Promise<ApiResponse<any>> {
    try {
      return await apiClient.post('/api/auth/register', userData);
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Registration failed',
      };
    }
  }

  // 登出
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  // 获取当前用户信息
  getCurrentUser(): any | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // 检查是否已登录
  isAuthenticated(): boolean {
    const token = localStorage.getItem('token');
    return !!token;
  }

  // 获取token
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  // 验证token
  async verifyToken(): Promise<ApiResponse<any>> {
    try {
      return await apiClient.get('/api/auth/verify');
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Token verification failed',
      };
    }
  }

  // 获取用户资料
  async getProfile(): Promise<ApiResponse<UserProfile>> {
    try {
      return await apiClient.get<UserProfile>('/api/auth/profile');
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get profile',
      };
    }
  }

  // 刷新token
  async refreshToken(): Promise<ApiResponse<LoginResponse>> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return {
          success: false,
          message: 'No refresh token available',
        };
      }

      const response = await apiClient.post<LoginResponse>('/api/auth/refresh', {
        refresh_token: refreshToken,
      });

      if (response.success && response.data) {
        // 更新token
        localStorage.setItem('token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
      }

      return response;
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Token refresh failed',
      };
    }
  }
}

// 创建认证服务实例
export const authService = new AuthService();

// 导出类型
export type { LoginRequest, LoginResponse, UserProfile };