# 量智回测平台（Liangzhi Backtest Platform）

单一仓库下整合了 Web 前端、Node.js API 与 Python 回测引擎，目录结构如下：

- `apps/liangzhi-huice/`：React + Vite 前端与 Express API 服务，包含业务代码、配置与 Supabase 集成。
- `services/backtest-engine/`：Python 回测脚本、缓存与 H5 数据文件，支持 ATR 自适应网格策略分析。
- `ops/`：部署与运维脚本（PowerShell、Batch），已指向新的应用目录。
- `.vercel/`：Vercel 本地项目配置，默认根目录已设置为 `apps/liangzhi-huice`。
- `docs/` 与其他历史资料保留在原位置（如 `.ai_memory`、`.trae`），可按需迁移或归档。

### 本地运行

1. 安装 Node.js 依赖：`cd apps/liangzhi-huice && npm install`
2. 运行前端/服务端开发模式：`npm run dev`
3. Python 回测引擎：`cd services/backtest-engine && python backtest_kline_trajectory.py`

默认的 H5 数据路径已统一指向 `services/backtest-engine`，可通过环境变量 `H5_FILE_PATH` 覆盖。Git LFS 用于管理 `.h5`、`.pkl` 等大文件，提交代码前请确保已安装并拉取对应对象。
