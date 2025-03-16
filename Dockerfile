FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装基础依赖和工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置入口脚本权限
RUN chmod +x docker-entrypoint.sh

# 创建必要目录
RUN mkdir -p /app/logs /app/data /app/sessions

# 暴露端口
EXPOSE 5000

# 设置入口点
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# 启动应用
CMD ["python", "app.py"] 