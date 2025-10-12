// Header 头部导航组件

import React from 'react';
import { Layout, Button, Space, Dropdown, Avatar, Badge, Tooltip } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  SunOutlined,
  MoonOutlined,
  GlobalOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  useTheme,
  useLanguage,
  useNotifications,
  useSidebar,
  useUIStore,
} from '../../stores';

const { Header: AntHeader } = Layout;

// Header组件属性
export interface HeaderProps {
  // 是否显示侧边栏切换按钮
  showSidebarToggle?: boolean;
  // 是否显示面包屑
  showBreadcrumb?: boolean;
  // 自定义标题
  title?: string;
  // 额外的操作按钮
  extra?: React.ReactNode;
}

// 用户菜单项
const getUserMenuItems = (onLogout: () => void) => [
  {
    key: 'profile',
    icon: <UserOutlined />,
    label: '个人资料',
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '设置',
  },
  {
    type: 'divider' as const,
  },
  {
    key: 'logout',
    icon: <LogoutOutlined />,
    label: '退出登录',
    onClick: onLogout,
  },
];

// 语言菜单项
const getLanguageMenuItems = (currentLanguage: string, onLanguageChange: (lang: string) => void) => [
  {
    key: 'zh-CN',
    label: '简体中文',
    onClick: () => onLanguageChange('zh-CN'),
    disabled: currentLanguage === 'zh-CN',
  },
  {
    key: 'en-US',
    label: 'English',
    onClick: () => onLanguageChange('en-US'),
    disabled: currentLanguage === 'en-US',
  },
];

// 通知列表组件
const NotificationList: React.FC<{
  notifications: any[];
  onClear: () => void;
  onItemClick: (id: string) => void;
}> = ({ notifications, onClear, onItemClick }) => {
  if (notifications.length === 0) {
    return (
      <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
        暂无通知
      </div>
    );
  }

  return (
    <div style={{ width: 300, maxHeight: 400, overflow: 'auto' }}>
      <div style={{ padding: '8px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 'bold' }}>通知</span>
          <Button type="link" size="small" onClick={onClear}>
            清空
          </Button>
        </div>
      </div>
      
      {notifications.map((notification) => (
        <div
          key={notification.id}
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid #f0f0f0',
            cursor: 'pointer',
            transition: 'background-color 0.2s',
          }}
          onClick={() => onItemClick(notification.id)}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#f5f5f5';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {notification.title}
          </div>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
            {notification.message}
          </div>
          <div style={{ fontSize: '11px', color: '#999' }}>
            {new Date(notification.timestamp).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
};

// Header组件
export const Header: React.FC<HeaderProps> = ({
  showSidebarToggle = true,
  // showBreadcrumb = true, // 暂时未使用
  title = '量化策略平台',
  extra,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const theme = useTheme();
  const language = useLanguage();
  const notifications = useNotifications();
  const { collapsed } = useSidebar();
  
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const setLanguage = useUIStore((state) => state.setLanguage);
  const clearNotifications = useUIStore((state) => state.clearNotifications);
  const removeNotification = useUIStore((state) => state.removeNotification);
  const openModal = useUIStore((state) => state.openModal);

  // 处理用户菜单点击
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        navigate('/profile');
        break;
      case 'settings':
        openModal('settings');
        break;
      case 'logout':
        handleLogout();
        break;
    }
  };

  // 处理退出登录
  const handleLogout = () => {
    // 清除用户数据
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // 跳转到登录页
    navigate('/login');
  };

  // 处理语言切换
  const handleLanguageChange = (lang: string) => {
    setLanguage(lang as any);
  };

  // 处理通知点击
  const handleNotificationClick = (id: string) => {
    removeNotification(id);
  };

  // 获取页面标题
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/kline':
        return 'K线图表';
      case '/backtest-result':
        return '回测结果';
      case '/strategy':
        return '策略管理';
      case '/history':
        return '历史记录';
      default:
        return title;
    }
  };

  return (
    <AntHeader
      style={{
        padding: '0 16px',
        background: theme === 'dark' ? '#001529' : '#fff',
        borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
      }}
    >
      {/* 左侧区域 */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {showSidebarToggle && (
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={toggleSidebar}
            style={{
              fontSize: '16px',
              width: 40,
              height: 40,
              marginRight: 16,
              color: theme === 'dark' ? '#fff' : '#000',
            }}
          />
        )}
        
        <div style={{ 
          fontSize: '18px', 
          fontWeight: 'bold',
          color: theme === 'dark' ? '#fff' : '#000',
        }}>
          {getPageTitle()}
        </div>
      </div>

      {/* 右侧区域 */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Space size="middle">
          {/* 额外操作 */}
          {extra}
          
          {/* 主题切换 */}
          <Tooltip title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}>
            <Button
              type="text"
              icon={theme === 'dark' ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              style={{
                color: theme === 'dark' ? '#fff' : '#000',
              }}
            />
          </Tooltip>
          
          {/* 语言切换 */}
          <Dropdown
            menu={{
              items: getLanguageMenuItems(language, handleLanguageChange),
            }}
            placement="bottomRight"
          >
            <Button
              type="text"
              icon={<GlobalOutlined />}
              style={{
                color: theme === 'dark' ? '#fff' : '#000',
              }}
            />
          </Dropdown>
          
          {/* 通知 */}
          <Dropdown
            popupRender={() => (
              <div style={{
                backgroundColor: '#fff',
                borderRadius: '6px',
                boxShadow: '0 6px 16px 0 rgba(0, 0, 0, 0.08)',
                border: '1px solid #f0f0f0',
              }}>
                <NotificationList
                  notifications={notifications}
                  onClear={clearNotifications}
                  onItemClick={handleNotificationClick}
                />
              </div>
            )}
            placement="bottomRight"
            trigger={['click']}
          >
            <Badge count={notifications.length} size="small" overflowCount={999999}>
              <Button
                type="text"
                icon={<BellOutlined />}
                style={{
                  color: theme === 'dark' ? '#fff' : '#000',
                }}
              />
            </Badge>
          </Dropdown>
          
          {/* 帮助 */}
          <Tooltip title="帮助">
            <Button
              type="text"
              icon={<QuestionCircleOutlined />}
              onClick={() => openModal('help')}
              style={{
                color: theme === 'dark' ? '#fff' : '#000',
              }}
            />
          </Tooltip>
          
          {/* 用户菜单 */}
          <Dropdown
            menu={{
              items: getUserMenuItems(handleLogout),
              onClick: handleUserMenuClick,
            }}
            placement="bottomRight"
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <Avatar
                size="small"
                icon={<UserOutlined />}
                style={{ marginRight: 8 }}
              />
              <span style={{ color: theme === 'dark' ? '#fff' : '#000' }}>
                用户
              </span>
            </div>
          </Dropdown>
        </Space>
      </div>
    </AntHeader>
  );
};

export default Header;