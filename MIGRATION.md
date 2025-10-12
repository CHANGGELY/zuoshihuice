# 迁移说明（8001/3000 → 8000）

本次迁移的目标是“前后端一体化”：只保留 FastAPI 后端（端口 8000），前端静态页也由它直接提供，所有请求同源无跨域问题。

## 1. 如何启动
- Windows（推荐）
  1) 双击或在终端运行 `start_web_system.bat`
  2) 浏览器自动打开 http://localhost:8000
- 手动方式
  ```powershell
  # 可选：启用本地代理
  $env:HTTP_PROXY = "http://127.0.0.1:10808"
  $env:HTTPS_PROXY = $env:HTTP_PROXY

  # 启动服务
  python -m uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8000 --reload
  ```

## 2. 目录与配置
- 数据目录（可改）：`K线data/` 通过环境变量 `DATA_DIR` 覆盖
- 缓存目录（可改）：`cache/` 通过环境变量 `CACHE_DIR` 覆盖
- 进度文件：写入 `CACHE_DIR/progress.json`

## 3. API 变化
- 统一端口：
  - 旧：前端 3000，后端 8001
  - 新：前端+后端都在 8000（前端从 `/` 访问，接口 `/health`、`/klines`、`/backtest`、`/progress`）
- `/klines`：支持 symbol/timeframe/start_date/end_date，并自动在 `DATA_DIR` 下匹配 `{symbol}_1m_*.h5`

## 4. Docker/Compose
- 构建（注意：容器内访问宿主代理使用 host.docker.internal）
  ```sh
  docker build \
    --build-arg HTTP_PROXY=http://host.docker.internal:10808 \
    --build-arg HTTPS_PROXY=http://host.docker.internal:10808 \
    -t kline-backtest:local .

  docker run --rm -p 8000:8000 \
    -e HTTP_PROXY=http://host.docker.internal:10808 \
    -e HTTPS_PROXY=http://host.docker.internal:10808 \
    -e DATA_DIR=/app/K线data -e CACHE_DIR=/app/cache \
    -v %cd%/K线data:/app/K线data \
    -v %cd%/cache:/app/cache \
    kline-backtest:local
  ```
- Compose（已简化，仅 backend）：
  ```sh
  docker compose up --build
  ```

## 5. 依赖与质量（建议一劳永逸）
- 用 pip-tools 生成锁定文件：
  ```powershell
  python -m pip install -U pip setuptools wheel pip-tools
  pip-compile --resolver=backtracking requirements.in -o requirements.txt
  pip-compile --resolver=backtracking requirements-dev.in -o requirements-dev.txt
  pip install -r requirements-dev.txt
  ```
- 安装 pre-commit 并启用：
  ```powershell
  pre-commit install
  pre-commit run -a
  ```
- CI 会在 GitHub 上自动执行：ruff/black/mypy/pytest。

## 6. 常见问题
- 代理：
  - 本机：`http://127.0.0.1:10808`
  - 容器：`http://host.docker.internal:10808`
- “卷挂载”：把容器内目录映射到本地，例如 `-v ./cache:/app/cache`，删容器数据不丢。
- HDF5 数据文件太大？已默认不提交缓存（cache/），建议用卷持久化。
