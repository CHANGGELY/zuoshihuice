# 前后端架构与API错误分析

## 分析时间
2025年8月2日 23:35

## 问题诊断

### 1. 根本原因分析

项目目前存在**架构设计混乱**的核心问题：

#### 1.1 双服务器架构冲突
- **Express 服务器**：运行在端口 3001，提供 K线数据 API
- **FastAPI 服务器**：运行在端口 8000，也提供 K线数据 API
- **前端配置**：硬编码请求 `http://localhost:8000`，但实际运行的是 Express 服务器

#### 1.2 路由配置不一致
- 前端期望：`/api/v1/kline/data` (配置指向端口 8000)
- Express 路由：`/api/v1/kline` 和 `/api/kline` (运行在端口 3001)
- FastAPI 路由：`/api/v1/kline` (运行在端口 8000)

#### 1.3 数据文件路径硬编码
- Express：`c:\\Users\\chuan\\Desktop\\zuoshihuice\\zuoshihuice\\ETHUSDT_1m_2019-11-01_to_2025-06-15.h5`
- FastAPI：相同的硬编码路径
- 风险：路径不可移植，依赖特定用户目录

### 2. 前端错误现象

根据用户界面显示的错误：
- **Failed to fetch**：网络连接失败
- **数据加载失败 [object Object]**：API 响应格式不匹配

### 3. 启动脚本混淆

- `start_web_system.bat`：启动旧版本的 Python 服务器
- `package.json`：配置 Express 服务器
- 用户不清楚应该启动哪个服务器

## 架构重构建议

### 方案A：前后端不分离架构（推荐）

#### 优点
- **简化部署**：单一服务器，减少配置复杂度
- **减少API错误**：无跨域问题，无端口冲突
- **更容易维护**：统一技术栈
- **降低学习成本**：减少前后端协调工作

#### 实现方案
1. **保留 Express 服务器作为主服务器**
2. **移除 FastAPI 服务器**
3. **Express 同时提供静态文件和 API 服务**
4. **前端打包后直接服务于 Express**

#### 具体步骤
```bash
# 1. 修改 vite.config.ts 添加代理
server: {
  proxy: {
    '/api': 'http://localhost:3001'
  }
}

# 2. 修改 api.ts
baseURL: '', // 使用相对路径

# 3. 简化启动命令
npm run build && npm start
```

### 方案B：保持前后端分离但修复配置

#### 实现步骤
1. **统一端口配置**
2. **添加 Vite 代理配置**
3. **修复路由一致性**
4. **添加 CORS 正确配置**

## 立即修复建议

### 1. 最小修复（保持当前架构）

```typescript
// vite.config.ts
export default defineConfig({
  // ... 其他配置
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 或 3001，取决于选择哪个服务器
        changeOrigin: true,
        secure: false
      }
    }
  }
});
```

```typescript
// src/services/api.ts
const API_CONFIG = {
  baseURL: process.env.NODE_ENV === 'development' ? '' : 'http://localhost:8000',
  // 开发环境使用代理，生产环境使用绝对路径
};
```

### 2. 路径修复

```python
# api/routes/h5_kline.py
import os
from pathlib import Path

# 动态获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
H5_FILE_PATH = PROJECT_ROOT / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"
```

### 3. 启动脚本统一

创建新的 `start.bat`：
```batch
@echo off
echo 启动交易系统...
echo 1. Express + React (推荐)
echo 2. FastAPI + React
choice /c 12 /m "请选择启动模式"
if errorlevel 2 goto fastapi
if errorlevel 1 goto express

:express
npm run build
npm start
goto end

:fastapi
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
goto end

:end
pause
```

## 技术债务清理

### 需要删除的文件
- `后端回测服务器.py`
- `前端服务器.py`
- `start_web_system.bat`
- 重复的 API 实现

### 需要重构的组件
- API 客户端配置
- 错误处理机制
- 数据加载逻辑

## 结论

**强烈建议采用方案A（前后端不分离）**，理由：

1. **项目规模适中**：不是大型系统，无需复杂架构
2. **团队规模小**：减少协调成本
3. **部署更简单**：单一服务器部署
4. **错误更少**：避免跨域和端口配置问题
5. **维护成本低**：统一的技术栈和构建流程

当前的架构混乱是导致 API 错误的根本原因，需要进行彻底的架构重构才能解决问题。