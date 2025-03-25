#!/usr/bin/env python
"""
修复依赖关系冲突的脚本
"""
import os
import sys
import subprocess

def fix_dependencies():
    """卸载冲突的包并安装正确的依赖"""
    print("开始修复依赖关系...")
    
    # 卸载Quart (如果存在)
    print("卸载Quart...")
    subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "quart"])
    
    # 确保正确的Flask和Werkzeug版本
    print("确保正确的依赖版本...")
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("依赖修复完成！")

if __name__ == "__main__":
    fix_dependencies() 