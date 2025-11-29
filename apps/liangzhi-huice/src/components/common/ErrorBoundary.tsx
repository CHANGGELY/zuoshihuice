// ErrorBoundary 错误边界组件

import React from 'react';
import { Result, Button, Typography, Collapse, Space } from 'antd';
import {
  ExclamationCircleOutlined,
  ReloadOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useUIStore } from '../../stores';

const { Text, Paragraph } = Typography;

// 错误信息接口
interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
  errorBoundaryStack?: string;
}

// ErrorBoundary状态
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

// ErrorBoundary属性
export interface ErrorBoundaryProps {
  children: React.ReactNode;
  // 自定义错误页面
  fallback?: React.ComponentType<{
    error: Error;
    errorInfo: ErrorInfo;
    resetError: () => void;
  }>;
  // 错误回调
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  // 是否显示详细错误信息
  showDetails?: boolean;
  // 是否自动重试
  autoRetry?: boolean;
  // 重试次数
  maxRetries?: number;
  // 重试间隔（毫秒）
  retryInterval?: number;
  // 是否显示返回首页按钮
  showHomeButton?: boolean;
}

// 错误类型
type ErrorType = 'chunk' | 'network' | 'runtime' | 'unknown';

// 错误分类函数
const getErrorType = (error: Error): ErrorType => {
  const message = error.message.toLowerCase();
  
  if (message.includes('loading chunk') || message.includes('loading css chunk')) {
    return 'chunk';
  }
  
  if (message.includes('network') || message.includes('fetch')) {
    return 'network';
  }
  
  return 'runtime';
};

// 错误信息格式化
const getErrorMessage = (error: Error, errorType: ErrorType): string => {
  switch (errorType) {
    case 'chunk':
      return '应用更新了，请刷新页面重新加载';
    case 'network':
      return '网络连接异常，请检查网络后重试';
    case 'runtime':
      return '应用运行时发生错误，请重试或联系技术支持';
    default:
      return error.message || '发生未知错误';
  }
};

// 错误详情组件
const ErrorDetails: React.FC<{
  error: Error;
  errorInfo: ErrorInfo;
  errorId: string;
}> = ({ error, errorInfo, errorId }) => (
  <Collapse ghost items={[{
    key: 'details',
    label: '查看错误详情',
    children: (
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>错误ID：</Text>
          <Text code>{errorId}</Text>
        </div>
        
        <div>
          <Text strong>错误信息：</Text>
          <Paragraph>
            <Text code>{error.message}</Text>
          </Paragraph>
        </div>
        
        <div>
          <Text strong>错误堆栈：</Text>
          <Paragraph>
            <pre style={{ 
              fontSize: '12px', 
              backgroundColor: '#f5f5f5', 
              padding: '8px',
              borderRadius: '4px',
              overflow: 'auto',
              maxHeight: '200px'
            }}>
              {error.stack}
            </pre>
          </Paragraph>
        </div>
        
        {errorInfo.componentStack && (
          <div>
            <Text strong>组件堆栈：</Text>
            <Paragraph>
              <pre style={{ 
                fontSize: '12px', 
                backgroundColor: '#f5f5f5', 
                padding: '8px',
                borderRadius: '4px',
                overflow: 'auto',
                maxHeight: '200px'
              }}>
                {errorInfo.componentStack}
              </pre>
            </Paragraph>
          </div>
        )}
      </Space>
    )
  }]} />
);

