# 项目截图与生成说明

本页汇总项目的核心可视化截图，并说明如何在本地生成或更新。

## 权益曲线
- 路径：`services/backtest-engine/equity_curve_*.png`
- 生成：运行 `python -X utf8 services/backtest-engine/backtest_kline_trajectory.py`，脚本会在同目录下输出最新的权益曲线图片。

## K线信号（前端）
- 在 `apps/liangzhi-huice` 目录运行 `npm run dev` 启动前端与 API；访问页面生成信号图。
- 后续将通过自动化截图（Playwright）将关键页面保存到 `docs/` 目录，便于展示（待启用）。

> 注意：截图来自真实数据与策略结果，不使用任何模拟数据。
