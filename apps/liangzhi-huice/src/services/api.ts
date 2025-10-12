// 基础API服务

import { ApiResponse } from '../types';

// API配置
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || '', // 使用相对路径，开发环境通过 Vite 代理转发
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// HTTP客户端类
class ApiClient {
  private baseURL: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;

  constructor(config = API_CONFIG) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
    this.defaultHeaders = config.headers;
  }

  // 构建完整URL
  private buildURL(endpoint: string): string {
    return `${this.baseURL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  }

  // 处理响应（增强空体/非JSON容错）
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const status = response.status;
    const contentType = response.headers.get('content-type') || '';

    // 204 或无内容时直接返回
    if (status === 204) {
      return { success: response.ok };
    }

    let parsed: any = null;
    let rawText: string | null = null;

    try {
      if (contentType.includes('application/json')) {
        // 优先按 JSON 解析
        parsed = await response.json();
      } else {
        // 非 JSON 尝试按文本读取再尽力解析
        rawText = await response.text();
        if (rawText && rawText.trim().length > 0) {
          try {
            parsed = JSON.parse(rawText);
          } catch {
            parsed = null;
          }
        }
      }
    } catch (e) {
      // response.json() 抛错（多为空响应体），尝试读取文本
      try {
        rawText = await response.text();
      } catch {
        rawText = null;
      }
    }

    if (!response.ok) {
      const message = (parsed && (parsed.message || parsed.error)) || (rawText && rawText.trim()) || `HTTP Error: ${status}`;
      return { success: false, message, code: status };
    }

    // 成功但无体
    if (parsed == null) {
      return { success: true };
    }

    return {
      success: true,
      data: (parsed && (parsed.data ?? parsed)) as T,
      message: (parsed && parsed.message) || undefined,
    };
  }

  // 获取认证token
  private getAuthToken(): string | null {
    return localStorage.getItem('token');
  }

  // 通用请求方法
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = this.buildURL(endpoint);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    // 添加认证头
    const token = this.getAuthToken();
    const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.defaultHeaders,
          ...authHeaders,
          ...((options.headers as Record<string, string>) || {}),
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return await this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return {
            success: false,
            message: 'Request timeout',
          };
        }
        return {
          success: false,
          message: error.message,
        };
      }

      return {
        success: false,
        message: 'Unknown error occurred',
      };
    }
  }

  // GET请求
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    let url = endpoint;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      url += `?${searchParams.toString()}`;
    }

    return this.request<T>(url, {
      method: 'GET',
    });
  }

  // POST请求
  async post<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // PUT请求
  async put<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // DELETE请求
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  // 上传文件
  async upload<T>(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {}, // 让浏览器自动设置Content-Type
    });
  }
}

// 创建默认API客户端实例
export const apiClient = new ApiClient();

// 导出API客户端类
export { ApiClient };

// 错误处理工具函数
export const handleApiError = (error: any): string => {
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  if (error?.message) {
    return error.message;
  }
  return 'An unknown error occurred';
};

// API端点常量
export const API_ENDPOINTS = {
  // K线数据
  KLINE: '/api/v1/kline',
  KLINE_HISTORY: '/api/v1/kline/history',

  // 交易信号
  SIGNALS: '/api/v1/signals',

  // 策略相关
  STRATEGY: '/api/v1/strategy',
  STRATEGY_VALIDATE: '/api/v1/strategy/validate',

  // 回测相关
  BACKTEST: '/api/v1/backtest',
  BACKTEST_STATUS: '/api/v1/backtest/status',
  BACKTEST_HISTORY: '/api/v1/backtest/history',

  // 基础数据
  SYMBOLS: '/api/v1/symbols',
  TIMEFRAMES: '/api/v1/timeframes',

  // 文件上传
  UPLOAD: '/api/v1/upload',
  UPLOAD_H5: '/api/v1/upload/h5',
} as const;