// ErrorBoundary类组件
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  private retryCount = 0;
  private retryTimer: NodeJS.Timeout | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // 生成错误ID
    const errorId = `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { onError } = this.props;
    
    this.setState({ errorInfo });
    
    // 调用错误回调
    if (onError) {
      onError(error, errorInfo);
    }
    
    // 显示错误通知
    // const errorType = getErrorType(error); // 暂时未使用
    // const errorMessage = getErrorMessage(error, errorType); // 暂时未使用
    
    // 错误通知将在render中显示，这里只记录日志
    
    // 记录错误日志
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // 发送错误报告（如果需要）
    this.reportError(error, errorInfo);
    
    // 自动重试
    if (this.props.autoRetry && this.shouldRetry(error)) {
      this.scheduleRetry();
    }
  }

  // 判断是否应该重试
  private shouldRetry = (error: Error): boolean => {
    const { maxRetries = 3 } = this.props;
    const errorType = getErrorType(error);
    
    // 只对特定类型的错误进行重试
    if (errorType === 'chunk' || errorType === 'network') {
      return this.retryCount < maxRetries;
    }
    
    return false;
  };

  // 安排重试
  private scheduleRetry = () => {
    const { retryInterval = 3000 } = this.props;
    
    this.retryTimer = setTimeout(() => {
      this.retryCount++;
      this.resetError();
    }, retryInterval);
  };

  // 重置错误状态
  private resetError = () => {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer);
      this.retryTimer = null;
    }
    
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });
  };

  // 手动重试
  private handleRetry = () => {
    this.retryCount = 0;
    this.resetError();
  };

  // 刷新页面
  private handleRefresh = () => {
    window.location.reload();
  };

  // 返回首页
  private handleGoHome = () => {
    window.location.href = '/';
  };

  // 发送错误报告
  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    // 这里可以集成错误监控服务，如 Sentry、Bugsnag 等
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        errorId: this.state.errorId,
      };
      
      // 发送到错误监控服务
      // errorMonitoringService.captureException(errorReport);
      
      console.log('Error report:', errorReport);
    } catch (reportError) {
      console.error('Failed to report error:', reportError);
    }
  };

  componentWillUnmount() {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer);
    }
  }

  render() {
    const { hasError, error, errorInfo, errorId } = this.state;
    const {
      children,
      fallback: Fallback,
      showDetails = true,
      showHomeButton = true,
    } = this.props;

    if (hasError && error && errorInfo) {
      // 使用自定义错误页面
      if (Fallback) {
        return (
          <Fallback
            error={error}
            errorInfo={errorInfo}
            resetError={this.resetError}
          />
        );
      }

      // 默认错误页面
      const errorType = getErrorType(error);
      const errorMessage = getErrorMessage(error, errorType);
      
      return (
        <div style={{ padding: '50px 20px', textAlign: 'center' }}>
          <Result
            status="error"
            icon={<ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />}
            title="应用发生错误"
            subTitle={errorMessage}
            extra={[
              <Button
                key="retry"
                type="primary"
                icon={<ReloadOutlined />}
                onClick={this.handleRetry}
              >
                重试
              </Button>,
              <Button
                key="refresh"
                icon={<ReloadOutlined />}
                onClick={this.handleRefresh}
              >
                刷新页面
              </Button>,
              showHomeButton && (
                <Button
                  key="home"
                  icon={<HomeOutlined />}
                  onClick={this.handleGoHome}
                >
                  返回首页
                </Button>
              ),
            ].filter(Boolean)}
          >
            {showDetails && (
              <ErrorDetails
                error={error}
                errorInfo={errorInfo}
                errorId={errorId}
              />
            )}
          </Result>
        </div>
      );
    }

    return children;
  }
}

// 函数式错误边界Hook
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);
  const { showError } = useUIStore();
  
  const resetError = React.useCallback(() => {
    setError(null);
  }, []);
  
  const captureError = React.useCallback((error: Error) => {
    setError(error);
    showError(error.message, '操作失败');
  }, [showError]);
  
  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);
  
  return { captureError, resetError };
};

// 异步错误处理Hook
export const useAsyncError = () => {
  const { captureError } = useErrorHandler();
  
  return React.useCallback(
    (error: Error) => {
      // 在下一个事件循环中抛出错误，让ErrorBoundary捕获
      setTimeout(() => {
        captureError(error);
      }, 0);
    },
    [captureError]
  );
};

// 简化的错误边界组件
export const SimpleErrorBoundary: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => (
  <ErrorBoundary showDetails={false} autoRetry maxRetries={1}>
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;