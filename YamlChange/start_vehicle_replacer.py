#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vehicle Content Replacer 启动脚本
直接启动Vehicle内容替换工具
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from vehicle_replacer import main
    
    if __name__ == "__main__":
        print("Starting Batch Vehicle Content Replacer...")
        print("Function: Replace Vehicle content in multiple files using a template")
        print("="*60)
        main()
        
except ImportError as e:
    print(f"Module import failed: {e}")
    print("Please ensure vehicle_replacer.py exists in current directory")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Startup failed: {e}")
    input("Press Enter to exit...")
