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
import sys
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash, session
from app.models import db, Channel, ForwardedMessage, Dialog, ForwardRule
from app.telegram_client import get_telegram_client, init_telegram_client

# 获取应用日志记录器
logger = logging.getLogger('app.routes')

main_bp = Blueprint('main', __name__)

# 全局变量存储后台任务循环
telegram_loop = None
background_task = None

# 帮助函数：将UTC时间转换为北京时间
def to_beijing_time(utc_time):
    """将UTC时间转换为北京时间（UTC+8）"""
    return utc_time + timedelta(hours=8)

@main_bp.context_processor
def inject_now():
    """向所有模板注入当前时间变量"""
    return {'now': datetime.now()}

@main_bp.route('/')
def index():
    """主页 - 显示监控概览"""
    try:
        logger.debug("访问首页")
        # 获取所有源频道和目标频道
        source_channels = Channel.query.filter_by(is_source=True).all()
        destination_channels = Channel.query.filter_by(is_destination=True).all()
        
        # 获取活跃的转发规则
        active_rules = ForwardRule.query.filter_by(is_active=True).all()
        
        # 获取今日转发数量
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = ForwardedMessage.query.filter(ForwardedMessage.forwarded_at >= today).count()
        
        # 获取最近20条转发记录
        recent_forwards = ForwardedMessage.query.order_by(
            ForwardedMessage.forwarded_at.desc()
        ).limit(20).all()
        
        # Telegram客户端状态
        tg_client = get_telegram_client()
        client_status = "运行中" if tg_client and tg_client.is_running else "未运行"
        logger.debug(f"Telegram客户端状态: {client_status}")
        
        # 获取所有频道的映射，用于显示频道名称
        channels = {c.channel_id: c.channel_title for c in Channel.query.all()}
        
        return render_template(
            'index.html',
            source_channels=source_channels,
            destination_channels=destination_channels,
            active_rules=active_rules,
            today_count=today_count,
            recent_forwards=recent_forwards,
            client_status=client_status,
            channels=channels,
            to_beijing_time=to_beijing_time
        )
    except Exception as e:
        logger.error(f"首页渲染出错: {e}")
        logger.error(traceback.format_exc())
        return f"服务器错误: {str(e)}", 500

