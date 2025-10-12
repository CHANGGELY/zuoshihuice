// 通用类型定义

// API响应基础接口
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  code?: number;
}

// 分页参数接口
export interface PaginationParams {
  page: number;
  page_size: number;
  total?: number;
}

// 分页响应接口
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 加载状态接口
export interface LoadingState {
  isLoading: boolean;
  progress: number;
  message: string;
}

// 错误信息接口
export interface ErrorInfo {
  message: string;
  code?: string | number;
  details?: any;
  timestamp?: number;
}

// 通知类型
export enum NotificationType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

// 通知接口
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  timestamp: number;
}

// 通知信息接口（别名）
export interface NotificationInfo extends Notification {}

// 主题类型
export type Theme = 'light' | 'dark' | 'auto';

// 语言类型
export type Language = 'zh-CN' | 'en-US';

// 用户偏好设置
export interface UserPreferences {
  theme: Theme;
  language: Language;
  autoSave: boolean;
  notifications: boolean;
  soundEnabled: boolean;
  chartSettings: {
    defaultTimeframe: string;
    showVolume: boolean;
    showGrid: boolean;
    autoScale: boolean;
  };
  tableSettings: {
    pageSize: number;
    showBorders: boolean;
    compactMode: boolean;
  };
}

// 应用状态接口
export interface AppState {
  initialized: boolean;
  loading: boolean;
  error: ErrorInfo | null;
  notifications: Notification[];
  preferences: UserPreferences;
}

// 选择器选项接口
export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
  description?: string;
}

// 表格列配置接口
export interface TableColumn {
  key: string;
  title: string;
  dataIndex: string;
  width?: number;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: any, index: number) => React.ReactNode;
}

// 图表数据点接口
export interface ChartDataPoint {
  x: number | string;
  y: number;
  label?: string;
  color?: string;
}

// 时间范围接口
export interface TimeRange {
  start: string;
  end: string;
  label?: string;
}

// 导出所有子模块类型
export * from './kline';
export * from './strategy';
export * from './backtest';