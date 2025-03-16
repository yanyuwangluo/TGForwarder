# TeleRelay（电报中继）

这是一个基于Python的Telegram频道转发工具，使用普通用户账号（非机器人）来监听指定频道并将消息转发到其他频道。

[English README](README_EN.md)

## 主要功能

- 监听多个Telegram频道
- 将消息转发到多个目标频道
- 通过Web界面进行管理
- 查看转发历史和统计数据
- 显示当天转发的消息数量
- 缓存对话列表到本地数据库
- 日志系统，支持文件轮转
- 自定义端口运行
- Docker支持，方便部署
- GitHub Actions自动构建

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`文件为`.env`，并填写以下信息：

```
# Telegram API配置
API_ID=你的API_ID
API_HASH=你的API_HASH
PHONE=你的电话号码（包含国家代码，如+8613800138000）

# Flask配置 
SECRET_KEY=你的秘钥
DATABASE_URI=sqlite:///telegram_forwarder.db

# 可选配置
PORT=5000  # Web服务端口，默认5000
```

关于API_ID和API_HASH：
1. 访问 https://my.telegram.org/ 并登录
2. 前往 "API development tools"
3. 创建一个新应用程序，获取API_ID和API_HASH

### 3. 运行应用

标准启动：
```bash
python app.py
```

指定端口启动：
```bash
# 方法1：通过命令行参数
python app.py 8080

# 方法2：通过环境变量
PORT=8080 python app.py
```

应用将在指定端口上启动，默认为 http://127.0.0.1:5000。使用自定义端口时，访问地址相应变更。

## Docker部署

项目支持Docker部署，提供更简单的安装和管理方式。

### 准备工作

1. 安装Docker和Docker Compose
2. 配置`.env`文件（与上述配置相同）
3. 可选：添加Telegram自动登录配置

### Telegram自动登录配置

在`.env`文件中添加以下配置可实现无需交互自动登录：

```
# Telegram登录配置
TG_2FA_PASSWORD=your_2fa_password  # 如果启用了二次验证，填写密码
TG_ALWAYS_CONFIRM=true  # 自动确认服务条款
```

当收到Telegram验证码时，有两种方式处理：

1. **临时方式**：启动容器后，查看日志获取验证码提示，然后将容器停止，并通过环境变量传入验证码重新启动：
   ```bash
   TG_LOGIN_CODE=12345 docker-compose up -d
   ```

2. **持久方式**：将验证码提前写入`.env`文件：
   ```
   TG_LOGIN_CODE=12345  # Telegram发送的验证码
   ```

> 注意：一旦登录成功，会话信息会保存在`sessions`目录，后续启动无需再次登录。

### 使用Docker启动

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 直接使用Docker Hub镜像

您可以直接使用我们预构建的Docker镜像：

```bash
# 下载并启动（请替换username为实际用户名）
docker run -d --name telerelay \
  -p 5000:5000 \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  -v ./.env:/app/.env \
  -v ./sessions:/app/sessions \
  --restart unless-stopped \
  username/telerelay:latest
```

### Docker配置说明

Docker部署会自动映射以下内容：
- 端口：默认5000端口（可通过.env中的PORT修改）
- 日志目录：`./logs` → `/app/logs`
- 数据库：`./data` → `/app/data`
- 配置文件：`./.env` → `/app/.env`
- Telegram会话：`./sessions` → `/app/sessions`

可以通过修改`docker-compose.yml`自定义这些映射。

## GitHub Actions自动构建

本项目使用GitHub Actions自动构建并发布Docker镜像到Docker Hub。

### 自动化流程

1. 当代码推送到main分支时，自动触发构建
2. 当创建版本标签(如v1.0.0)时，自动构建带版本号的镜像
3. 自动推送到Docker Hub
4. 同时构建支持ARM64和AMD64架构的镜像

### 多架构支持

TeleRelay的Docker镜像支持以下CPU架构：
- `linux/amd64`: 适用于标准PC、服务器、大多数云环境
- `linux/arm64`: 适用于树莓派4、Apple M1/M2系列、AWS Graviton等ARM设备

无需特殊配置，Docker会自动拉取匹配您设备架构的镜像。

### 如何使用

要在自己的GitHub仓库中启用自动构建，需要设置以下Secrets：

1. `DOCKERHUB_USERNAME`: Docker Hub用户名
2. `DOCKERHUB_TOKEN`: Docker Hub访问令牌（不是密码）

如何设置：
1. 在GitHub仓库页面，点击"Settings"
2. 点击"Secrets and variables" → "Actions"
3. 点击"New repository secret"添加上述两个密钥

## 使用指南

1. 首次运行时，会要求验证Telegram账号，请按照提示操作。
2. 在Web界面中，前往"频道管理"页面添加要监听和转发的频道。
3. 点击"启动服务"开始监听和转发。
4. 在频道管理页面使用"同步所有对话"按钮可以获取全部频道和群组。

## 日志系统

系统具有完善的日志记录功能，所有日志存储在`logs`目录下：
- `telegram_forwarder.log`: 常规运行日志（INFO级别及以上）
- `error.log`: 仅错误日志（ERROR级别）

日志特性：
- 自动轮转：单个日志文件最大5MB
- 保留历史：保留最近10个日志文件
- 分级记录：详细的调试信息仅在控制台显示

## 注意事项

- 使用普通用户账号进行大量自动转发可能违反Telegram服务条款，请谨慎使用。
- 频道ID格式通常为`-100xxxxxxxxx`，也可以使用`@username`格式。
- 请确保账号已加入源频道和目标频道，且有足够的权限。
- 使用Docker部署时，首次启动需要验证Telegram账号，请查看日志进行操作。

## 常见问题

1. 如何获取频道ID？
   - 在频道管理页面使用"同步所有对话"功能自动获取
   - 或者转发频道中的消息到 @username_to_id_bot
   - 或者在网页版Telegram中，频道链接中的数字部分就是ID

2. 程序无法连接Telegram？
   - 请检查API_ID和API_HASH是否正确
   - 确认网络连接是否正常
   - 查看logs/error.log文件了解详细错误信息

3. 无法转发消息？
   - 确保账号已加入源频道和目标频道
   - 检查是否有转发权限
   - 查看应用日志了解详细错误信息
   
4. 如何获取全部频道和群组？
   - 在频道管理页面点击"同步所有对话"按钮
   - 同步过程可能需要一些时间，请耐心等待
   - 同步后的数据会缓存到本地数据库，速度更快

5. Docker部署时如何验证Telegram账号？
   - 首次启动时查看容器日志：`docker-compose logs -f`
   - 按照日志中的提示输入验证码
   - 可以使用`docker-compose exec telerelay bash`进入容器内部进行操作

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

Copyright (c) 2023-2025 烟雨 (www.yanyuwangluo.cn) 