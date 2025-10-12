import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, ConfigProvider, theme, App as AntdApp } from 'antd';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import BacktestPage from './pages/BacktestPage';
// import BacktestVisualizationPage from './pages/BacktestVisualizationPage';
import StrategyPage from './pages/StrategyPage';
import StrategyManagementPage from './pages/StrategyManagementPage';
import DataPage from './pages/DataPage';
import AnalysisPage from './pages/AnalysisPage';
import KlineTest from './pages/KlineTest';

const { Content } = Layout;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <AntdApp>
        <Router>
          <Layout style={{ minHeight: '100vh' }}>
            <Sidebar collapsed={collapsed} />
            <Layout>
              <Header
                collapsed={collapsed}
                setCollapsed={setCollapsed}
                darkMode={darkMode}
                setDarkMode={setDarkMode}
              />
              <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/backtest" element={<BacktestPage />} />
                  {/* <Route path="/backtest-visualization" element={<BacktestVisualizationPage />} /> */}
                  <Route path="/strategy" element={<StrategyPage />} />
                  <Route path="/strategy-management" element={<StrategyManagementPage />} />
                  <Route path="/data" element={<DataPage />} />
                  <Route path="/analysis" element={<AnalysisPage />} />
                  <Route path="/kline-test" element={<KlineTest />} />
                </Routes>
              </Content>
            </Layout>
          </Layout>
        </Router>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;