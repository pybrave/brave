# ============================
# Stage 1: Build frontend
# ============================
FROM node:22-bullseye-slim AS frontend

# 安装 git
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/brave-ui

# 浅克隆仓库（只获取最新 commit）
RUN git clone --depth 1 https://github.com/pybrave/brave-ui.git . 
ENV NODE_OPTIONS="--max-old-space-size=4096"

# 安装依赖并构建
RUN yarn install --frozen-lockfile && yarn build

# ============================
# Stage 2: Python backend
# ============================
FROM python:3.10-slim AS backend

# 安装系统依赖
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         git \
#         curl \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
# 复制前端 build 文件
COPY --from=frontend /tmp/brave-ui/dist /app/brave/frontend/build



RUN pip install --no-cache-dir   .  

# 默认命令
CMD ["brave"]
