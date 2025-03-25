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
mkdir -p /app/instance

# 显示欢迎信息
echo -e "\033[36m============================================\033[0m"
echo -e "\033[36m        Telegram 转发器配置向导\033[0m"
echo -e "\033[36m============================================\033[0m"
echo

# 交互式输入配置
log_info "请输入Telegram API配置信息"
echo

# 输入API ID
while true; do
  read -p "请输入您的Telegram API ID: " TG_API_ID
  if [[ $TG_API_ID =~ ^[0-9]+$ ]]; then
    break
  else
    echo -e "\033[31m错误：API ID必须是数字\033[0m"
  fi
done

# 输入API Hash
while true; do
  read -p "请输入您的Telegram API Hash: " TG_API_HASH
  if [[ $TG_API_HASH =~ ^[a-f0-9]{32}$ ]]; then
    break
  else
    echo -e "\033[31m错误：API Hash必须是32位十六进制字符\033[0m"
  fi
done

# 输入电话号码
while true; do
  read -p "请输入您的电话号码(格式如 +8613800138000): " TG_PHONE
  # 移除所有空格
  TG_PHONE=$(echo "$TG_PHONE" | tr -d ' ')
  # 如果没有+号，添加+号
  if [[ ! $TG_PHONE =~ ^\+ ]]; then
    TG_PHONE="+$TG_PHONE"
  fi
  # 验证电话号码格式（允许更宽松的格式）
  if [[ $TG_PHONE =~ ^\+[0-9]{8,15}$ ]]; then
    break
  else
    echo -e "\033[31m错误：电话号码格式不正确，请确保包含国家代码\033[0m"
  fi
done

# 显示配置信息
echo
echo -e "\033[36m============================================\033[0m"
echo -e "\033[36m              配置信息确认\033[0m"
echo -e "\033[36m============================================\033[0m"
echo -e "API ID: \033[32m$TG_API_ID\033[0m"
echo -e "API Hash: \033[32m$TG_API_HASH\033[0m"
echo -e "电话号码: \033[32m$TG_PHONE\033[0m"
echo -e "\033[36m============================================\033[0m"
echo

# 确认配置
read -p "确认以上配置信息是否正确？(y/n): " confirm
if [[ $confirm != "y" ]]; then
  echo -e "\033[31m配置已取消，容器将退出\033[0m"
  exit 1
fi

# 设置正确的权限
log_info "设置目录权限..."
chmod -R 755 /app/logs
chmod -R 755 /app/sessions
chmod -R 755 /app/instance

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
echo
echo -e "\033[36m============================================\033[0m"
echo -e "\033[36m              使用说明\033[0m"
echo -e "\033[36m============================================\033[0m"
echo -e "1. 应用已启动，您可以通过浏览器访问 \033[32mhttp://localhost:5000\033[0m"
echo -e "2. 如需退出交互模式，请按 \033[32mCtrl+P\033[0m 然后按 \033[32mCtrl+Q\033[0m"
echo -e "3. 如需重新进入交互模式，请使用命令：\033[32mdocker attach telerelay\033[0m"
echo -e "\033[36m============================================\033[0m"
echo

# 创建配置文件
cat > /app/config.yaml << EOF
telegram:
  api_id: $TG_API_ID
  api_hash: $TG_API_HASH
  phone: "$TG_PHONE"
  session_name: ""

server:
  port: 5000

flask:
  database_uri: sqlite:///instance/telegram_forwarder.db
  secret_key: dev_key
EOF

# 运行应用
exec python app.py