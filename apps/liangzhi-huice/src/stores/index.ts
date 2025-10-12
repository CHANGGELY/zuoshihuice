// 状态管理统一导出

// 重新导出所有store
export * from './klineStore';
export * from './backtestStore';
export * from './uiStore';

// 导出常用的hooks和工具函数
export {
  // UI相关
  useUIStore,
  useTheme,
  useLanguage,
  usePreferences,
  useNotifications,
  useSidebar,
  useModals,
  useGlobalLoading,
  useCurrentPage,
  useBreadcrumbs,
  useWindowSize,
  useBreakpoints,
  showNotification,
  showSuccess,
  showError,
  showWarning,
  showInfo,
} from './uiStore';

// 为了向后兼容，重新导出为useUiStore
export { useUIStore as useUiStore } from './uiStore';