import React, { useState } from 'react';
import { Layout, Button, Space, Badge, Dropdown, Avatar, Typography } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BulbOutlined,
  BulbFilled,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  WifiOutlined,
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

interface HeaderProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  darkMode: boolean;
  setDarkMode: (darkMode: boolean) => void;
}

const Header: React.FC<HeaderProps> = ({
  collapsed,
  setCollapsed,
  darkMode,
  setDarkMode,
}) => {
  const [notificationCount] = useState(0); // 真实的通知数量
  const serverStatus = '服务器运行正常'; // 临时硬编码状态
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const isServerOnline = serverStatus?.includes('正常') || false;

  return (
    <AntHeader
      style={{
        padding: '0 16px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => setCollapsed(!collapsed)}
          style={{
            fontSize: '16px',
            width: 64,
            height: 64,
          }}
        />
        <Space size="middle" style={{ marginLeft: '16px' }}>
          <Badge
            status={isServerOnline ? 'success' : 'error'}
            text={
              <Text type={isServerOnline ? 'success' : 'danger'}>
                <WifiOutlined style={{ marginRight: '4px' }} />
                {serverStatus}
              </Text>
            }
          />
        </Space>
      </div>

      <Space size="middle">
        <Button
          type="text"
          icon={darkMode ? <BulbFilled /> : <BulbOutlined />}
          onClick={() => setDarkMode(!darkMode)}
          style={{ fontSize: '16px' }}
        />
        
        <Badge count={notificationCount} size="small">
          <Button
            type="text"
            icon={<BellOutlined />}
            style={{ fontSize: '16px' }}
          />
        </Badge>

        <Dropdown
          menu={{ items: userMenuItems }}
          placement="bottomRight"
          arrow
        >
          <Space style={{ cursor: 'pointer' }}>
            <Avatar size="small" icon={<UserOutlined />} />
            <Text>管理员</Text>
          </Space>
        </Dropdown>
      </Space>
    </AntHeader>
  );
};

export default Header;