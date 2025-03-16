FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
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