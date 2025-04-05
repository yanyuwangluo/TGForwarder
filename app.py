"""
TeleRelay - Telegram Channel Message Relay Tool

作者: 烟雨
网址: www.yanyuwangluo.cn
时间: 2023/3/16
转载请备注出处
"""


import os
import threading
import asyncio
import time
import logging
import traceback
import yaml
import sys
from app import create_app
from app.telegram_client import get_telegram_client, init_telegram_client

# 加载配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 保存配置文件
def save_config(config):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# 检查并获取必要的Telegram配置
def check_telegram_config():
    config = load_config()
    telegram_config = config.get('telegram', {})
    
    # 检查API ID
    api_id = telegram_config.get('api_id')
    if not api_id:
        print("请输入Telegram API ID:")
        api_id = input().strip()
        try:
            # 确保API ID是整数
            api_id = int(api_id)
            telegram_config['api_id'] = api_id
        except ValueError:
            print("错误: API ID必须是一个整数!")
            return check_telegram_config()  # 递归调用，重新获取
    elif isinstance(api_id, str) and api_id.strip().isdigit():
        # 如果是字符串形式的数字，转换为整数
        api_id = int(api_id)
        telegram_config['api_id'] = api_id
    
    # 检查API Hash
    api_hash = telegram_config.get('api_hash')
    if not api_hash:
        print("请输入Telegram API Hash:")
        api_hash = input().strip()
        telegram_config['api_hash'] = api_hash
    
    # 检查手机号
    phone = telegram_config.get('phone')
    if not phone:
        print("请输入Telegram账号手机号 (格式: +86123456789):")
        phone = input().strip()
        
    # 确保手机号不为空并格式正确
    if not phone or not isinstance(phone, str):
        print("错误: 电话号码不能为空!")
        return check_telegram_config()
    
    # 去除手机号中可能包含的引号
    phone = phone.strip("'\"")
    
    # 确保手机号格式正确
    if not phone.startswith('+'):
        print("提醒: 电话号码应该以'+'开头，已自动添加")
        phone = '+' + phone
    
    # 检查手机号是否包含有效数字
    import re
    if not re.match(r'\+\d{6,15}$', phone):
        print(f"警告: 电话号码 '{phone}' 格式可能不正确，请确保格式为 '+国家代码电话号码'")
        confirm = input("是否继续使用此电话号码? (y/n): ").strip().lower()
        if confirm != 'y':
            return check_telegram_config()
    
    telegram_config['phone'] = phone
    
    # 如果有任何配置被更新，保存配置文件
    config['telegram'] = telegram_config
    save_config(config)
    
    return api_id, api_hash, phone

# 配置日志
def setup_logging():
    # 创建日志格式
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # 文件处理器 - 常规日志（带轮转）
    os.makedirs('logs', exist_ok=True)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        'logs/telegram_forwarder.log', 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # 文件处理器 - 错误日志（带轮转）
    error_handler = RotatingFileHandler(
        'logs/error.log', 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # 默认级别为INFO
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # 应用程序日志设置
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.DEBUG)  # 应用代码始终保持DEBUG级别
    
    # 设置Telethon日志级别为WARNING，减少过多的网络日志
    telethon_logger = logging.getLogger('telethon')
    telethon_logger.setLevel(logging.WARNING)
    
    # 特别为telethon.client.updates设置INFO级别，保留重要的更新日志
    updates_logger = logging.getLogger('telethon.client.updates')
    updates_logger.setLevel(logging.INFO)
    
    # SQLAlchemy日志设置为WARNING
    sqlalchemy_logger = logging.getLogger('sqlalchemy')
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # Werkzeug日志设置为WARNING，除非需要调试HTTP请求
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    # 使用根日志记录器输出初始化完成信息
    root_logger.info("日志系统初始化完成")

# 设置日志
setup_logging()

# 获取应用日志记录器
logger = logging.getLogger(__name__)

app = create_app()

# 全局变量存储Telegram客户端循环
telegram_loop = None
telegram_thread = None
should_exit = False
# 防止在每次请求结束时停止客户端
client_started = False

def start_telegram_client():
    """在后台线程中启动Telegram客户端"""
    global telegram_loop, should_exit
    
    logger.debug("开始初始化Telegram客户端线程")
    
    # 创建新的事件循环
    telegram_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(telegram_loop)
    
    # 输出清晰的提示，表明正在等待用户输入
    print("\n============================================")
    print("Telegram客户端配置初始化")
    print("============================================")
    
    # 检查并获取Telegram配置
    api_id, api_hash, phone = check_telegram_config()
    
    # 输出清晰的提示，表明配置已完成，正在连接
    print("\n============================================")
    print("配置已完成，正在连接Telegram服务器...")
    print("============================================\n")
    
    logger.debug(f"使用API ID: {api_id}, 手机号: {phone}")
    
    # 传入Flask应用实例
    tg_client = init_telegram_client(api_id, api_hash, phone, app)
    
    # 启动客户端
    try:
        logger.debug("开始启动Telegram客户端")
        telegram_loop.run_until_complete(tg_client.start())
        logger.debug("Telegram客户端启动完成")
        print("Telegram客户端已启动")
        
        # 设置保持连接的回调
        async def keep_alive():
            logger.debug("开始保持客户端连接")
            while not should_exit:
                if not tg_client.is_running:
                    logger.debug("检测到客户端已停止，尝试重新连接")
                    try:
                        await tg_client.reconnect()
                    except Exception as e:
                        logger.error(f"重新连接失败: {e}")
                await asyncio.sleep(30)  # 每30秒检查一次
                
        # 添加保持连接的任务        
        keep_alive_task = telegram_loop.create_task(keep_alive())
        
        # 保持循环运行
        logger.debug("开始运行事件循环")
        telegram_loop.run_forever()
    except Exception as e:
        logger.error(f"Telegram客户端循环异常: {e}")
    finally:
        # 正确关闭循环
        should_exit = True
        logger.debug("开始关闭事件循环")
        
        try:
            # 取消所有未完成的任务
            pending = asyncio.all_tasks(telegram_loop)
            for task in pending:
                task.cancel()
                
            # 运行直到所有任务完成或取消
            telegram_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            telegram_loop.close()
        except Exception as e:
            logger.error(f"关闭事件循环时出错: {e}")
            
        logger.debug("Telegram客户端循环已关闭")
        print("Telegram客户端循环已关闭")

