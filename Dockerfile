# Stage 1: Build frontend
# ============================
FROM node:22-bullseye-slim AS frontend

# 减少缓存层
WORKDIR /tmp/brave-ui
COPY brave-ui/package.json brave-ui/yarn.lock ./
RUN yarn install --frozen-lockfile

# 构建前端
COPY brave-ui ./
RUN yarn build

# ============================
# Stage 2: Python backend
# ============================
FROM python:3.10-slim AS backend

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制后端源码
COPY . .

# 从前端阶段复制 build 文件
COPY --from=frontend /tmp/brave-ui/dist /app/brave/frontend/build

# 安装 Python 包并清理缓存
RUN pip install --no-cache-dir .

# 设置默认启动命令
CMD ["brave"]
