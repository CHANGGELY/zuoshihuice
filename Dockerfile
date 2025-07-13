# 多阶段构建 - 前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY web应用/frontend/package*.json ./
RUN npm ci --only=production

COPY web应用/frontend/ ./
RUN npm run build

# Python后端阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖文件
COPY fastapi_backend/requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY fastapi_backend/ ./fastapi_backend/
COPY backtest_kline_trajectory.py ./
COPY cache/ ./cache/
COPY K线data/ ./K线data/
COPY 回测结果.db ./

# 复制前端构建结果
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
