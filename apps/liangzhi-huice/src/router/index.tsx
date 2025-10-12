// React Router 配置

import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { Layout } from 'antd';
import { ErrorBoundary, Loading } from '../components/common';

// 懒加载页面组件
const KlinePage = React.lazy(() => import('../pages/KlinePage'));
const BacktestResultPage = React.lazy(() => import('../pages/BacktestResultPage'));
const LoginPage = React.lazy(() => import('../pages/LoginPage'));

// MainLayout组件已移除，直接在路由中使用布局

// 简单布局组件（无侧边栏）
const SimpleLayout: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Content style={{ minHeight: '100vh' }}>
        <ErrorBoundary>
          <Suspense fallback={<Loading fullscreen />}>
            <Outlet />
          </Suspense>
        </ErrorBoundary>
      </Layout.Content>
    </Layout>
  );
};

// 认证保护组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// 路由配置
export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <ErrorBoundary>
        <Suspense fallback={<Loading fullscreen />}>
          <LoginPage />
        </Suspense>
      </ErrorBoundary>
    ),
  },
  {
    path: '/',
    element: <SimpleLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/kline" replace />,
      },
      {
        path: 'kline',
        element: (
          <ProtectedRoute>
            <KlinePage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'backtest',
        element: (
          <ProtectedRoute>
            <BacktestResultPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'backtest/:id',
        element: (
          <ProtectedRoute>
            <BacktestResultPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
  {
    path: '*',
    element: (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
      }}>
        <h1>404 - 页面未找到</h1>
        <p>您访问的页面不存在</p>
        <a href="/">返回首页</a>
      </div>
    ),
  },
]);

// 路由配置类型
export interface RouteConfig {
  path: string;
  name: string;
  icon?: React.ReactNode;
  component?: React.ComponentType;
  children?: RouteConfig[];
  hidden?: boolean;
  meta?: {
    title?: string;
    description?: string;
    requireAuth?: boolean;
    roles?: string[];
  };
}

// 导航菜单配置
export const menuConfig: RouteConfig[] = [
  {
    path: '/kline',
    name: 'K线图表',
    meta: {
      title: 'K线图表',
      description: '实时K线图表和策略配置',
    },
  },
  {
    path: '/backtest',
    name: '回测结果',
    meta: {
      title: '回测结果',
      description: '查看和分析回测结果',
    },
  },
];

// 面包屑配置
export const breadcrumbConfig: Record<string, string[]> = {
  '/': ['首页'],
  '/kline': ['首页', 'K线图表'],
  '/backtest': ['首页', '回测结果'],
  '/backtest/:id': ['首页', '回测结果', '详情'],
};

// 页面标题配置
export const pageTitleConfig: Record<string, string> = {
  '/': '量化策略平台',
  '/kline': 'K线图表 - 量化策略平台',
  '/backtest': '回测结果 - 量化策略平台',
  '/backtest/:id': '回测详情 - 量化策略平台',
};

// 路由守卫Hook
export const useRouteGuard = () => {
  // 这里可以添加路由守卫逻辑
  // 例如：权限验证、登录检查等
  return {
    canAccess: () => {
      // 暂时返回true，后续可以添加权限逻辑
      return true;
    },
    redirectTo: (path: string) => {
      // 重定向逻辑
      window.location.href = path;
    },
  };
};

export default router;