@main_bp.route('/channels', methods=['GET', 'POST'])
def manage_channels():
    """管理频道"""
    try:
        if request.method == 'POST':
            logger.debug("提交频道表单")
            channel_id = request.form.get('channel_id')
            is_source = 'is_source' in request.form
            is_destination = 'is_destination' in request.form
            
            logger.debug(f"频道ID: {channel_id}, 是否源: {is_source}, 是否目标: {is_destination}")
            
            # 检查频道是否已存在
            channel = Channel.query.filter_by(channel_id=channel_id).first()
            
            if not channel:
                logger.debug(f"新频道: {channel_id}")
                # 获取频道信息
                tg_client = get_telegram_client()
                if not tg_client or not tg_client.is_running:
                    logger.warning("Telegram客户端未运行")
                    return jsonify({'success': False, 'error': 'Telegram客户端未运行'}), 400
                
                # 获取主模块中的telegram_loop
                main_module = sys.modules.get('__main__')
                if main_module and hasattr(main_module, 'telegram_loop'):
                    telegram_loop = main_module.telegram_loop
                    try:
                        # 检查客户端连接状态
                        if tg_client.client and not tg_client.client.is_connected():
                            logger.warning("客户端未连接，尝试重新连接")
                            # 创建一个新的事件循环用于重连
                            reconnect_future = asyncio.run_coroutine_threadsafe(
                                tg_client.reconnect(), 
                                telegram_loop
                            )
                            reconnect_result = reconnect_future.result(timeout=10)
                            if not reconnect_result:
                                logger.error("重新连接失败")
                                return jsonify({'success': False, 'error': '重新连接Telegram客户端失败'}), 400
                        
                        # 使用正确的循环获取频道信息
                        logger.debug(f"开始获取频道信息: {channel_id}")
                        future = asyncio.run_coroutine_threadsafe(
                            tg_client.get_entity_info(channel_id), 
                            telegram_loop
                        )
                        channel_info = future.result(timeout=15)  # 设置适当的超时时间
                        logger.debug(f"获取频道信息结果: {channel_info}")
                    except Exception as e:
                        logger.error(f"获取频道信息时出错: {e}")
                        logger.error(traceback.format_exc())
                        return jsonify({'success': False, 'error': f'获取频道信息时出错: {str(e)}'}), 400
                else:
                    logger.error("无法获取主模块中的telegram_loop")
                    return jsonify({'success': False, 'error': 'Telegram客户端循环未初始化'}), 400
                
                if not channel_info['success']:
                    logger.error(f"找不到频道: {channel_info.get('error', '未知错误')}")
                    return jsonify({'success': False, 'error': f'找不到频道: {channel_info.get("error", "未知错误")}'}), 400
                
                # 创建新频道
                channel = Channel(
                    channel_id=channel_info['id'],  # 使用返回的ID，可能已格式化
                    channel_title=channel_info['title'],
                    is_source=is_source,
                    is_destination=is_destination
                )
                db.session.add(channel)
                logger.debug(f"添加新频道: {channel.channel_title} (ID: {channel.channel_id})")
            else:
                # 更新现有频道
                channel.is_source = is_source
                channel.is_destination = is_destination
                logger.debug(f"更新频道: {channel.channel_title} (ID: {channel.channel_id})")
            
            db.session.commit()
            return redirect(url_for('main.manage_channels'))
        
        # 获取所有频道
        channels = Channel.query.all()
        logger.debug(f"加载频道列表: {len(channels)}个频道")
        return render_template('channels.html', channels=channels)
    except Exception as e:
        logger.error(f"频道管理页面出错: {e}")
        logger.error(traceback.format_exc())
        return f"服务器错误: {str(e)}", 500

@main_bp.route('/channels/<int:channel_id>/delete', methods=['POST'])
def delete_channel(channel_id):
    """删除频道"""
    try:
        logger.debug(f"删除频道ID: {channel_id}")
        channel = Channel.query.get_or_404(channel_id)
        logger.debug(f"找到频道: {channel.channel_title} ({channel.channel_id})")
        db.session.delete(channel)
        db.session.commit()
        logger.debug("频道删除成功")
        return redirect(url_for('main.manage_channels'))
    except Exception as e:
        logger.error(f"删除频道时出错: {e}")
        logger.error(traceback.format_exc())
        return f"删除频道失败: {str(e)}", 500

