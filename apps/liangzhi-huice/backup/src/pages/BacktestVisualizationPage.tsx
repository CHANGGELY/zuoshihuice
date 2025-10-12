import React from 'react';
import { Typography } from 'antd';
import BacktestVisualization from '../components/BacktestVisualization';

const { Title } = Typography;

const BacktestVisualizationPage: React.FC = () => {
  return (
    <div style={{ padding: '0' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>回测可视化</Title>
        <p style={{ color: '#666', marginTop: '8px' }}>ATR对冲网格策略回测结果可视化分析</p>
      </div>
      <BacktestVisualization />
    </div>
  );
};

export default BacktestVisualizationPage;