# TeleRelay（电报中继）

基于Python的Telegram频道转发工具，使用普通用户账号（非机器人）来监听指定频道并将消息转发到其他频道。

[English Version](#english-version)

## 主要功能

- **高效转发**: 自动监听指定频道并转发消息
- **Web界面管理**: 可视化配置转发规则与频道
- **频道搜索**: 快速从大量频道中筛选特定频道
- **实时错误监控**: 
  - 转发失败实时通知
  - 错误日志专用页面
  - 浏览器桌面通知
  - 导航栏错误计数提醒
- **北京时间显示**: 所有时间戳自动转换为北京时间
- **完善的日志系统**: 便于故障排查与监控

## 安装与配置

### 基本安装

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 配置YAML文件  
   编辑项目根目录下的`config.yaml`文件:
   ```yaml
   telegram:
     api_id: 你的API_ID
     api_hash: 你的API_HASH
     phone: 你的电话号码（如+8613800138000）
   
   server:
     port: 5000  # Web服务端口
   ```

3. 运行应用
   ```bash
   python app.py
   ```

### Docker部署

1. 构建并启动
   ```bash
   docker-compose up -d
   ```

2. 查看日志
   ```bash
   docker-compose logs -f
   ```

## 功能使用指南

### 基本操作流程

1. **首次登录**: 验证您的Telegram账号
2. **管理频道**: 
   - 进入"频道管理"页面
   - 使用"同步所有对话"获取频道列表
   - 使用搜索功能快速找到特定频道
   - 设置频道为"监听源"或"转发目标"
3. **创建转发规则**: 在"转发规则"页面创建规则
4. **启动服务**: 点击"启动服务"开始自动转发
5. **监控错误**: 通过错误日志页面查看转发问题

### 错误通知系统

- **实时通知**: 转发失败时页面顶部显示通知
- **错误日志页面**: 集中查看所有历史错误
- **桌面通知**: 页面不可见时发送浏览器通知
- **错误计数**: 导航栏显示未读错误数量

## 常见问题

1. **获取API_ID和API_HASH**:
   - 访问 https://my.telegram.org/
   - 登录后前往"API development tools"
   - 创建一个新应用获取凭证

2. **无法连接Telegram**:
   - 检查API_ID和API_HASH是否正确
   - 确认网络连接正常
   - 查看logs/error.log了解详细错误信息

3. **转发失败原因**:
   - 未加入源频道或目标频道
   - 源频道禁止转发
   - 在目标频道缺少发送权限
   - 详细原因会显示在错误日志中

4. **频道ID格式问题**:
   - 频道ID通常为`-100xxxxxxxxx`
   - 也可以使用`@username`格式

## 许可证

本项目采用MIT许可证。

版权所有 (c) 2023-2025 烟雨 (www.yanyuwangluo.cn)

---

# English Version

# TeleRelay

A Python-based Telegram channel forwarding tool that uses a regular user account (not a bot) to monitor specified channels and forward messages to other channels.

## Key Features

- **Efficient Forwarding**: Automatically monitor and forward messages from specified channels
- **Web Interface**: Visual configuration of forwarding rules and channels
- **Channel Search**: Quickly filter specific channels from a large number of channels
- **Real-time Error Monitoring**: 
  - Instant notifications for forwarding failures
  - Dedicated error log page
  - Browser desktop notifications
  - Error count alerts in navigation bar
- **Beijing Time Display**: All timestamps automatically converted to Beijing time
- **Comprehensive Logging System**: For easy troubleshooting and monitoring

## Installation and Configuration

### Basic Installation

1. Install dependencies
   ```bash
   pip install -r requirements.txt
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