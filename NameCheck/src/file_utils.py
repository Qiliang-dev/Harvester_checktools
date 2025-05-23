"""
文件处理相关的工具函数
"""

import os
import re
from typing import List, Set, Dict, Optional

from ..config.settings import FILENAME_PATTERN, FILES_PER_TEST

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
        folder_filenames:
            
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