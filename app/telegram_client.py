"""
作者: 烟雨
网址: www.yanyuwangluo.cn
时间: 2025/3/16
转载请备注出处
"""

import os
import asyncio
import logging
import traceback
import yaml
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, Channel as TelegramChannel
from app.models import db, Channel, ForwardedMessage, Dialog, ForwardRule
from flask import current_app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 加载配置文件
def load_config():
    # 修改为从项目根目录加载配置文件
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone):
        self.client = None
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.is_running = False
        self.loop = None
        self._handlers_registered = False
        self.app = None  # 存储Flask应用实例
        self.config = load_config()['telegram']
        
    async def start(self):
        """启动Telegram客户端"""
        try:
            logger.debug("准备启动Telegram客户端")
            
            # 获取会话名称
            session_name = self.config.get('session_name', '')
            if not session_name:
                session_name = str(self.phone)
            # 清理会话名称中的特殊字符
            session_name = ''.join(c for c in session_name if c.isalnum() or c in '_-')
            
            session_path = f"sessions/{session_name}"
            logger.debug(f"使用会话路径: {session_path}")
            
            # 创建会话目录
            os.makedirs("sessions", exist_ok=True)
            
            # 初始化客户端
            self.client = TelegramClient(session_path, self.api_id, self.api_hash)
            
            # 启动客户端，不设置自定义登录处理，使用默认的交互式处理
            try:
                logger.debug("开始连接Telegram服务器")
                # 使用默认的交互式处理方式，将直接提示用户在控制台输入验证码和二次验证密码
                await self.client.start(phone=self.phone)
                
                if not self.client.is_connected():
                    logger.error("客户端连接失败")
                    return False
                    
                self.is_running = True
                logger.info("成功连接Telegram服务器")
                
                # 注册消息处理器
                if not self._handlers_registered:
                    logger.debug("注册消息处理器")
                    self.client.add_event_handler(self.message_handler, events.NewMessage)
                    # 添加编辑消息处理器
                    self.client.add_event_handler(self.edited_message_handler, events.MessageEdited)
                    self._handlers_registered = True
                
                # 获取客户端信息
                try:
                    me = await self.client.get_me()
                    logger.info(f"登录账号: {me.first_name} {getattr(me, 'last_name', '')} (@{me.username})")
                except Exception as e:
                    logger.error(f"获取账号信息失败: {e}")
                    # 但不影响客户端使用
                
                return True
            except Exception as e:
                logger.error(f"启动客户端时出错: {e}")
                logger.error(traceback.format_exc())
                self.is_running = False
                return False
                
        except Exception as e:
            logger.error(f"初始化客户端时出错: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
            return False
    
    async def reconnect(self):
        """重新连接Telegram客户端"""
        logger.debug("尝试重新连接Telegram客户端")
        try:
            if self.client:
                # 检查连接状态
                if not self.client.is_connected():
                    logger.debug("客户端未连接，尝试重新连接")
                    await self.client.connect()
                    
                # 检查授权状态
                if not await self.client.is_user_authorized():
                    logger.warning("客户端未授权，需要重新登录")
                    return await self.start()
                
                # 重新注册消息处理器
                if not self._handlers_registered:
                    logger.debug("重新注册消息处理器")
                    self.client.add_event_handler(
                        self.message_handler,
                        events.NewMessage()
                    )
                    # 添加编辑消息处理器
                    self.client.add_event_handler(
                        self.edited_message_handler,
                        events.MessageEdited()
                    )
                    self._handlers_registered = True
                
                self.is_running = True
                logger.info("Telegram客户端已重新连接")
                return True
            else:
                logger.warning("客户端实例不存在，需要重新初始化")
                return await self.start()
        except Exception as e:
            logger.error(f"重新连接Telegram客户端失败: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
            return False
    
    async def stop(self):
        """停止Telegram客户端"""
        logger.debug("开始停止Telegram客户端")
        try:
            if self.client:
                # 移除所有处理器
                if self._handlers_registered:
                    logger.debug("移除消息处理器")
                    self.client.remove_event_handler(self.message_handler)
                    self.client.remove_event_handler(self.edited_message_handler)
                    self._handlers_registered = False
                
                # 断开连接
                logger.debug("断开客户端连接")
                await self.client.disconnect()
                self.is_running = False
                logger.info("Telegram客户端已停止")
        except Exception as e:
            logger.error(f"停止Telegram客户端时发生错误: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
    
    async def get_entity_info(self, channel_id):
        """获取频道信息"""
        logger.debug(f"开始获取频道信息: {channel_id}")
        try:
            # 确保客户端已连接
            if not self.client.is_connected():
                logger.warning("客户端未连接，尝试重新连接")
                await self.client.connect()
            
            # 处理数字ID (确保正确格式)
            if channel_id.startswith('-100') and channel_id[4:].isdigit():
                # 已经是正确格式的数字ID
                entity_id = int(channel_id[4:])
                logger.debug(f"使用已格式化的ID: -100{entity_id}")
            elif channel_id.startswith('-') and channel_id[1:].isdigit():
                # 旧格式的负数ID，转换为新格式
                entity_id = int(channel_id[1:])
                channel_id = f"-100{entity_id}"
                logger.debug(f"转换旧格式ID到: {channel_id}")
            elif channel_id.isdigit():
                # 纯数字ID，添加-100前缀
                entity_id = int(channel_id)
                channel_id = f"-100{entity_id}"
                logger.debug(f"添加前缀到纯数字ID: {channel_id}")
            else:
                # 用户名格式，直接使用
                entity_id = channel_id
                logger.debug(f"使用用户名格式: {entity_id}")
            
            # 获取实体信息
            logger.debug(f"开始请求实体信息: {entity_id}")
            entity = await self.client.get_entity(entity_id)
            logger.debug(f"获取实体成功: {entity}")
            
            if isinstance(entity, TelegramChannel):
                logger.debug(f"实体是频道: {entity.title}")
                return {
                    'id': channel_id,
                    'title': entity.title,
                    'success': True
                }
            
            logger.debug(f"实体不是频道，尝试提取标题")
            return {
                'id': channel_id,
                'title': getattr(entity, 'title', channel_id),
                'success': True
            }
        except Exception as e:
            logger.error(f"获取频道信息失败: {e}")
            logger.error(traceback.format_exc())
            return {
                'id': channel_id,
                'title': None,
                'success': False,
                'error': str(e)
            }
    
    async def get_dialogs(self, use_cache=True, force_update=False):
        """获取用户已加入的对话列表(包括频道、群组)
        
        参数:
            use_cache: 是否使用本地缓存
            force_update: 是否强制更新缓存
        """
        logger.debug("开始获取用户的对话列表")
        
        if self.app and use_cache and not force_update:
            # 尝试从数据库缓存获取
            with self.app.app_context():
                cached_dialogs = Dialog.query.all()
                if cached_dialogs:
                    logger.debug(f"从缓存获取到 {len(cached_dialogs)} 个对话")
                    return {
                        'success': True,
                        'results': [dialog.to_dict() for dialog in cached_dialogs],
                        'from_cache': True
                    }
        
        try:
            # 确保客户端已连接
            if not self.client.is_connected():
                logger.warning("客户端未连接，尝试重新连接")
                await self.client.connect()
            
            # 一次性获取对话，不使用分页方式，避免offset_peer错误
            logger.debug("直接获取所有对话列表")
            all_dialogs = []
            
            try:
                # 获取对话列表，限制较大数量但不使用分页
                dialogs = await self.client.get_dialogs(limit=500)
                logger.debug(f"获取到 {len(dialogs)} 个对话")
                
                # 处理对话
                for dialog in dialogs:
                    entity = dialog.entity
                    
                    # 确定实体类型和ID格式
                    entity_type = "未知"
                    entity_id = ""
                    
                    if hasattr(entity, 'megagroup') and entity.megagroup:
                        entity_type = "超级群组"
                        entity_id = f"-100{entity.id}"
                    elif hasattr(entity, 'gigagroup') and entity.gigagroup:
                        entity_type = "超级群组"
                        entity_id = f"-100{entity.id}"
                    elif hasattr(entity, 'broadcast') and entity.broadcast:
                        if hasattr(entity, 'megagroup') and not entity.megagroup:
                            entity_type = "频道"
                            entity_id = f"-100{entity.id}"
                    elif hasattr(entity, 'chat_id'):
                        entity_type = "群组"
                        entity_id = f"-{entity.chat_id}"
                    else:
                        # 跳过私聊等其他类型
                        continue
                    
                    # 添加到结果列表
                    dialog_info = {
                        'id': entity_id,
                        'title': getattr(entity, 'title', '未命名'),
                        'type': entity_type
                    }
                    all_dialogs.append(dialog_info)
            except Exception as e:
                logger.error(f"获取对话列表时出错: {e}")
                logger.error(traceback.format_exc())
                # 使用备用方法尝试获取对话
                logger.debug("尝试使用备用方法获取对话")
                try:
                    # 直接获取所有聊天实体，可能会比较慢但更可靠
                    dialogs = await self.client.get_dialogs(archived=False)
                    channels = [d for d in dialogs if hasattr(d.entity, 'broadcast') and 
                               not (hasattr(d.entity, 'megagroup') and d.entity.megagroup)]
                    groups = [d for d in dialogs if (hasattr(d.entity, 'megagroup') and d.entity.megagroup) or
                             hasattr(d.entity, 'chat_id')]
                    
                    # 处理频道
                    for dialog in channels:
                        entity = dialog.entity
                        entity_id = f"-100{entity.id}"
                        all_dialogs.append({
                            'id': entity_id,
                            'title': getattr(entity, 'title', '未命名'),
                            'type': "频道"
                        })
                    
                    # 处理群组
                    for dialog in groups:
                        entity = dialog.entity
                        if hasattr(entity, 'chat_id'):
                            entity_id = f"-{entity.chat_id}"
                            entity_type = "群组"
                        else:
                            entity_id = f"-100{entity.id}"
                            entity_type = "超级群组"
                        
                        all_dialogs.append({
                            'id': entity_id,
                            'title': getattr(entity, 'title', '未命名'),
                            'type': entity_type
                        })
                except Exception as e2:
                    logger.error(f"备用方法获取对话列表也失败: {e2}")
                    logger.error(traceback.format_exc())
            
            logger.debug(f"总共获取到 {len(all_dialogs)} 个频道和群组")
            
            # 将结果保存到数据库
            if self.app and (use_cache or force_update) and all_dialogs:
                with self.app.app_context():
                    # 清除旧数据（如果强制更新）
                    if force_update:
                        logger.debug("强制更新缓存，清除旧数据")
                        Dialog.query.delete()
                    
                    # 保存新数据
                    for dialog in all_dialogs:
                        # 检查是否已存在
                        existing = Dialog.query.filter_by(dialog_id=dialog['id']).first()
                        if existing:
                            # 更新现有记录
                            existing.title = dialog['title']
                            existing.dialog_type = dialog['type']
                            existing.updated_at = datetime.utcnow()
                        else:
                            # 创建新记录
                            new_dialog = Dialog(
                                dialog_id=dialog['id'],
                                title=dialog['title'],
                                dialog_type=dialog['type']
                            )
                            db.session.add(new_dialog)
                    
                    db.session.commit()
                    logger.debug(f"已将 {len(all_dialogs)} 个对话保存到数据库")
            
            return {
                'success': True,
                'results': all_dialogs,
                'from_cache': False
            }
        except Exception as e:
            logger.error(f"获取对话列表失败: {e}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
            
    async def sync_dialogs(self):
        """同步所有对话到本地数据库"""
        logger.debug("开始同步对话列表到本地数据库")
        result = await self.get_dialogs(use_cache=False, force_update=True)
        return result
    
    async def get_followed_channels(self):
        """获取用户已加入的频道列表（备用方法）"""
        logger.debug("使用备用方法获取频道列表")
        try:
            # 确保客户端已连接
            if not self.client.is_connected():
                logger.warning("客户端未连接，尝试重新连接")
                await self.client.connect()
                
            # 获取所有对话
            channels = []
            
            # 方法1：使用客户端API获取频道
            try:
                # 通过API直接获取，不使用分页
                from telethon.tl.functions.channels import GetChannelsRequest
                from telethon.tl.functions.messages import GetDialogsRequest
                from telethon.tl.types import InputPeerEmpty
                
                # 先获取所有对话的基本信息
                result = await self.client(GetDialogsRequest(
                    offset_date=None,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=100,
                    hash=0
                ))
                
                channel_entities = []
                for dialog in result.dialogs:
                    if hasattr(dialog.peer, 'channel_id'):
                        try:
                            channel_id = dialog.peer.channel_id
                            channel_entities.append(channel_id)
                        except:
                            pass
                
                if channel_entities:
                    # 批量获取频道详细信息
                    from telethon.tl.types import InputChannel
                    for i in range(0, len(channel_entities), 10):
                        batch = channel_entities[i:i+10]
                        try:
                            # 不应直接使用access_hash=0
                            input_channels = []
                            for channel_id in batch:
                                try:
                                    # 获取完整实体信息包含access_hash
                                    entity_id = f"-100{channel_id}"
                                    channel_entity = await self.client.get_entity(entity_id)
                                    if hasattr(channel_entity, 'access_hash'):
                                        input_channels.append(InputChannel(
                                            channel_id=channel_id,
                                            access_hash=channel_entity.access_hash
                                        ))
                                except Exception as e:
                                    logger.error(f"获取频道 {channel_id} 信息失败: {e}")
                                    
                            if input_channels:
                                channel_full = await self.client(GetChannelsRequest(input_channels))
                                
                                for channel in channel_full.chats:
                                    if hasattr(channel, 'broadcast') and channel.broadcast:
                                        entity_id = f"-100{channel.id}"
                                        channels.append({
                                            'id': entity_id,
                                            'title': getattr(channel, 'title', '未命名'),
                                            'type': "频道"
                                        })
                        except Exception as e:
                            logger.error(f"获取频道详情批次失败: {e}")
            except Exception as e:
                logger.error(f"方法1获取频道失败: {e}")
                logger.error(traceback.format_exc())
            
            # 方法2：使用get_dialogs的简化版本
            if not channels:
                try:
                    dialogs = await self.client.get_dialogs(limit=100)
                    for dialog in dialogs:
                        entity = dialog.entity
                        if hasattr(entity, 'broadcast') and entity.broadcast:
                            if not hasattr(entity, 'megagroup') or not entity.megagroup:
                                entity_id = f"-100{entity.id}"
                                channels.append({
                                    'id': entity_id,
                                    'title': getattr(entity, 'title', '未命名'),
                                    'type': "频道"
                                })
                except Exception as e:
                    logger.error(f"方法2获取频道失败: {e}")
                    logger.error(traceback.format_exc())
            
            logger.debug(f"使用备用方法获取到 {len(channels)} 个频道")
            
            # 将结果保存到数据库
            if self.app and channels:
                with self.app.app_context():
                    for channel_info in channels:
                        # 检查是否已存在
                        existing = Dialog.query.filter_by(dialog_id=channel_info['id']).first()
                        if not existing:
                            # 创建新记录
                            new_dialog = Dialog(
                                dialog_id=channel_info['id'],
                                title=channel_info['title'],
                                dialog_type=channel_info['type']
                            )
                            db.session.add(new_dialog)
                    
                    db.session.commit()
                    logger.debug(f"已将 {len(channels)} 个频道保存到数据库")
            
            return {
                'success': True,
                'results': channels,
                'from_cache': False
            }
        except Exception as e:
            logger.error(f"备用方法获取频道失败: {e}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    async def message_handler(self, event):
        """处理新消息并转发"""
        if not event.message:
            return
            
        # 获取消息来源
        try:
            logger.debug("收到新消息")
            chat = await event.get_chat()
            
            # 获取正确格式的频道ID
            if hasattr(chat, 'id'):
                # 对于超级群组和频道，ID格式为 -100{chat.id}
                if hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast'):
                    chat_id = f"-100{chat.id}"
                else:
                    chat_id = str(chat.id)
            else:
                chat_id = str(getattr(chat, 'id', 'unknown'))
            
            logger.debug(f"消息来源: {chat_id}")
            
            # 创建Flask应用上下文
            if self.app:
                with self.app.app_context():
                    # 检查是否是来自监听的源频道
                    source_channel = Channel.query.filter_by(
                        channel_id=chat_id, 
                        is_source=True
                    ).first()
                    
                    if not source_channel:
                        logger.debug(f"频道 {chat_id} 不是监听源，忽略消息")
                        return
                    
                    # 保存源频道名称和ID，避免后续会话分离问题
                    source_channel_title = source_channel.channel_title
                    source_channel_id = source_channel.id
                    logger.info(f"收到来自监听源的消息: {source_channel_title}")
                        
                    # 获取消息内容作为标题
                    message_text = event.message.message
                    message_title = message_text[:100] if message_text else "无文本内容"
                    logger.debug(f"消息内容: {message_title[:50]}{'...' if len(message_title) > 50 else ''}")
                    
                    # 查找适用于此源频道的活跃转发规则
                    forward_rules = []
                    try:
                        forward_rules = ForwardRule.query.filter_by(
                            source_channel_id=source_channel_id,
                            is_active=True
                        ).all()
                    except Exception as e:
                        logger.error(f"查询转发规则出错: {e}")
                        # 如果查询出错，尝试使用旧的转发方式
                    
                    if not forward_rules:
                        logger.debug(f"没有为源频道 {source_channel_title} 配置转发规则，尝试使用旧版转发逻辑")
                        # 兼容旧版，如果没有特定规则，尝试转发到所有目标
                        destinations = Channel.query.filter_by(is_destination=True).all()
                        for dest in destinations:
                            # 直接转发到此目标
                            await self._forward_message_to_channel(
                                event.message, 
                                chat_id,
                                source_channel_title, 
                                dest.channel_id, 
                                dest.channel_title,
                                message_title
                            )
                    else:
                        logger.debug(f"找到 {len(forward_rules)} 条适用的转发规则")
                        # 转发到每个规则指定的目标频道
                        for rule in forward_rules:
                            dest = rule.destination_channel
                            if dest:
                                await self._forward_message_to_channel(
                                    event.message, 
                                    chat_id,
                                    source_channel_title, 
                                    dest.channel_id, 
                                    dest.channel_title,
                                    message_title
                                )
                            else:
                                logger.error(f"规则 {rule.id} 的目标频道不存在")
            else:
                logger.error("未设置Flask应用实例，无法处理数据库操作")
        except Exception as e:
            logger.error(f"处理消息时发生错误: {str(e)}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
    
    async def edited_message_handler(self, event):
        """处理编辑过的消息并更新已转发的消息"""
        if not event.message:
            return
            
        # 获取消息来源
        try:
            logger.debug("收到编辑消息")
            chat = await event.get_chat()
            
            # 获取正确格式的频道ID
            if hasattr(chat, 'id'):
                # 对于超级群组和频道，ID格式为 -100{chat.id}
                if hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast'):
                    chat_id = f"-100{chat.id}"
                else:
                    chat_id = str(chat.id)
            else:
                chat_id = str(getattr(chat, 'id', 'unknown'))
            
            message_id = event.message.id
            logger.debug(f"编辑消息来源: {chat_id}, 消息ID: {message_id}")
            
            # 创建Flask应用上下文
            if self.app:
                with self.app.app_context():
                    # 检查是否是来自监听的源频道
                    source_channel = Channel.query.filter_by(
                        channel_id=chat_id, 
                        is_source=True
                    ).first()
                    
                    if not source_channel:
                        logger.debug(f"频道 {chat_id} 不是监听源，忽略编辑消息")
                        return
                    
                    # 查找之前转发的记录
                    forwarded_records = ForwardedMessage.query.filter_by(
                        message_id=message_id,
                        source_channel_id=chat_id
                    ).all()
                    
                    if not forwarded_records:
                        logger.debug(f"没有找到原消息ID为 {message_id} 的转发记录，忽略编辑")
                        return
                    
                    logger.info(f"找到 {len(forwarded_records)} 条消息ID为 {message_id} 的转发记录，准备更新")
                    
                    # 获取消息内容作为标题
                    message_text = event.message.message
                    message_title = message_text[:100] if message_text else "无文本内容"
                    logger.debug(f"编辑后的消息内容: {message_title[:50]}{'...' if len(message_title) > 50 else ''}")
                    
                    # 更新每条转发记录
                    for record in forwarded_records:
                        # 检查是否有已保存的转发消息ID
                        if record.forwarded_msg_id:
                            try:
                                # 处理目标ID格式
                                target_id = record.destination_channel_id
                                if target_id.startswith('-100') and target_id[4:].isdigit():
                                    target_id = int(target_id[4:])
                                
                                # 获取目标实体
                                dest_entity = await self.client.get_entity(target_id)
                                
                                # 在目标频道更新消息
                                await self.client.edit_message(
                                    entity=dest_entity,
                                    message=record.forwarded_msg_id,
                                    text=message_text
                                )
                                
                                # 更新数据库记录
                                record.message_title = message_title
                                record.forwarded_at = datetime.utcnow()
                                db.session.commit()
                                
                                logger.info(f"已更新转发消息: 目标 {record.destination_channel_id}, 消息ID {record.forwarded_msg_id}")
                            except Exception as e:
                                logger.error(f"更新转发消息失败: {e}")
                                # 消息可能已被删除或无法编辑，记录错误但不阻止其他更新
                        else:
                            logger.debug(f"转发记录 {record.id} 没有保存转发后的消息ID，无法更新")
            else:
                logger.error("未设置Flask应用实例，无法处理数据库操作")
        except Exception as e:
            logger.error(f"处理编辑消息时发生错误: {str(e)}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
    
    async def _forward_message_to_channel(self, message, source_chat_id, source_title, dest_id, dest_title, message_title):
        """实际执行转发消息的辅助方法"""
        try:
            logger.debug(f"开始转发到: {dest_title} ({dest_id})")
            # 处理目标ID格式
            target_id = dest_id
            if target_id.startswith('-100') and target_id[4:].isdigit():
                target_id = int(target_id[4:])
                logger.debug(f"使用处理后的目标ID: {target_id}")
            
            dest_entity = await self.client.get_entity(target_id)
            
            forwarded = await self.client.forward_messages(
                dest_entity,
                message
            )
            
            # 获取转发后的消息ID
            forwarded_msg_id = None
            if forwarded and isinstance(forwarded, list) and len(forwarded) > 0:
                forwarded_msg_id = forwarded[0].id
            elif hasattr(forwarded, 'id'):
                forwarded_msg_id = forwarded.id
            
            # 每次转发操作都在新的app上下文中执行数据库操作
            if self.app:
                with self.app.app_context():
                    # 记录转发消息
                    forwarded_msg = ForwardedMessage(
                        message_id=message.id,
                        source_channel_id=source_chat_id,
                        destination_channel_id=dest_id,
                        message_title=message_title,
                        forwarded_at=datetime.utcnow(),
                        forwarded_msg_id=forwarded_msg_id
                    )
                    db.session.add(forwarded_msg)
                    db.session.commit()
            
            logger.info(f"消息已转发: {source_title} -> {dest_title}, 转发后消息ID: {forwarded_msg_id}")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            
            # 检查是否是禁止转发的错误
            if 'restricted' in error_msg and 'forward' in error_msg:
                # 这是禁止转发的错误
                error_detail = f"消息来自受保护的聊天，无法转发"
                logger.error(f"转发失败 - {error_detail}")
                
                # 如果应用上下文可用，记录这个错误到数据库
                if self.app:
                    with self.app.app_context():
                        try:
                            # 记录特殊错误类型的转发失败
                            forwarded_msg = ForwardedMessage(
                                message_id=message.id,
                                source_channel_id=source_chat_id,
                                destination_channel_id=dest_id,
                                message_title=f"[转发失败] {error_detail}",
                                forwarded_at=datetime.utcnow(),
                                forwarded_msg_id=None
                            )
                            db.session.add(forwarded_msg)
                            db.session.commit()
                            logger.debug(f"已记录转发失败的消息")
                        except Exception as db_err:
                            logger.error(f"记录转发失败消息到数据库时出错: {db_err}")
            elif 'chat_write_forbidden' in error_msg:
                # 没有权限发送消息的错误
                error_detail = f"没有在目标群组发送消息的权限"
                logger.error(f"转发失败 - {error_detail}")
                
                # 记录到数据库
                if self.app:
                    with self.app.app_context():
                        try:
                            forwarded_msg = ForwardedMessage(
                                message_id=message.id,
                                source_channel_id=source_chat_id,
                                destination_channel_id=dest_id,
                                message_title=f"[转发失败] {error_detail}",
                                forwarded_at=datetime.utcnow(),
                                forwarded_msg_id=None
                            )
                            db.session.add(forwarded_msg)
                            db.session.commit()
                        except Exception as db_err:
                            logger.error(f"记录转发失败消息到数据库时出错: {db_err}")
            elif 'not found' in error_msg or 'peer id invalid' in error_msg:
                # 目标频道不存在或ID无效
                error_detail = f"目标频道不存在或ID无效"
                logger.error(f"转发失败 - {error_detail}")
                
                # 记录到数据库
                if self.app:
                    with self.app.app_context():
                        try:
                            forwarded_msg = ForwardedMessage(
                                message_id=message.id,
                                source_channel_id=source_chat_id,
                                destination_channel_id=dest_id,
                                message_title=f"[转发失败] {error_detail}",
                                forwarded_at=datetime.utcnow(),
                                forwarded_msg_id=None
                            )
                            db.session.add(forwarded_msg)
                            db.session.commit()
                        except Exception as db_err:
                            logger.error(f"记录转发失败消息到数据库时出错: {db_err}")
            else:
                # 其他类型的错误
                error_detail = str(e)
                logger.error(f"转发消息到 {dest_title} 失败: {error_detail}")
                
                # 记录到数据库
                if self.app:
                    with self.app.app_context():
                        try:
                            forwarded_msg = ForwardedMessage(
                                message_id=message.id,
                                source_channel_id=source_chat_id,
                                destination_channel_id=dest_id,
                                message_title=f"[转发失败] {error_detail[:80]}",  # 限制长度
                                forwarded_at=datetime.utcnow(),
                                forwarded_msg_id=None
                            )
                            db.session.add(forwarded_msg)
                            db.session.commit()
                        except Exception as db_err:
                            logger.error(f"记录转发失败消息到数据库时出错: {db_err}")
                
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
            return False

# 全局Telegram客户端实例
telegram_client = None

def init_telegram_client(api_id, api_hash, phone, app=None):
    """初始化Telegram客户端"""
    global telegram_client
    logger.debug(f"初始化Telegram客户端: API_ID={api_id}, 手机号={phone}")
    telegram_client = TelegramForwarder(api_id, api_hash, phone)
    if app:
        telegram_client.app = app
    return telegram_client

def get_telegram_client():
    """获取Telegram客户端实例"""
    global telegram_client
    return telegram_client 