@main_bp.route('/messages')
def message_history():
    """消息历史"""
    try:
        logger.debug("访问消息历史页面")
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # 获取所有转发消息
        messages = ForwardedMessage.query.order_by(
            ForwardedMessage.forwarded_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        # 获取频道信息以便显示频道名称
        channels = {c.channel_id: c.channel_title for c in Channel.query.all()}
        
        logger.debug(f"加载消息历史: 第{page}页, 共{messages.total}条记录")
        return render_template('messages.html', messages=messages, channels=channels, to_beijing_time=to_beijing_time)
    except Exception as e:
        logger.error(f"加载消息历史时出错: {e}")
        logger.error(traceback.format_exc())
        return f"加载消息历史失败: {str(e)}", 500

@main_bp.route('/start_client', methods=['POST'])
def start_client():
    """启动Telegram客户端"""
    try:
        global telegram_loop, background_task
        
        logger.debug("请求启动Telegram客户端")
        tg_client = get_telegram_client()
        if tg_client and tg_client.is_running:
            logger.warning("Telegram客户端已经在运行")
            return jsonify({'success': False, 'message': 'Telegram客户端已经在运行'})
        
        # 获取主模块中的init_app函数
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'init_app'):
            logger.debug("调用主模块中的init_app函数")
            main_module.init_app()
            return jsonify({'success': True, 'message': 'Telegram客户端正在启动中'})
        else:
            logger.error("无法获取主模块中的init_app函数")
            return jsonify({'success': False, 'message': '无法初始化Telegram客户端'}), 500
    except Exception as e:
        logger.error(f"启动Telegram客户端失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'启动失败: {str(e)}'}), 500

@main_bp.route('/stop_client', methods=['POST'])
def stop_client():
    """停止Telegram客户端"""
    try:
        global telegram_loop, background_task
        
        logger.debug("请求停止Telegram客户端")
        tg_client = get_telegram_client()
        if not tg_client or not tg_client.is_running:
            logger.warning("Telegram客户端未运行")
            return jsonify({'success': False, 'message': 'Telegram客户端未运行'})
        
        # 获取主模块中的telegram_loop
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'telegram_loop'):
            telegram_loop = main_module.telegram_loop
            try:
                # 在正确的循环中停止客户端
                logger.debug("发送停止请求到客户端")
                future = asyncio.run_coroutine_threadsafe(tg_client.stop(), telegram_loop)
                future.result(timeout=5)  # 等待最多5秒
                logger.debug("Telegram客户端已停止")
                return jsonify({'success': True, 'message': 'Telegram客户端已停止'})
            except Exception as e:
                logger.error(f"停止客户端失败: {e}")
                logger.error(traceback.format_exc())
                return jsonify({'success': False, 'message': f'停止客户端失败: {str(e)}'})
        
        logger.error("无法获取主模块中的telegram_loop")
        return jsonify({'success': False, 'message': 'Telegram客户端循环未初始化'})
    except Exception as e:
        logger.error(f"停止Telegram客户端时发生错误: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'错误: {str(e)}'}), 500

@main_bp.route('/stats')
def stats():
    """统计数据API"""
    try:
        logger.debug("请求统计数据")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今日转发数量
        today_count = ForwardedMessage.query.filter(ForwardedMessage.forwarded_at >= today).count()
        
        # 按小时统计今日转发数量
        hourly_stats = []
        for hour in range(24):
            hour_start = today + timedelta(hours=hour)
            hour_end = today + timedelta(hours=hour+1)
            
            count = ForwardedMessage.query.filter(
                ForwardedMessage.forwarded_at >= hour_start,
                ForwardedMessage.forwarded_at < hour_end
            ).count()
            
            hourly_stats.append({
                'hour': hour,
                'count': count
            })
        
        # 按源频道统计
        source_stats = []
        sources = Channel.query.filter_by(is_source=True).all()
        for source in sources:
            count = ForwardedMessage.query.filter(
                ForwardedMessage.source_channel_id == source.channel_id,
                ForwardedMessage.forwarded_at >= today
            ).count()
            
            source_stats.append({
                'channel': source.channel_title,
                'count': count
            })
        
        logger.debug(f"统计数据: 今日总计 {today_count}条")
        return jsonify({
            'today_count': today_count,
            'hourly_stats': hourly_stats,
            'source_stats': source_stats
        })
    except Exception as e:
        logger.error(f"获取统计数据时出错: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# 添加健康检查接口
@main_bp.route('/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute("SELECT 1").scalar()
        
        # 检查Telegram客户端状态
        tg_client = get_telegram_client()
        telegram_status = "running" if tg_client and tg_client.is_running else "stopped"
        
        # 获取连接状态
        connected = False
        if tg_client and tg_client.client:
            connected = tg_client.client.is_connected()
        
        # 获取主模块中的telegram_loop状态
        main_module = sys.modules.get('__main__')
        loop_running = False
        if main_module and hasattr(main_module, 'telegram_loop'):
            telegram_loop = main_module.telegram_loop
            loop_running = telegram_loop is not None and telegram_loop.is_running()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'telegram_client': telegram_status,
            'connected': connected,
            'loop_running': loop_running,
            'db_connected': True
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@main_bp.route('/api/dialogs', methods=['GET'])
def get_dialogs():
    """获取Telegram对话列表"""
    try:
        logger.debug("请求获取对话列表")
        force_refresh = request.args.get('refresh', '0') == '1'
        
        tg_client = get_telegram_client()
        if not tg_client:
            logger.error("Telegram客户端未初始化")
            return jsonify({'success': False, 'error': 'Telegram客户端未初始化'}), 400
            
        # 如果不强制刷新，首先尝试从数据库获取缓存的对话列表
        if not force_refresh:
            dialogs = Dialog.query.all()
            if dialogs:
                logger.debug(f"从数据库缓存获取到 {len(dialogs)} 个对话")
                return jsonify({
                    'success': True, 
                    'results': [dialog.to_dict() for dialog in dialogs],
                    'from_cache': True
                })
        
        # 获取主模块中的telegram_loop
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'telegram_loop'):
            telegram_loop = main_module.telegram_loop
            logger.debug("开始获取对话列表")
            
            try:
                future = asyncio.run_coroutine_threadsafe(
                    tg_client.get_dialogs(use_cache=not force_refresh, force_update=force_refresh), 
                    telegram_loop
                )
                dialogs_result = future.result(timeout=30)  # 设置较长的超时时间，因为可能会获取很多对话
                
                # 检查结果是否成功且有内容
                if not dialogs_result.get('success') or not dialogs_result.get('results'):
                    logger.warning("主方法获取对话列表失败或无结果，尝试备用方法")
                    # 使用备用方法
                    backup_future = asyncio.run_coroutine_threadsafe(
                        tg_client.get_followed_channels(), 
                        telegram_loop
                    )
                    dialogs_result = backup_future.result(timeout=30)
                
                logger.debug(f"获取对话列表结果: {len(dialogs_result.get('results', []))}个对话")
                return jsonify(dialogs_result)
            except Exception as e:
                logger.error(f"获取对话列表时出错: {e}")
                logger.error(traceback.format_exc())
                
                # 尝试备用方法
                try:
                    logger.debug("主方法失败，尝试备用方法获取频道列表")
                    backup_future = asyncio.run_coroutine_threadsafe(
                        tg_client.get_followed_channels(), 
                        telegram_loop
                    )
                    backup_result = backup_future.result(timeout=30)
                    logger.debug(f"备用方法获取到 {len(backup_result.get('results', []))} 个频道")
                    return jsonify(backup_result)
                except Exception as e2:
                    logger.error(f"备用方法也失败: {e2}")
                    logger.error(traceback.format_exc())
                    
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            logger.error("无法获取主模块中的telegram_loop")
            return jsonify({'success': False, 'error': 'Telegram客户端循环未初始化'}), 400
    except Exception as e:
        logger.error(f"获取对话列表时发生错误: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/sync_dialogs', methods=['POST'])
def sync_dialogs():
    """同步所有对话到本地数据库"""
    try:
        logger.debug("请求同步对话列表")
        tg_client = get_telegram_client()
        if not tg_client:
            logger.error("Telegram客户端未初始化")
            return jsonify({'success': False, 'error': 'Telegram客户端未初始化'}), 400
            
        # 获取主模块中的telegram_loop
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'telegram_loop'):
            telegram_loop = main_module.telegram_loop
            logger.debug("开始同步对话列表")
            
            try:
                # 尝试主方法
                future = asyncio.run_coroutine_threadsafe(
                    tg_client.sync_dialogs(), 
                    telegram_loop
                )
                sync_result = future.result(timeout=60)  # 设置更长的超时时间
                
                # 检查结果是否成功且有内容
                if not sync_result.get('success') or not sync_result.get('results'):
                    logger.warning("主方法同步对话列表失败或无结果，尝试备用方法")
                    # 使用备用方法
                    backup_future = asyncio.run_coroutine_threadsafe(
                        tg_client.get_followed_channels(), 
                        telegram_loop
                    )
                    sync_result = backup_future.result(timeout=30)
                
                dialogs_count = len(sync_result.get('results', []))
                logger.debug(f"同步对话列表完成: {dialogs_count}个对话")
                return jsonify({
                    'success': True,
                    'message': f'已同步{dialogs_count}个对话到本地数据库',
                    'count': dialogs_count
                })
            except Exception as e:
                logger.error(f"同步对话列表时出错: {e}")
                logger.error(traceback.format_exc())
                
                # 尝试备用方法
                try:
                    logger.debug("主方法失败，尝试备用方法同步频道列表")
                    backup_future = asyncio.run_coroutine_threadsafe(
                        tg_client.get_followed_channels(), 
                        telegram_loop
                    )
                    backup_result = backup_future.result(timeout=30)
                    dialogs_count = len(backup_result.get('results', []))
                    logger.debug(f"备用方法同步频道列表完成: {dialogs_count}个频道")
                    return jsonify({
                        'success': True,
                        'message': f'已使用备用方法同步{dialogs_count}个频道到本地数据库',
                        'count': dialogs_count
                    })
                except Exception as e2:
                    logger.error(f"备用方法也失败: {e2}")
                    logger.error(traceback.format_exc())
                    
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            logger.error("无法获取主模块中的telegram_loop")
            return jsonify({'success': False, 'error': 'Telegram客户端循环未初始化'}), 400
    except Exception as e:
        logger.error(f"同步对话列表时发生错误: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/rules')
def manage_rules():
    """管理转发规则页面"""
    try:
        logger.debug("访问转发规则管理页面")
        
        # 获取所有规则
        rules = ForwardRule.query.all()
        
        # 获取所有频道，用于创建新规则
        source_channels = Channel.query.filter_by(is_source=True).all()
        destination_channels = Channel.query.filter_by(is_destination=True).all()
        
        return render_template(
            'rules.html',
            rules=rules,
            source_channels=source_channels,
            destination_channels=destination_channels
        )
    except Exception as e:
        logger.error(f"转发规则管理页面加载出错: {e}")
        logger.error(traceback.format_exc())
        return f"服务器错误: {str(e)}", 500

@main_bp.route('/rules/add', methods=['POST'])
def add_rule():
    """添加新的转发规则"""
    try:
        logger.debug("添加新的转发规则")
        
        source_id = request.form.get('source_id', type=int)
        destination_id = request.form.get('destination_id', type=int)
        
        if not source_id or not destination_id:
            flash('请选择源频道和目标频道', 'error')
            return redirect(url_for('main.manage_rules'))
        
        # 检查源频道和目标频道是否存在
        source = Channel.query.get(source_id)
        destination = Channel.query.get(destination_id)
        
        if not source or not destination:
            flash('选择的频道不存在', 'error')
            return redirect(url_for('main.manage_rules'))
        
        # 检查是否已存在相同的规则
        existing_rule = ForwardRule.query.filter_by(
            source_channel_id=source_id,
            destination_channel_id=destination_id
        ).first()
        
        if existing_rule:
            flash('已存在相同的转发规则', 'warning')
            return redirect(url_for('main.manage_rules'))
        
        # 创建新规则
        new_rule = ForwardRule(
            source_channel_id=source_id,
            destination_channel_id=destination_id,
            is_active=True
        )
        
        db.session.add(new_rule)
        db.session.commit()
        
        flash(f'成功添加转发规则: {source.channel_title} -> {destination.channel_title}', 'success')
        return redirect(url_for('main.manage_rules'))
    except Exception as e:
        logger.error(f"添加转发规则出错: {e}")
        logger.error(traceback.format_exc())
        flash(f'添加规则失败: {str(e)}', 'error')
        return redirect(url_for('main.manage_rules'))

@main_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
def toggle_rule(rule_id):
    """启用/禁用转发规则"""
    try:
        logger.debug(f"切换规则 {rule_id} 的状态")
        
        rule = ForwardRule.query.get_or_404(rule_id)
        rule.is_active = not rule.is_active
        
        db.session.commit()
        
        status = "启用" if rule.is_active else "禁用"
        flash(f'已{status}转发规则: {rule.source_channel.channel_title} -> {rule.destination_channel.channel_title}', 'success')
        return redirect(url_for('main.manage_rules'))
    except Exception as e:
        logger.error(f"切换规则状态出错: {e}")
        logger.error(traceback.format_exc())
        flash(f'操作失败: {str(e)}', 'error')
        return redirect(url_for('main.manage_rules'))

@main_bp.route('/rules/<int:rule_id>/delete', methods=['POST'])
def delete_rule(rule_id):
    """删除转发规则"""
    try:
        logger.debug(f"删除规则 {rule_id}")
        
        rule = ForwardRule.query.get_or_404(rule_id)
        source_title = rule.source_channel.channel_title
        dest_title = rule.destination_channel.channel_title
        
        db.session.delete(rule)
        db.session.commit()
        
        flash(f'已删除转发规则: {source_title} -> {dest_title}', 'success')
        return redirect(url_for('main.manage_rules'))
    except Exception as e:
        logger.error(f"删除规则出错: {e}")
        logger.error(traceback.format_exc())
        flash(f'删除失败: {str(e)}', 'error')
        return redirect(url_for('main.manage_rules'))

@main_bp.route('/api/recent_errors')
def recent_errors():
    """获取最近的转发错误信息"""
    try:
        # 获取最近10条转发失败的消息
        recent_errors = ForwardedMessage.query.filter(
            ForwardedMessage.message_title.like('[转发失败]%')
        ).order_by(ForwardedMessage.forwarded_at.desc()).limit(10).all()
        
        error_data = []
        for error in recent_errors:
            # 获取来源和目标频道名称
            source_channel = Channel.query.filter_by(channel_id=error.source_channel_id).first()
            dest_channel = Channel.query.filter_by(channel_id=error.destination_channel_id).first()
            
            source_name = source_channel.channel_title if source_channel else error.source_channel_id
            dest_name = dest_channel.channel_title if dest_channel else error.destination_channel_id
            
            # 提取错误消息（移除[转发失败]前缀）
            error_message = error.message_title.replace('[转发失败] ', '')
            
            # 转换为北京时间
            beijing_time = to_beijing_time(error.forwarded_at)
            
            error_data.append({
                'id': error.id,
                'time': beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': source_name,
                'destination': dest_name,
                'message': error_message,
                'timestamp': int(beijing_time.timestamp())
            })
        
        return jsonify({
            'success': True,
            'errors': error_data
        })
    except Exception as e:
        logger.error(f"获取转发错误信息失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/error_log')
def error_log():
    """错误日志页面"""
    try:
        logger.debug("访问错误日志页面")
        # 更新最后访问错误日志的时间
        session['last_error_check'] = datetime.utcnow()
        
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # 获取所有转发失败的消息
        errors = ForwardedMessage.query.filter(
            ForwardedMessage.message_title.like('[转发失败]%')
        ).order_by(
            ForwardedMessage.forwarded_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        # 获取频道信息以便显示频道名称
        channels = {c.channel_id: c.channel_title for c in Channel.query.all()}
        
        logger.debug(f"加载错误日志: 第{page}页, 共{errors.total}条记录")
        return render_template('error_log.html', errors=errors, channels=channels, to_beijing_time=to_beijing_time)
    except Exception as e:
        logger.error(f"加载错误日志时出错: {e}")
        logger.error(traceback.format_exc())
        return f"加载错误日志失败: {str(e)}", 500

@main_bp.route('/api/unread_errors_count')
def unread_errors_count():
    """获取未读错误数量"""
    try:
        # 获取最后一次用户访问错误日志页面的时间
        # 这里我们使用session存储最后访问时间，如果没有则使用当前时间减去1小时
        last_error_check = session.get('last_error_check', datetime.utcnow() - timedelta(hours=1))
        
        # 查询在上次查看后出现的新错误数量
        new_errors_count = ForwardedMessage.query.filter(
            ForwardedMessage.message_title.like('[转发失败]%'),
            ForwardedMessage.forwarded_at > last_error_check
        ).count()
        
        return jsonify({
            'success': True,
            'count': new_errors_count
        })
    except Exception as e:
        logger.error(f"获取未读错误数量失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 