"""
NameCheck应用程序主入口
"""

import tkinter as tk
import sys
import os

# 添加项目根目录到Python路径，以便能够正确导入模块
# 这一步对于使用相对导入的Python包是必要的
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.main_window import MainWindow

def main():
    """
    程序主入口函数
    """
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 