"""
结果窗口UI组件
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ...config.settings import RESULT_WINDOW_TITLE, RESULT_WINDOW_WIDTH, RESULT_WINDOW_HEIGHT

class ResultWindow:
    """
    显示比较结果的窗口类
    """
    def __init__(self, parent, result_text):
        """
        初始化结果窗口
        
        Args:
            parent: 父窗口
            result_text: 要显示的结果文本
        """
        self.window = tk.Toplevel(parent)
        self.window.title(RESULT_WINDOW_TITLE)
        self.window.geometry(f"{RESULT_WINDOW_WIDTH}x{RESULT_WINDOW_HEIGHT}")

        # 保存原始文本用于撤销
        self.original_text = result_text

        # 添加输入框和按钮框架
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(pady=5)
        
        # 添加输入框
        self.suffix_var = tk.StringVar()
        ttk.Label(self.input_frame, text="添加后缀:").pack(side=tk.LEFT, padx=5)
        self.suffix_entry = ttk.Entry(self.input_frame, textvariable=self.suffix_var)
        self.suffix_entry.pack(side=tk.LEFT, padx=5)
        
        # 添加应用后缀按钮和撤销按钮
        ttk.Button(self.input_frame, text="应用后缀", command=self.apply_suffix).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="撤销", command=self.undo_changes).pack(side=tk.LEFT, padx=5)

        # 创建文本框
        self.text_widget = tk.Text(self.window, wrap=tk.WORD, width=70, height=20)
        self.text_widget.insert(tk.END, result_text)
        self.text_widget.pack(padx=10, pady=10)

        # 创建按钮框架
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=5)
        
        # 添加复制按钮
        ttk.Button(button_frame, text="复制结果(保留换行)", command=self.copy_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制为单行", command=self.copy_as_single_line).pack(side=tk.LEFT, padx=5)

    def apply_suffix(self):
        """
        为所有文件名添加后缀
        """
        suffix = self.suffix_var.get()
        if suffix:
            # 获取所有文本内容
            content = self.text_widget.get("1.0", tk.END).strip()
            lines = content.split('\n')
            
            # 处理每一行
            new_content = []
            for line in lines:
                if line.strip() and not line.startswith("In Excel") and not line.startswith("In Folder"):
                    line = line + suffix
                new_content.append(line)
            
            # 更新文本框内容
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", '\n'.join(new_content))

    def undo_changes(self):
        """
        撤销更改，恢复为原始文本
        """
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", self.original_text)

    def copy_text(self):
        """
        复制文本（保留换行）
        """
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text_widget.get("1.0", tk.END))
        messagebox.showinfo("成功", "结果已复制到剪贴板！")

    def copy_as_single_line(self):
        """
        复制为单行（删除换行符和标题行）
        """
        content = self.text_widget.get("1.0", tk.END).strip()
        lines = content.split('\n')
        
        # 过滤掉标题行和空行，只保留文件名，并删除所有空白字符
        filenames = [line.strip() for line in lines 
                    if line.strip() and not line.startswith("In Excel") and not line.startswith("In Folder")]
        
        # 直接连接所有文件名（不添加任何分隔符）
        single_line = ''.join(filenames)
        
        # 确保删除所有可能的换行符
        single_line = single_line.replace('\n', '').replace('\r', '')
        
        self.window.clipboard_clear()
        self.window.clipboard_append(single_line)
        messagebox.showinfo("成功", "结果已复制为单行！") 