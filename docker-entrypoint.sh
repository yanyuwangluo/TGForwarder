#!/bin/bash
set -e

# 输出彩色日志信息
log_info() {
  echo -e "\033[32m[INFO]\033[0m $1"
}

log_warn() {
  echo -e "\033[33m[WARN]\033[0m $1"
}

log_error() {
  echo -e "\033[31m[ERROR]\033[0m $1"
}

# 创建必要的目录
log_info "正在检查并创建必要的目录..."
mkdir -p /app/logs
mkdir -p /app/sessions

# Telegram API信息输入检查
if [ -z "$TG_API_ID" ] || [ -z "$TG_API_HASH" ] || [ -z "$TG_PHONE" ]; then
  log_warn "缺少Telegram API必要参数，即将进入交互式输入模式"
  
  # 如果没有提供API ID，请求输入
  if [ -z "$TG_API_ID" ]; then
    read -p "请输入您的Telegram API ID: " TG_API_ID
    export TG_API_ID
  fi
  
  # 如果没有提供API Hash，请求输入
  if [ -z "$TG_API_HASH" ]; then
    read -p "请输入您的Telegram API Hash: " TG_API_HASH
    export TG_API_HASH
  fi
  
  # 如果没有提供Phone，请求输入
  if [ -z "$TG_PHONE" ]; then
    read -p "请输入您的电话号码(格式如 +8613800138000): " TG_PHONE
    export TG_PHONE
  fi
fi

log_info "使用的API ID: $TG_API_ID"
log_info "使用的电话号码: $TG_PHONE"

# 设置正确的权限
log_info "设置目录权限..."
chmod -R 755 /app/logs
chmod -R 755 /app/sessions

# 处理Telegram登录
log_info "正在检查Telegram登录配置..."

# 检查是否有TG验证码等待处理
if [ -n "$TG_LOGIN_CODE" ]; then
  log_info "发现预设的Telegram验证码，将用于登录"
  export TG_LOGIN_CODE
fi

# 检查是否有二次验证密码
if [ -n "$TG_2FA_PASSWORD" ]; then
  log_info "发现Telegram二次验证密码配置"
  export TG_2FA_PASSWORD
fi

# 设置自动确认
if [ "$TG_ALWAYS_CONFIRM" = "true" ]; then
  log_info "已启用自动确认模式"
  export TG_ALWAYS_CONFIRM=true
fi

log_info "Telegram配置处理完成，准备启动应用..."

# 捕获终止信号
trap 'log_info "接收到终止信号，正在关闭应用..."; exit 0' SIGTERM SIGINT

# 运行应用
log_info "启动应用..."
exec python app.py --api-id "$TG_API_ID" --api-hash "$TG_API_HASH" --phone "$TG_PHONE"