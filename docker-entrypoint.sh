#!/bin/bash
set -e

# 创建必要的目录
mkdir -p /app/logs
mkdir -p /app/data
mkdir -p /app/sessions

# 检查数据库文件目录
if [ ! -d "/app/instance" ]; then
  mkdir -p /app/instance
fi

# 检查是否需要调整数据库URI路径
if grep -q "sqlite:///telegram_forwarder.db" /app/.env; then
  echo "调整数据库路径为持久化存储位置..."
  sed -i 's|sqlite:///telegram_forwarder.db|sqlite:///data/telegram_forwarder.db|g' /app/.env
fi

# 处理Telegram登录
echo "正在检查Telegram登录配置..."

# 检查是否有TG验证码等待处理
if [ -n "$TG_LOGIN_CODE" ]; then
  echo "发现预设的Telegram验证码，将用于登录"
  # 确保环境变量在容器中可见
  export TG_LOGIN_CODE
fi

# 检查是否有二次验证密码
if [ -n "$TG_2FA_PASSWORD" ]; then
  echo "发现Telegram二次验证密码配置"
  export TG_2FA_PASSWORD
fi

# 设置自动确认
if [ "$TG_ALWAYS_CONFIRM" = "true" ]; then
  echo "已启用自动确认模式"
  export TG_ALWAYS_CONFIRM=true
fi

echo "Telegram配置处理完成，准备启动应用..."

# 运行应用
exec "$@" 