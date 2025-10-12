import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  LineChartOutlined,
  SettingOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  StockOutlined,
  ControlOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

interface SidebarProps {
  collapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/backtest',
      icon: <LineChartOutlined />,
      label: '策略回测',
    },
    {
      key: '/backtest-visualization',
      icon: <StockOutlined />,
      label: '回测可视化',
    },
    {
      key: '/strategy',
      icon: <ThunderboltOutlined />,
      label: '策略概览',
    },
    {
      key: '/strategy-management',
      icon: <ControlOutlined />,
      label: 'ATR策略管理',
    },
    {
      key: '/data',
      icon: <DatabaseOutlined />,
      label: '数据管理',
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: '分析报告',
    },
    {
      key: '/kline-test',
      icon: <StockOutlined />,
      label: 'K线测试',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      width={240}
      style={{
        background: '#001529',
        boxShadow: '2px 0 8px rgba(0,0,0,0.15)',
      }}
    >
      <div
        style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#002140',
          color: '#fff',
          fontSize: collapsed ? '16px' : '18px',
          fontWeight: 'bold',
          borderBottom: '1px solid #1f1f1f',
        }}
      >
        {collapsed ? 'QT' : '量化交易系统'}
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          borderRight: 0,
          background: '#001529',
        }}
      />
    </Sider>
  );
};

export default Sidebar;