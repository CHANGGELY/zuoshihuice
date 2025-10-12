# 变更日志

## Unreleased

### 重大变更
- 统一后端与前端：仅保留 FastAPI (端口 8000)，移除旧 http.server 后端与独立前端服务器。
- 前端静态页改为由 FastAPI 托管：`/` 返回 `fastapi_backend/static/index.html`，前端调用改为同源相对路径。
- 进度与缓存目录参数化：新增 `fastapi_backend/settings.py`，进度文件与缓存写到 `CACHE_DIR`（默认 `cache/`）。
- `/klines` 数据文件动态发现：默认在 `DATA_DIR`（默认 `K线data/`）匹配 `{symbol}_1m_*.h5`，并将周期缓存写到 `cache/klines/{symbol}/`。

### 构建与部署
- 重写 `Dockerfile`：优化层缓存；支持构建时代理 `HTTP_PROXY/HTTPS_PROXY`；容器内默认 `DATA_DIR=/app/K线data`、`CACHE_DIR=/app/cache`。
- 精简 `docker-compose.yml`：仅保留 `backend` 服务；通过卷挂载持久化 `K线data/` 与 `cache/`；加入 `host.docker.internal` 以访问宿主机代理。
- 更新 `start_web_system.bat`：仅启动 FastAPI:8000 并打开首页；自动创建数据与缓存目录；读取本地 HTTP 代理。

### 质量与依赖
- 新增 `pyproject.toml`（black/ruff/mypy/pytest 配置）。
- 新增 `requirements.in` / `requirements-dev.in`（建议用 pip-tools 生成锁定文件）。
- 新增 `.pre-commit-config.yaml`（提交前自动格式化/检查/测试）。
- 新增 GitHub Actions 工作流 `.github/workflows/ci.yml`（lint/typecheck/test + 可选 Docker 构建）。
- 更新 `.gitignore`：忽略 `.venv/`、`cache/`、`.pytest_cache/`、`.env`。

### 移除
- 删除 `后端回测服务器.py`（旧 http.server 后端）。
- 删除 `前端服务器.py`（独立前端服务）。
