// 量化策略前端应用主组件

import React, { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { Toaster } from 'sonner';
import { router } from './router';
import { useUIStore } from './stores';
import { ErrorBoundary } from './components/common';
import 'dayjs/locale/zh-cn';
import dayjs from 'dayjs';

// 设置dayjs中文
dayjs.locale('zh-cn');

// 主应用组件
const App: React.FC = () => {
  const { theme: currentTheme, language, setWindowSize } = useUIStore();

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      setWindowSize(window.innerWidth, window.innerHeight);
    };

    // 初始化窗口大小
    handleResize();

    // 添加事件监听
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [setWindowSize]);

  // Ant Design主题配置
  const antdTheme = {
    algorithm: currentTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
      wireframe: false,
    },
    components: {
      Layout: {
        headerBg: currentTheme === 'dark' ? '#001529' : '#ffffff',
        siderBg: currentTheme === 'dark' ? '#001529' : '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
      },
    },
  };

  return (
    <ErrorBoundary>
      <ConfigProvider
        theme={antdTheme}
        locale={language === 'zh-CN' ? zhCN : undefined}
      >
        <AntdApp>
          <div className="app" data-theme={currentTheme}>
            <RouterProvider router={router} />
            
            {/* 全局通知组件 */}
            <Toaster
              position="top-right"
              expand
              richColors
              closeButton
              theme={currentTheme === 'auto' ? 'system' : currentTheme}
            />
          </div>
        </AntdApp>
      </ConfigProvider>
    </ErrorBoundary>
  );
};

export default App;