# 使用轻量级的 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置 Python 环境变量，确保日志实时刷新到 stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装必要的系统库（针对 cryptography 编译）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8099

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8099"]