def init_app():
    """初始化应用"""
    global telegram_thread, should_exit, client_started
    
    # 如果客户端已经启动，不要重复启动
    if client_started:
        logger.debug("客户端已经启动，跳过初始化")
        return
    
    # 重置退出标志
    should_exit = False
    
    logger.debug("初始化应用，启动Telegram客户端线程")
    
    # 先检查配置是否已设置，如果未设置，提示用户先设置配置
    config = load_config()
    telegram_config = config.get('telegram', {})
    if not telegram_config.get('api_id') or not telegram_config.get('api_hash') or not telegram_config.get('phone'):
        logger.info("Telegram配置未完全设置，将在后台线程中提示用户输入")
        print("请注意: 需要输入Telegram API配置才能继续")
    
    # 启动Telegram客户端线程
    telegram_thread = threading.Thread(target=start_telegram_client)
    telegram_thread.daemon = True  # 设为守护线程
    telegram_thread.start()
    
    # 设置客户端已启动标志，避免重复启动
    client_started = True
    logger.debug("Telegram客户端线程已启动")
    
    # 等待配置输入完成和客户端初始化
    # 这里不立即尝试同步对话，等待客户端真正准备好后再进行
    logger.debug("等待Telegram客户端初始化...")
    max_wait_time = 120  # 最多等待2分钟
    wait_interval = 5  # 每5秒检查一次
    waited_time = 0
    
    while waited_time < max_wait_time:
        # 检查客户端是否准备好
        if telegram_loop and get_telegram_client() and get_telegram_client().is_running:
            logger.debug("Telegram客户端已准备好")
            
            # 同步对话列表
            try:
                logger.debug("开始同步对话列表到本地数据库")
                tg_client = get_telegram_client()
                future = asyncio.run_coroutine_threadsafe(
                    tg_client.get_dialogs(use_cache=True, force_update=False), 
                    telegram_loop
                )
                # 增加超时时间
                dialogs_result = future.result(timeout=60)
                results = dialogs_result.get('results', [])
                logger.info(f"初始化时同步对话列表完成，获取到 {len(results)} 个对话")
                break
            except Exception as e:
                logger.error(f"同步对话列表失败: {e}")
                logger.error(traceback.format_exc())
                break
        else:
            # 客户端尚未准备好，等待一段时间
            time.sleep(wait_interval)
            waited_time += wait_interval
            
            # 只有在后台提示，避免干扰用户输入
            logger.debug(f"等待客户端准备就绪...已等待{waited_time}秒")
    
    if waited_time >= max_wait_time:
        logger.warning(f"等待客户端准备就绪超时(>{max_wait_time}秒)，可能需要手动重启应用")

@app.teardown_appcontext
def shutdown_client(exception=None):
    """关闭应用时停止Telegram客户端"""
    global telegram_loop, should_exit, client_started
    
    # 只在应用真正关闭时停止客户端，而不是每次请求结束时
    if exception is not None:
        logger.debug(f"应用上下文结束，但有异常: {exception}，不停止客户端")
        return
    
    # 检查是否是Flask开发服务器的请求上下文结束
    # 这种情况下不应该停止客户端
    if not should_exit:
        return
    
    logger.debug("应用上下文结束，准备停止Telegram客户端")
    
    # 设置退出标志
    should_exit = True
    client_started = False
    
    tg_client = get_telegram_client()
    if tg_client and tg_client.is_running and telegram_loop:
        try:
            # 在正确的循环中停止客户端
            logger.debug("发送停止客户端请求")
            future = asyncio.run_coroutine_threadsafe(tg_client.stop(), telegram_loop)
            future.result(timeout=5)  # 等待最多5秒
            logger.debug("客户端停止请求完成")
        except Exception as e:
            logger.error(f"停止Telegram客户端时发生错误: {e}")

if __name__ == '__main__':
    # 获取端口号，优先从命令行参数获取，其次从配置文件获取，最后使用默认值5000
    import sys
    
    # 默认端口
    port = 5000
    
    # 从配置文件获取
    try:
        config = load_config()
        if 'server' in config and 'port' in config['server']:
            port = config['server']['port']
            logger.info(f"使用配置文件指定的端口: {port}")
    except Exception as e:
        logger.warning(f"从配置文件获取端口失败: {e}，使用默认端口: {port}")
    
    # 从命令行参数获取（优先级更高）
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            logger.info(f"使用命令行参数指定的端口: {port}")
        except ValueError:
            logger.warning(f"命令行参数端口值无效: {sys.argv[1]}，使用默认端口: {port}")
    
    # 手动调用初始化
    logger.debug("启动应用")
    with app.app_context():
        init_app()
    logger.info(f"启动Web服务器，监听端口: {port}")
    app.run(debug=True, use_reloader=False, threaded=True, port=port, host='0.0.0.0')  # 禁用重新加载器以避免多次启动客户端