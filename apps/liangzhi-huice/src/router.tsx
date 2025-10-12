// 路由配置

import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { Header } from './components/common';
import { KlinePage } from './pages/KlinePage';
import { BacktestResultPage } from './pages/BacktestResultPage';

const { Content } = Layout;

// 主布局组件
const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header />
      <Content style={{ padding: '24px' }}>
        {children}
      </Content>
    </Layout>
  );
};

// 路由配置
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/kline" replace />,
  },
  {
    path: '/kline',
    element: (
      <MainLayout>
        <KlinePage />
      </MainLayout>
    ),
  },
  {
    path: '/backtest',
    element: (
      <MainLayout>
        <BacktestResultPage />
      </MainLayout>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/kline" replace />,
  },
]);