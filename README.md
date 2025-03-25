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

1. 启动
##### 手机号必须包含国家代码和按照这个形式不能有空格，如+8613800138000
   ```bash
   mkdir telegram_forwarder
   cd telegram_forwarder
   touch config.yaml
   docker run -it --name telerelay \
   -p 5000:5000 \
   -v $(pwd)/logs:/app/logs \
   -v $(pwd)/sessions:/app/sessions \
   -v $(pwd)/config.yaml:/app/config.yaml \
   yanyuwangluo/telerelay:latest
   ```

2. 查看日志
   ```bash
   docker logs telerelay -f
   ```

## 功能使用指南

### 基本操作流程

**首次登录**: 验证您的Telegram账号
**管理频道**: 
 - 进入"频道管理"页面
 - 使用"同步所有对话"获取频道列表
 - 使用搜索功能快速找到特定频道
 - 设置频道为"监听源"或"转发目标"
**创建转发规则**: 在"转发规则"页面创建规则
**启动服务**: 点击"启动服务"开始自动转发
**监控错误**: 通过错误日志页面查看转发问题
**实时通知**: 转发失败时页面顶部显示通知
**错误日志页面**: 集中查看所有历史错误
**桌面通知**: 页面不可见时发送浏览器通知
**错误计数**: 导航栏显示未读错误数量

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

2. Configure YAML file  
   Edit the `config.yaml` file in the project root directory:
   ```yaml
   telegram:
     api_id: your_API_ID
     api_hash: your_API_HASH
     phone: your_phone_number (e.g., +12025550123)
   
   server:
     port: 5000  # Web service port
   ```

3. Run the application
   ```bash
   python app.py
   ```

### Docker Deployment

1. start
   ```bash
   mkdir telegram_forwarder
   cd telegram_forwarder
   touch config.yaml
   docker run -it --name telerelay \
   -p 5000:5000 \
   -v $(pwd)/logs:/app/logs \
   -v $(pwd)/sessions:/app/sessions \
   -v $(pwd)/config.yaml:/app/config.yaml \
   yanyuwangluo/telerelay:latest
   ```

2. View logs
   ```bash
   docker logs telerelay -f
   ```

## Feature Usage Guide

### Basic Operation Flow

1. **First Login**: Verify your Telegram account
2. **Manage Channels**: 
   - Go to the "Channel Management" page
   - Use "Sync All Dialogs" to get your channel list
   - Use the search function to quickly find specific channels
   - Set channels as "Monitoring Source" or "Forwarding Target"
3. **Create Forwarding Rules**: Create rules on the "Forwarding Rules" page
4. **Start Service**: Click "Start Service" to begin automatic forwarding
5. **Monitor Errors**: Check forwarding issues through the error log page

### Error Notification System

- **Real-time Notifications**: Display at page top when forwarding fails
- **Error Log Page**: Centralized view of all historical errors
- **Desktop Notifications**: Browser notifications when page is not visible
- **Error Count**: Navigation bar displays unread error count

## Common Issues

1. **Getting API_ID and API_HASH**:
   - Visit https://my.telegram.org/
   - Log in and go to "API development tools"
   - Create a new application to get credentials

2. **Cannot Connect to Telegram**:
   - Check if API_ID and API_HASH are correct
   - Confirm network connection is normal
   - Check logs/error.log for detailed error information

3. **Forwarding Failure Reasons**:
   - Not joined source or target channel
   - Source channel prohibits forwarding
   - Lack of sending permissions in target channel
   - Detailed reasons will be shown in the error log

4. **Channel ID Format Issues**:
   - Channel ID is typically `-100xxxxxxxxx`
   - Can also use `@username` format

## License

This project is licensed under the MIT License.

Copyright (c) 2023-2025 YanYu (www.yanyuwangluo.cn)