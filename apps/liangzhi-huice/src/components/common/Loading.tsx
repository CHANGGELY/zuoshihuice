// Loading 加载组件

import React from 'react';
import { Spin, SpinProps } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { useGlobalLoading } from '../../stores/uiStore';

// Loading组件属性
export interface LoadingProps extends Omit<SpinProps, 'spinning'> {
  // 是否显示加载状态
  loading?: boolean;
  // 加载文本
  text?: string;
  // 是否全屏加载
  fullscreen?: boolean;
  // 是否使用全局加载状态
  useGlobal?: boolean;
  // 自定义加载图标
  icon?: React.ReactNode;
  // 最小加载时间（毫秒）
  minDuration?: number;
  // 延迟显示时间（毫秒）
  delay?: number;
}

// 自定义加载图标
const CustomLoadingIcon = () => (
  <LoadingOutlined
    style={{
      fontSize: 24,
      color: '#1890ff',
    }}
    spin
  />
);

// 全屏加载样式
const fullscreenStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.8)',
  zIndex: 9999,
  backdropFilter: 'blur(2px)',
};

// 深色主题全屏加载样式
const fullscreenDarkStyle: React.CSSProperties = {
  ...fullscreenStyle,
  backgroundColor: 'rgba(0, 0, 0, 0.8)',
};

// Loading组件
export const Loading: React.FC<LoadingProps> = ({
  loading: propLoading,
  text = '加载中...',
  fullscreen = false,
  useGlobal = false,
  icon,
  minDuration = 0,
  delay = 0,
  children,
  size = 'default',
  ...spinProps
}) => {
  const globalLoading = useGlobalLoading();
  const [showLoading, setShowLoading] = React.useState(false);
  const [isDarkTheme, setIsDarkTheme] = React.useState(false);
  
  // 确定是否显示加载状态
  const isLoading = useGlobal ? globalLoading : propLoading;
  
  // 检测主题
  React.useEffect(() => {
    const checkTheme = () => {
      const theme = document.documentElement.getAttribute('data-theme');
      setIsDarkTheme(theme === 'dark');
    };
    
    checkTheme();
    
    // 监听主题变化
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
    
    return () => observer.disconnect();
  }, []);
  
  // 处理延迟显示和最小持续时间
  React.useEffect(() => {
    let delayTimer: NodeJS.Timeout;
    let minDurationTimer: NodeJS.Timeout;
    
    if (isLoading) {
      if (delay > 0) {
        delayTimer = setTimeout(() => {
          setShowLoading(true);
        }, delay);
      } else {
        setShowLoading(true);
      }
    } else {
      if (showLoading && minDuration > 0) {
        minDurationTimer = setTimeout(() => {
          setShowLoading(false);
        }, minDuration);
      } else {
        setShowLoading(false);
      }
    }
    
    return () => {
      if (delayTimer) clearTimeout(delayTimer);
      if (minDurationTimer) clearTimeout(minDurationTimer);
    };
  }, [isLoading, delay, minDuration, showLoading]);
  
  // 如果不显示加载状态，直接返回子组件
  if (!showLoading) {
    return <>{children}</>;
  }
  
  // 加载指示器
  const loadingIndicator = icon ? (React.isValidElement(icon) ? icon : <CustomLoadingIcon />) : <CustomLoadingIcon />;
  
  // 全屏加载
  if (fullscreen) {
    return (
      <>
        {children}
        <div style={isDarkTheme ? fullscreenDarkStyle : fullscreenStyle}>
          <Spin
            indicator={loadingIndicator}
            size={size}
            {...spinProps}
          />
          <div style={{ marginTop: 16, color: isDarkTheme ? '#fff' : '#000' }}>{text}</div>
        </div>
      </>
    );
  }
  
  // 普通加载
  return (
    <Spin
      spinning={showLoading}
      indicator={loadingIndicator}
      size={size}
      {...spinProps}
    >
      {children}
    </Spin>
  );
};

// 简化的加载组件
export const SimpleLoading: React.FC<{ size?: 'small' | 'default' | 'large' }> = ({
  size = 'default',
}) => (
  <div style={{ textAlign: 'center', padding: '20px' }}>
    <Spin size={size} />
  </div>
);

// 全屏加载组件
export const FullscreenLoading: React.FC<{ text?: string }> = ({
  text = '加载中...',
}) => (
  <Loading fullscreen loading text={text} />
);

// 页面加载组件
export const PageLoading: React.FC<{ text?: string }> = ({
  text = '页面加载中...',
}) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '200px',
      width: '100%',
    }}
  >
    <div style={{ textAlign: 'center' }}>
      <Spin size="large" />
      <div style={{ marginTop: 16 }}>{text}</div>
    </div>
  </div>
);

// 表格加载组件
export const TableLoading: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div style={{ padding: '20px' }}>
    {Array.from({ length: rows }, (_, index) => (
      <div
        key={index}
        style={{
          height: '40px',
          backgroundColor: '#f5f5f5',
          marginBottom: '8px',
          borderRadius: '4px',
          animation: 'pulse 1.5s ease-in-out infinite',
        }}
      />
    ))}
    <style>
      {`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}
    </style>
  </div>
);

// 图表加载组件
export const ChartLoading: React.FC<{ height?: number }> = ({
  height = 400,
}) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: `${height}px`,
      backgroundColor: '#fafafa',
      borderRadius: '6px',
      border: '1px solid #d9d9d9',
    }}
  >
    <div style={{ textAlign: 'center' }}>
      <Spin size="large" />
      <div style={{ marginTop: 16 }}>图表加载中...</div>
    </div>
  </div>
);

// 按钮加载组件
export const ButtonLoading: React.FC<{
  loading: boolean;
  children: React.ReactNode;
}> = ({ loading, children }) => (
  <>
    {loading && <LoadingOutlined style={{ marginRight: 8 }} />}
    {children}
  </>
);

export default Loading;