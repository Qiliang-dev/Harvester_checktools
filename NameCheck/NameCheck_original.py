"""
文件名检查工具 - 原始单文件版本
功能：比较Excel文件中的文件名与文件夹中的文件，检查文件完整性
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import re
from typing import List, Set, Dict, Optional, Tuple

# 配置常量
FILENAME_PATTERN = r'20\d{2}_\d{2}_\d{2}_\d{6}'
FILES_PER_TEST = 4
WINDOW_TITLE = "文件名检查工具"
RESULT_WINDOW_TITLE = "对比结果"
RESULT_WINDOW_WIDTH = 600
RESULT_WINDOW_HEIGHT = 400

def extract_filename_base(file_name: str) -> Optional[str]:
    """
    提取文件名中符合模式的基本部分 (20xx_xx_xx_xxxxxx)
    
    Args:
        file_name: 待处理的文件名
        
    Returns:
        匹配的文件名基本部分，如果没有匹配则返回None
    """
    match = re.search(FILENAME_PATTERN, file_name)
    if match:
        return match.group(0)  # 返回匹配的模式
    return None

def get_folder_files(folder_path: str) -> List[str]:
    """
    获取文件夹中的所有文件
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        文件夹中的文件列表
    """
    return os.listdir(folder_path)

def extract_folder_filename_bases(folder_filenames: List[str]) -> Set[str]:
    """
    从文件夹文件列表中提取符合模式的文件名基本部分
    
    Args:
        folder_filenames: 文件夹中的文件列表
            
    Returns:
        符合模式的文件名基本部分集合
    """
    return set([extract_filename_base(f) for f in folder_filenames if extract_filename_base(f)])

def check_file_completeness(folder_path: str, folder_filenames: List[str]) -> List[str]:
    """
    检查每个测试编号是否有完整的文件集合
    
    Args:
        folder_path: 文件夹路径
        folder_filenames: 文件夹中的文件列表
        
    Returns:
        不完整的测试编号列表
    """
    # 按测试编号分组文件
    files_by_number = {}
    
    # 将文件按其基本编号分组
    for filename in folder_filenames:
        # 使用extract_filename_base函数获取完整的日期-编号字符串
        base_name = extract_filename_base(filename)
        if base_name:
            # 使用完整的日期-编号字符串作为键
            if base_name not in files_by_number:
                files_by_number[base_name] = set()
            files_by_number[base_name].add(filename)
    
    # 检查每个编号的完整性
    incomplete_numbers = []
    for number, files in files_by_number.items():
        if len(files) < FILES_PER_TEST:  # 如果文件数小于FILES_PER_TEST，则不完整
            incomplete_numbers.append(number)
    
    return incomplete_numbers

def split_filenames(cell_value):
    """
    使用多种分隔符分割单元格内容
    
    Args:
        cell_value: 单元格内容
        
    Returns:
        分割后的文件名列表
    """
    if isinstance(cell_value, str):
        # 使用常见分隔符：换行符、逗号、分号、空格
        delimiters = r'[\n,; ]+'
        return re.split(delimiters, cell_value)
    return []

def scan_excel_for_filenames(df: pd.DataFrame) -> Tuple[pd.Series, List[str], int]:
    """
    扫描整个Excel表格，找出所有符合模式的文件名
    
    Args:
        df: pandas DataFrame对象
        
    Returns:
        Tuple包含：
        - 所有唯一的文件名（pandas.Series）
        - 重复的文件名列表
        - 不同测试编号的数量
    """
    all_filenames = []
    for col in df.columns:
        column_data = df[col].dropna().apply(split_filenames).explode()
        column_filenames = column_data.apply(lambda x: extract_filename_base(str(x))).dropna()
        all_filenames.extend(column_filenames)
    
    # 转换为Series并找出重复项
    filename_series = pd.Series(all_filenames)
    duplicates = filename_series[filename_series.duplicated()].unique()
    unique_filenames = filename_series.drop_duplicates()
    
    # 计算不同的测试编号数量
    test_numbers = set()
    for filename in all_filenames:
        if filename:
            test_number = filename[-6:]  # 获取文件名最后6位数字
            test_numbers.add(test_number)
    
    return unique_filenames, duplicates.tolist(), len(test_numbers)

def get_excel_sheets(file_path: str) -> List[str]:
    """
    获取Excel文件的所有sheet名称
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        sheet名称列表
    """
    return pd.ExcelFile(file_path).sheet_names

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
                if line.strip() and not line.startswith("在Excel中") and not line.startswith("在文件夹中"):
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
                    if line.strip() and not line.startswith("在Excel中") and not line.startswith("在文件夹中")]
        
        # 直接连接所有文件名（不添加任何分隔符）
        single_line = ''.join(filenames)
        
        # 确保删除所有可能的换行符
        single_line = single_line.replace('\n', '').replace('\r', '')
        
        self.window.clipboard_clear()
        self.window.clipboard_append(single_line)
        messagebox.showinfo("成功", "结果已复制为单行！")

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

def main():
    """
    程序主入口函数
    """
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
