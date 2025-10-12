# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

1) 常用终端命令（Windows PowerShell 友好）
- 安装依赖：npm install
- 前端开发服务器（Vite，:5173）：npm run dev
- 后端 API 服务器（Express，:8001）：npm run server
- 备用后端热更新（读取 nodemon.json）：npx nodemon
- 构建前端（输出 dist/）：npm run build
- 预览构建产物：npm run preview
- 测试（vitest）：
  - 运行全部：npm run test
  - 监听模式：npm run test:watch
  - UI 模式：npm run test:ui
  - 单文件：npx vitest run tests/format.test.ts
  - 按测试名：npm run test -- -t "formatPrice"
- 说明：package.json 未配置 lint 脚本（无 eslint 命令）

2) 架构与整体流程（高层概览）
- 前端（src/）：React + Vite + Ant Design + Zustand
  - 状态：src/stores（klineStore、backtestStore、uiStore）管理 K 线/回测/UI；
    - klineStore 通过 klineService 拉取 K 线与交易信号并缓存；
    - backtestStore 调用 backtestService 启动/轮询/获取回测结果；
  - 页面：
    - KlinePage 渲染 ECharts K 线（components/charts/EChartsKlineChart），可配合 SignalMarkers 表格查看/导出信号；
    - BacktestResultPage 启动回测、轮询状态并用 Recharts 显示资金曲线（EquityCurveChart）与指标（BacktestResultVisualization）。
  - 服务：src/services/* 以 fetch 封装 API（api.ts 暴露 API_ENDPOINTS），klineService/backtestService 为领域服务；
  - 类型：src/types/* 定义 K 线、策略、回测等类型；
  - 代理：vite.config.ts 将 /api 转发到 http://localhost:8001，便于本地联调。
- 后端（api/）：Express 应用（api/app.ts）
  - 路由：
    - /api/v1/kline（以及 /api/kline、/range、/stats、/symbols、/timeframes、/signals）
    - /api/v1/strategy（策略参数校验与模板占位）
    - /api/v1/backtest（启动、查询状态、获取结果、历史与删除）
  - 数据桥接（K 线读取）：/api/v1/kline 内部通过 child_process.spawn 调用本地 Python 脚本 api/scripts/read_h5.py 解析 H5 数据；
    - H5 路径取自 config/default.js 的 DEFAULT_CONFIG.data.h5FilePath / h5BackupPath，亦可用环境变量 H5_FILE_PATH / H5_BACKUP_PATH 覆盖；
    - Python 解释器路径按平台定位 .venv（Windows: .venv\Scripts\python.exe；Unix: .venv/bin/python）。
  - 回测（TS 版引擎）：domain/backtest/BacktestService 通过 H5Reader 读取数据并在 Node 内执行简化网格策略；
    - 状态保存在内存 Map，提供 start/status/result/history/delete；
    - 注意：api/domain/backtest/BacktestService.ts 为旧实现（调用外部 backtest_kline_trajectory.py），当前路由未使用该旧版。
- 配置与路径别名：
  - tsconfig.json：@config/* -> config/*；@domain/* -> domain/*；
  - vite.config.ts：'@/' -> src/*，并配置 /api 代理；
  - vercel.json：framework=vite，functions: api/**/*.ts（Node 18），outputDirectory=dist，重写 /api/* 到函数。

3) 运行环境与前置条件
- Node.js（建议 Node 18+，与 Vercel 运行时一致）；
- Python 3.x：在仓库根创建 .venv，并至少安装 h5py 与 numpy（api/scripts/read_h5.py 依赖）；
- H5 数据文件：确保 H5_FILE_PATH 指向 ETHUSDT 1m 数据集（可用 H5_BACKUP_PATH 兜底），或调整 config/default.js 中 DEFAULT_CONFIG.data；
- 本地开发默认：前端 :5173，后端 :8001（vite 代理 /api -> :8001）；
- 如需外网访问（例如 fetch_binance_klines.py 拉取 Binance 数据），请按用户偏好使用本机代理 127.0.0.1:10808（可设置 HTTP_PROXY/HTTPS_PROXY）。

4) 重要提示与易错点
- 文档一致性：docs/API_DOCUMENTATION.md 描述的是旧的 FastAPI 方案，当前后端为 Express，接口路径与行为以 api/routes/* 与 src/services/* 为准；
- 内存态回测：回测状态/结果只保存在内存，重启后端将清空；
- 数据仓储：supabase/ 提供迁移脚本，但现有 Express 路由未启用数据库，除非你主动集成；
- 部署体积：.vercelignore 已排除大文件（H5/CSV 等），vercel.json 仅部署 dist 与 api 函数；
- 安全：请勿在提交中包含任何真实密钥或私密信息（.env 请本地维护）。

5) 关键代码交叉引用（查阅索引）
- package.json：scripts（build/dev/server/test）
- vite.config.ts：别名与 /api 代理
- tsconfig.json：@config、@domain 路径别名
- api/app.ts：路由注册与静态资源服务
- api/routes/kline.ts：H5 读取（spawn .venv python，调用 api/scripts/read_h5.py）与 /api/kline 家族端点
- domain/data/h5/h5reader.ts：解析 H5 路径与 .venv python，可读时间范围与数据
- api/routes/v1/backtest.ts：接入 TS 回测服务
- domain/backtest/BacktestService.ts：简化网格回测引擎与内存状态机
- vercel.json：无服务器部署配置
- tests/format.test.ts：vitest 示例（针对 src/utils/format）
