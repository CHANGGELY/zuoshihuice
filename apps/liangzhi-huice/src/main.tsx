// 量化策略前端应用入口文件

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app';
import './styles/index.css';

// 创建根节点并渲染应用
const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);