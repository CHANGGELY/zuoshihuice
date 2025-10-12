// UI状态管理

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  Theme,
  Language,
  UserPreferences,
  NotificationInfo,
  NotificationType,
} from '../types';

// UI状态接口
interface UIState {
  // 主题和外观
  theme: Theme;
  language: Language;
  
  // 用户偏好设置
  preferences: UserPreferences;
  
  // 通知系统
  notifications: NotificationInfo[];
  
  // 侧边栏和布局
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  
  // 模态框和弹窗
  modals: {
    strategyConfig: boolean;
    backtestHistory: boolean;
    settings: boolean;
    help: boolean;
  };
  
  // 加载状态
  globalLoading: boolean;
  
  // 页面状态
  currentPage: string;
  breadcrumbs: Array<{ label: string; path: string }>;
  
  // 窗口尺寸
  windowSize: {
    width: number;
    height: number;
  };
  
  // 响应式断点
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
}

// UI操作接口
interface UIActions {
  // 主题控制
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  
  // 语言控制
  setLanguage: (language: Language) => void;
  
  // 偏好设置
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  resetPreferences: () => void;
  
  // 通知管理
  addNotification: (notification: Omit<NotificationInfo, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // 侧边栏控制
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarWidth: (width: number) => void;
  
  // 模态框控制
  openModal: (modalName: keyof UIState['modals']) => void;
  closeModal: (modalName: keyof UIState['modals']) => void;
  closeAllModals: () => void;
  
  // 全局加载状态
  setGlobalLoading: (loading: boolean) => void;
  
  // 页面导航
  setCurrentPage: (page: string) => void;
  setBreadcrumbs: (breadcrumbs: Array<{ label: string; path: string }>) => void;
  
  // 窗口尺寸
  setWindowSize: (width: number, height: number) => void;
  updateBreakpoints: () => void;
  
  // 初始化
  initialize: () => void;
  
  // 通知快捷方法
  showError: (message: string, title?: string) => void;
  showSuccess: (message: string, title?: string) => void;
  showWarning: (message: string, title?: string) => void;
  showInfo: (message: string, title?: string) => void;
}

// 默认偏好设置
const defaultPreferences: UserPreferences = {
  theme: 'dark',
  language: 'zh-CN',
  autoSave: true,
  notifications: true,
  soundEnabled: false,
  chartSettings: {
    defaultTimeframe: '1h',
    showVolume: true,
    showGrid: true,
    autoScale: true,
  },
  tableSettings: {
    pageSize: 20,
    showBorders: true,
    compactMode: false,
  },
};

// 初始状态
const initialState: UIState = {
  theme: 'dark',
  language: 'zh-CN',
  
  preferences: defaultPreferences,
  
  notifications: [],
  
  sidebarCollapsed: false,
  sidebarWidth: 280,
  
  modals: {
    strategyConfig: false,
    backtestHistory: false,
    settings: false,
    help: false,
  },
  
  globalLoading: false,
  
  currentPage: '/',
  breadcrumbs: [],
  
  windowSize: {
    width: window.innerWidth || 1920,
    height: window.innerHeight || 1080,
  },
  
  isMobile: false,
  isTablet: false,
  isDesktop: true,
};

// 创建UI状态管理
export const useUIStore = create<UIState & UIActions>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // 设置主题
        setTheme: (theme: Theme) => {
          set({ theme });
          document.documentElement.setAttribute('data-theme', theme);
        },

        // 切换主题
        toggleTheme: () => {
          const currentTheme = get().theme;
          const newTheme = currentTheme === 'light' ? 'dark' : 'light';
          get().setTheme(newTheme);
        },

        // 设置语言
        setLanguage: (language: Language) => {
          set({ language });
          document.documentElement.setAttribute('lang', language);
        },

        // 更新偏好设置
        updatePreferences: (newPreferences: Partial<UserPreferences>) => {
          const currentPreferences = get().preferences;
          const updatedPreferences = {
            ...currentPreferences,
            ...newPreferences,
          };
          
          set({ preferences: updatedPreferences });
          
          // 同步主题和语言
          if (newPreferences.theme) {
            get().setTheme(newPreferences.theme);
          }
          if (newPreferences.language) {
            get().setLanguage(newPreferences.language);
          }
        },

        // 重置偏好设置
        resetPreferences: () => {
          set({ preferences: defaultPreferences });
          get().setTheme(defaultPreferences.theme);
          get().setLanguage(defaultPreferences.language);
        },

        // 添加通知
        addNotification: (notification: Omit<NotificationInfo, 'id' | 'timestamp'>) => {
          const newNotification: NotificationInfo = {
            ...notification,
            id: Date.now().toString(),
            timestamp: Date.now(),
          };
          
          set({
            notifications: [...get().notifications, newNotification],
          });

          // 自动移除通知（除非是错误类型）
          if (notification.type !== NotificationType.ERROR) {
            setTimeout(() => {
              get().removeNotification(newNotification.id);
            }, notification.duration || 5000);
          }
        },

        // 移除通知
        removeNotification: (id: string) => {
          set({
            notifications: get().notifications.filter(n => n.id !== id),
          });
        },

        // 清除所有通知
        clearNotifications: () => {
          set({ notifications: [] });
        },

        // 切换侧边栏
        toggleSidebar: () => {
          set({ sidebarCollapsed: !get().sidebarCollapsed });
        },

        // 设置侧边栏折叠状态
        setSidebarCollapsed: (collapsed: boolean) => {
          set({ sidebarCollapsed: collapsed });
        },

