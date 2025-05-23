"""
主窗口UI组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

from ...config.settings import WINDOW_TITLE
from ..file_utils import get_folder_files, extract_folder_filename_bases, check_file_completeness
from ..excel_utils import get_excel_sheets, scan_excel_for_filenames
from .result_window import ResultWindow

class MainWindow:
    """
    主窗口类，负责文件选择和比较操作
    """
    def __init__(self, root):
        """
        初始化主窗口
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title(WINDOW_TITLE)
        
        # 保存路径
        self.excel_path_var = tk.StringVar()
        self.folder_path_var = tk.StringVar()
        self.sheet_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        设置UI组件
        """
        # Excel文件选择
        tk.Label(self.root, text="选择Excel文件:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.excel_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="浏览", command=self.select_excel_file).grid(row=0, column=2, padx=10, pady=10)
        
        # Sheet选择
        tk.Label(self.root, text="选择Sheet:").grid(row=1, column=0, padx=10, pady=10)
        self.sheet_menu = tk.OptionMenu(self.root, self.sheet_var, '')  # 默认空菜单
        self.sheet_menu.grid(row=1, column=1, padx=10, pady=10)
        
        # 文件夹选择
        tk.Label(self.root, text="选择文件夹:").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.folder_path_var, width=50).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.root, text="浏览", command=self.select_folder).grid(row=2, column=2, padx=10, pady=10)
        
        # 开始比较按钮
        tk.Button(self.root, text="开始比较", command=self.compare_files).grid(row=3, column=1, padx=10, pady=20)
    
    def select_excel_file(self):
        """
        选择Excel文件
        """
        file_path = filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel文件", "*.xlsx")])
        self.excel_path_var.set(file_path)
        if file_path:
            try:
                # 读取Excel文件中的所有sheet名称
                sheet_names = get_excel_sheets(file_path)
                self.sheet_var.set(sheet_names[0])  # 默认选择第一个sheet
                self.sheet_menu['menu'].delete(0, 'end')  # 清除旧菜单
                for sheet in sheet_names:
                    self.sheet_menu['menu'].add_command(label=sheet, command=tk._setit(self.sheet_var, sheet))
            except Exception as e:
                messagebox.showerror("错误", f"无法读取Excel中的sheet: {str(e)}")
    
    def select_folder(self):
        """
        选择文件夹
        """
        folder_path = filedialog.askdirectory(title="选择文件夹")
        self.folder_path_var.set(folder_path)
    
    def compare_files(self):
        """
        比较文件
        """
        excel_file_path = self.excel_path_var.get()
        folder_path = self.folder_path_var.get()
        selected_sheet = self.sheet_var.get()
        
        if not excel_file_path or not folder_path:
            messagebox.showerror("错误", "请重新选择Excel文件和文件夹")
            return
        
        try:
            # 读取选择的Excel sheet
            df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)
            
            # 扫描整个Excel中符合模式的文件名并获取重复项
            excel_filenames, duplicates, test_count = scan_excel_for_filenames(df)
            
            # 获取文件夹中的文件列表
            folder_filenames = get_folder_files(folder_path)
            
            # 从文件夹中提取相关文件名并使用集合去除重复项
            folder_filenames_base = extract_folder_filename_bases(folder_filenames)
            
            # 比较文件名（仅匹配模式）
            excel_not_in_folder = excel_filenames[~excel_filenames.isin(folder_filenames_base)]
            folder_not_in_excel = [f for f in folder_filenames_base if f not in excel_filenames.values]
            
            # 检查文件完整性
            incomplete_files = check_file_completeness(folder_path, folder_filenames)
            
            result = ""
            has_issues = False
            
            # Excel中有但文件夹中没有的
            if not excel_not_in_folder.empty:
                has_issues = True
                result += "在Excel中但不在文件夹中:\n"
                result += "\n".join(excel_not_in_folder) + "\n\n"
            
            # 文件夹中有但Excel中没有的
            if folder_not_in_excel:
                has_issues = True
                result += "在文件夹中但不在Excel中:\n"
                result += "\n".join(folder_not_in_excel) + "\n\n"
            
            # 添加不完整文件信息
            if incomplete_files:
                has_issues = True
                result += "文件不完整的编号（少于4个文件）:\n"
                result += ", ".join(incomplete_files) + "\n\n"
            
            # 添加重复文件信息
            if duplicates:
                has_issues = True
                result += "Excel中发现重复的文件名:\n"
                result += "\n".join(duplicates) + "\n\n"
            else:
                result += "Excel中没有发现重复的文件名。\n\n"
            
            # 如果没有发现问题，显示完整的成功信息
            if not has_issues:
                result = "所有编号都有完整的文件集（每个4个文件），Excel和文件夹匹配。\nExcel中没有发现重复的文件名。"
            
            # 在结果开头添加测试计数信息
            result = f"当前Excel文件({selected_sheet})中有{test_count}个不同的测试编号。\n\n" + result
            
            # 显示结果窗口
            ResultWindow(self.root, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}") 