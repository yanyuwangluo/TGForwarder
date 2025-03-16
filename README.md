# TGForwarder（TG转发器）

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
## 图片实例
![image](https://github.com/yanyuwangluo/TGForwarder/blob/main/img/1.png)
![image](https://github.com/yanyuwangluo/TGForwarder/blob/main/img/2.png)
![image](https://github.com/yanyuwangluo/TGForwarder/blob/main/img/3.png)
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

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

Copyright (c) 2023-2025 烟雨 (www.yanyuwangluo.cn) 