        // 设置侧边栏宽度
        setSidebarWidth: (width: number) => {
          set({ sidebarWidth: Math.max(200, Math.min(400, width)) });
        },

        // 打开模态框
        openModal: (modalName: keyof UIState['modals']) => {
          set({
            modals: {
              ...get().modals,
              [modalName]: true,
            },
          });
        },

        // 关闭模态框
        closeModal: (modalName: keyof UIState['modals']) => {
          set({
            modals: {
              ...get().modals,
              [modalName]: false,
            },
          });
        },

        // 关闭所有模态框
        closeAllModals: () => {
          set({
            modals: {
              strategyConfig: false,
              backtestHistory: false,
              settings: false,
              help: false,
            },
          });
        },

        // 设置全局加载状态
        setGlobalLoading: (loading: boolean) => {
          set({ globalLoading: loading });
        },

        // 设置当前页面
        setCurrentPage: (page: string) => {
          set({ currentPage: page });
        },

        // 设置面包屑
        setBreadcrumbs: (breadcrumbs: Array<{ label: string; path: string }>) => {
          set({ breadcrumbs });
        },

        // 设置窗口尺寸
        setWindowSize: (width: number, height: number) => {
          set({ windowSize: { width, height } });
          get().updateBreakpoints();
        },

        // 更新响应式断点
        updateBreakpoints: () => {
          const { width } = get().windowSize;
          
          set({
            isMobile: width < 768,
            isTablet: width >= 768 && width < 1024,
            isDesktop: width >= 1024,
          });
        },

        // 初始化
        initialize: () => {
          const { theme, language, preferences } = get();
          
          // 设置主题
          document.documentElement.setAttribute('data-theme', theme);
          
          // 设置语言
          document.documentElement.setAttribute('lang', language);
          
          // 监听窗口尺寸变化
          const handleResize = () => {
            get().setWindowSize(window.innerWidth, window.innerHeight);
          };
          
          window.addEventListener('resize', handleResize);
          
          // 初始化窗口尺寸
          handleResize();
          
          // 监听系统主题变化
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          const handleThemeChange = (e: MediaQueryListEvent) => {
            if (preferences.theme === 'auto') {
              get().setTheme(e.matches ? 'dark' : 'light');
            }
          };
          
          mediaQuery.addEventListener('change', handleThemeChange);
          
          // 清理函数
          return () => {
            window.removeEventListener('resize', handleResize);
            mediaQuery.removeEventListener('change', handleThemeChange);
          };
        },
        
        // 通知快捷方法
        showError: (message: string, title?: string) => {
          get().addNotification({
            type: NotificationType.ERROR,
            title: title || 'Error',
            message,
            duration: 0, // 错误通知不自动消失
          });
        },
        
        showSuccess: (message: string, title?: string) => {
          get().addNotification({
            type: NotificationType.SUCCESS,
            title: title || 'Success',
            message,
          });
        },
        
        showWarning: (message: string, title?: string) => {
          get().addNotification({
            type: NotificationType.WARNING,
            title: title || 'Warning',
            message,
          });
        },
        
        showInfo: (message: string, title?: string) => {
          get().addNotification({
            type: NotificationType.INFO,
            title: title || 'Info',
            message,
          });
        },
      }),
      {
        name: 'ui-store',
        partialize: (state) => ({
          theme: state.theme,
          language: state.language,
          preferences: state.preferences,
          sidebarCollapsed: state.sidebarCollapsed,
          sidebarWidth: state.sidebarWidth,
        }),
      }
    ),
    {
      name: 'ui-store',
    }
  ));

// 选择器
export const useTheme = () => useUIStore((state) => state.theme);
export const useLanguage = () => useUIStore((state) => state.language);
export const usePreferences = () => useUIStore((state) => state.preferences);
export const useNotifications = () => useUIStore((state) => state.notifications);
export const useSidebar = () => {
  const collapsed = useUIStore((state) => state.sidebarCollapsed);
  const width = useUIStore((state) => state.sidebarWidth);
  return { collapsed, width };
};
export const useModals = () => useUIStore((state) => state.modals);
export const useGlobalLoading = () => useUIStore((state) => state.globalLoading);
export const useCurrentPage = () => useUIStore((state) => state.currentPage);
export const useBreadcrumbs = () => useUIStore((state) => state.breadcrumbs);
export const useWindowSize = () => useUIStore((state) => state.windowSize);
export const useBreakpoints = () => useUIStore((state) => ({
  isMobile: state.isMobile,
  isTablet: state.isTablet,
  isDesktop: state.isDesktop,
}));

// 工具函数
export const showNotification = (notification: Omit<NotificationInfo, 'id' | 'timestamp'>) => {
  useUIStore.getState().addNotification(notification);
};

export const showSuccess = (message: string, title?: string) => {
  showNotification({
    type: NotificationType.SUCCESS,
    title: title || 'Success',
    message,
  });
};

export const showError = (message: string, title?: string) => {
  showNotification({
    type: NotificationType.ERROR,
    title: title || 'Error',
    message,
    duration: 0, // 错误通知不自动消失
  });
};

export const showWarning = (message: string, title?: string) => {
  showNotification({
    type: NotificationType.WARNING,
    title: title || 'Warning',
    message,
  });
};

export const showInfo = (message: string, title?: string) => {
  showNotification({
    type: NotificationType.INFO,
    title: title || 'Info',
    message,
  });
};