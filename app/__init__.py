"""
作者: 烟雨
网址: www.yanyuwangluo.cn
时间: 2025/3/16
转载请备注出处
"""
import os
import asyncio
import logging
from flask import Flask
from dotenv import load_dotenv
from app.models import db
from app.telegram_client import init_telegram_client

# 获取应用日志记录器
logger = logging.getLogger('app')

# 加载环境变量
load_dotenv()

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///telegram_forwarder.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化Telegram客户端
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    phone = os.getenv('PHONE')
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # 在应用上下文中创建数据库表
    with app.app_context():
        db.create_all()
        
        # 注意：这里不要初始化Telegram客户端
        # 实际的客户端初始化会在app.py中的start_telegram_client函数中执行
    
    return app 