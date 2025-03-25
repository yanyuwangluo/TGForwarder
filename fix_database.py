#!/usr/bin/env python
"""
数据库修复脚本 - 添加ForwardRule表和相关更新
"""
import os
import sys
from app import create_app
from app.models import db, ForwardRule

def fix_database():
    """创建或更新ForwardRule表"""
    print("开始修复数据库...")
    
    # 创建Flask应用和上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 检查ForwardRule表是否存在
            tables = db.engine.table_names()
            
            if 'forward_rule' not in tables:
                print("创建ForwardRule表...")
                # 为了确保表创建正确，我们创建一个单独的表，避免影响其他表
                db.session.execute("""
                CREATE TABLE IF NOT EXISTS forward_rule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_channel_id INTEGER NOT NULL,
                    destination_channel_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_channel_id) REFERENCES channel (id),
                    FOREIGN KEY (destination_channel_id) REFERENCES channel (id)
                )
                """)
                db.session.commit()
                print("ForwardRule表创建成功！")
            else:
                print("ForwardRule表已存在，无需创建")
                
            print("数据库修复完成！")
        except Exception as e:
            print(f"修复数据库时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("数据库修复成功，现在可以重新启动应用")
    else:
        print("数据库修复失败") 