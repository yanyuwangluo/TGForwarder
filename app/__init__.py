"""
作者: 烟雨
网址: www.yanyuwangluo.cn
时间: 2025/3/16
转载请备注出处
"""
import os
import asyncio
import logging
import yaml
from flask import Flask
# 从dotenv import load_dotenv
from app.models import db
from app.telegram_client import init_telegram_client

# 获取应用日志记录器
logger = logging.getLogger('app')

# 加载配置文件
def load_config():
    # 修改为从项目根目录加载配置文件
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# load_dotenv()

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    config = load_config()
    
    # 配置
    app.config['SECRET_KEY'] = config['flask']['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['flask']['database_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # 在应用上下文中创建数据库表
    with app.app_context():
        db.create_all()
        
        # 注意：这里不要初始化Telegram客户端
        # 实际的客户端初始化会在app.py中的start_telegram_client函数中执行
    
    return app 