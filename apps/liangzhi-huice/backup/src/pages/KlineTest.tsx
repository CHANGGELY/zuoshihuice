import React from 'react';
import { Card, Typography } from 'antd';
import KlineChart from '../components/KlineChart';

const { Title, Paragraph } = Typography;

const KlineTest: React.FC = () => {
  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Card style={{ marginBottom: '24px' }}>
          <Title level={2}>K线图表测试页面</Title>
          <Paragraph>
            这个页面用于测试K线图表组件是否能正确从后端API获取并显示ETHUSDT历史数据。
            如果API连接失败，将自动切换到模拟数据展示。
          </Paragraph>
        </Card>
        
        <Card>
          <KlineChart 
            symbol="ETHUSDT" 
            height={600} 
          />
        </Card>
      </div>
    </div>
  );
};

export default KlineTest;