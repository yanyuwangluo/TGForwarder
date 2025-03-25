"""
作者: 烟雨
网址: www.yanyuwangluo.cn
时间: 2025/3/16
转载请备注出处
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Channel(db.Model):
    """监听的频道和转发目标频道"""
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(100), nullable=False)  # 频道ID或用户名
    channel_title = db.Column(db.String(200))  # 频道标题
    is_source = db.Column(db.Boolean, default=False)  # 是否为监听源
    is_destination = db.Column(db.Boolean, default=False)  # 是否为转发目标
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Channel {self.channel_title}>'

class ForwardRule(db.Model):
    """转发规则：定义从哪个源频道转发到哪个目标频道"""
    id = db.Column(db.Integer, primary_key=True)
    source_channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)  # 源频道ID
    destination_channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)  # 目标频道ID
    is_active = db.Column(db.Boolean, default=True)  # 规则是否激活
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联到Channel表
    source_channel = db.relationship('Channel', foreign_keys=[source_channel_id], backref='source_rules')
    destination_channel = db.relationship('Channel', foreign_keys=[destination_channel_id], backref='destination_rules')
    
    def __repr__(self):
        return f'<ForwardRule {self.source_channel.channel_title} -> {self.destination_channel.channel_title}>'

class ForwardedMessage(db.Model):
    """已转发的消息记录"""
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer)  # 原始消息ID
    source_channel_id = db.Column(db.String(100))  # 来源频道ID
    destination_channel_id = db.Column(db.String(100))  # 目标频道ID
    message_title = db.Column(db.String(500))  # 消息标题或前100个字符
    forwarded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ForwardedMessage {self.id}>'

class Dialog(db.Model):
    """缓存的所有频道和群组对话"""
    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.String(100), nullable=False, unique=True)  # 对话ID
    title = db.Column(db.String(200), nullable=False)  # 对话标题
    dialog_type = db.Column(db.String(50), nullable=False)  # 类型：频道、超级群组、群组
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Dialog {self.title} ({self.dialog_type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dialog_id': self.dialog_id,
            'title': self.title,
            'type': self.dialog_type,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 