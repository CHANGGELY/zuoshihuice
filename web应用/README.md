# 🚀 永续合约做市策略回测平台

基于 **Django + Vue.js** 的专业永续合约做市策略回测分析平台，提供实时K线图表、策略回测、结果分析等功能。

## ✨ 功能特性

### 📊 实时图表
- **TradingView级别的K线图表** - 基于Lightweight Charts
- **多时间周期支持** - 1m, 5m, 15m, 1h, 4h, 1d
- **交互式操作** - 缩放、拖拽、十字线
- **币安风格界面** - 专业的深色主题

### 🔄 策略回测
- **永续合约做市策略** - 高频双向交易
- **动态杠杆调整** - 智能风险控制
- **参数化配置** - 灵活的策略参数
- **实时进度显示** - 回测过程可视化

### 📈 结果分析
- **详细性能指标** - 收益率、夏普比率、最大回撤
- **权益曲线图** - 资金变化趋势
- **交易分布分析** - 盈亏统计
- **风险指标计算** - 全面的风险评估

### ⚙️ 系统功能
- **前后端分离** - 现代化架构
- **RESTful API** - 标准化接口
- **响应式设计** - 支持多设备
- **主题切换** - 深色/浅色模式

## 🏗️ 技术架构

### 后端技术栈
- **Django 4.2** - Web框架
- **Django REST Framework** - API框架
- **Pandas** - 数据处理
- **NumPy** - 数值计算
- **SQLite** - 数据库（可扩展到PostgreSQL）

### 前端技术栈
- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **Element Plus** - UI组件库
- **Lightweight Charts** - 图表库
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

## 🚀 快速开始

### 环境要求
- **Python 3.8+**
- **Node.js 16+**
- **npm 或 yarn**

### 一键启动
```bash
# 克隆项目
git clone <repository-url>
cd web应用

# 运行启动脚本（自动安装依赖并启动服务）
python 启动脚本.py
```

启动成功后：
- 🌐 **前端地址**: http://localhost:5173
- 🔧 **后端地址**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/admin

### 手动启动

#### 后端启动
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动服务
python manage.py runserver 0.0.0.0:8000
```

#### 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
web应用/
├── backend/                    # Django后端
│   ├── trading_platform/      # 项目配置
│   ├── api/                   # 基础API
│   ├── market_data/           # 市场数据模块
│   ├── backtest/              # 回测模块
│   ├── requirements.txt       # Python依赖
│   └── manage.py             # Django管理脚本
├── frontend/                  # Vue前端
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   ├── services/        # API服务
│   │   └── utils/           # 工具函数
│   ├── package.json         # Node.js依赖
│   └── vite.config.js       # Vite配置
├── 启动脚本.py               # 一键启动脚本
└── README.md                # 项目文档
```

## 🔧 配置说明

### 后端配置
编辑 `backend/.env` 文件：
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
DATA_ROOT=../K线data
```

### 前端配置
编辑 `frontend/.env` 文件：
```env
VITE_APP_TITLE=永续合约做市策略回测平台
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## 📊 API接口

### 市场数据
- `GET /api/v1/market/klines/` - 获取K线数据
- `GET /api/v1/market/stats/` - 获取市场统计
- `GET /api/v1/market/symbols/` - 获取交易对列表
- `GET /api/v1/market/timeframes/` - 获取时间周期列表

### 回测接口
- `POST /api/v1/backtest/run/` - 运行回测
- `GET /api/v1/backtest/results/` - 获取回测结果
- `GET /api/v1/backtest/history/` - 获取历史回测

### 系统接口
- `GET /api/v1/health/` - 健康检查
- `GET /api/v1/status/` - 系统状态
- `GET /api/v1/info/` - 系统信息

## 🎯 使用指南

### 1. 查看实时图表
- 访问主页面查看ETH/USDC的实时K线图表
- 使用工具栏切换时间周期
- 通过鼠标操作缩放和拖拽图表

### 2. 运行策略回测
- 进入"策略回测"页面
- 配置回测参数（时间范围、杠杆、价差等）
- 点击"开始回测"运行策略
- 查看实时回测进度和结果

### 3. 分析回测结果
- 进入"结果分析"页面
- 查看详细的性能指标
- 分析权益曲线和交易分布
- 导出分析报告

### 4. 系统设置
- 进入"系统设置"页面
- 配置界面主题和默认参数
- 查看系统信息和状态
- 管理缓存和配置

## 🔄 开发计划

### 已完成 ✅
- [x] Django后端API框架
- [x] Vue前端应用框架
- [x] TradingView图表集成
- [x] 市场数据接口
- [x] 基础UI界面
- [x] 主题切换功能

### 进行中 🚧
- [ ] 回测引擎集成
- [ ] 实时数据推送
- [ ] 用户认证系统

### 计划中 📋
- [ ] 多策略支持
- [ ] 实盘交易接口
- [ ] 移动端适配
- [ ] 数据库优化
- [ ] 性能监控
- [ ] 单元测试

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
