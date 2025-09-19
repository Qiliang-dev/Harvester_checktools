#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vehicle替换器功能
"""

import os
import sys
import shutil
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vehicle_replacer import VehicleReplacer

def test_vehicle_replacer():
    """测试Vehicle替换器功能"""
    print("=== Vehicle Replacer 测试 ===")
    
    # 检查测试文件是否存在
    source_file = "Austauchen/2025_09_19_134119_H022296_E.yaml"
    target_file = "Austauchen/2025_04_15_151228_DA00097_E.yaml"
    
    if not os.path.exists(source_file):
        print(f"错误: 源文件不存在 - {source_file}")
        return False
    
    if not os.path.exists(target_file):
        print(f"错误: 目标文件不存在 - {target_file}")
        return False
    
    print(f"源文件: {source_file}")
    print(f"目标文件: {target_file}")
    
    # 创建测试副本
    test_target_file = target_file.replace('.yaml', '_test.yaml')
    shutil.copy2(target_file, test_target_file)
    print(f"创建测试副本: {test_target_file}")
    
    try:
        # 创建替换器实例
        replacer = VehicleReplacer()
        
        # 测试文件加载
        print("\n1. 测试文件加载...")
        source_data = replacer.load_yaml_file(source_file)
        target_data = replacer.load_yaml_file(test_target_file)
        print("   文件加载成功")
        
        # 测试Vehicle内容提取
        print("\n2. 测试Vehicle内容提取...")
        source_vehicle = replacer.extract_vehicle_content(source_data)
        target_vehicle = replacer.extract_vehicle_content(target_data)
        print(f"   源文件Vehicle包含: {len(source_vehicle)}个主要部分")
        print(f"   目标文件Vehicle包含: {len(target_vehicle)}个主要部分")
        
        # 显示主要差异
        print("\n3. 主要差异预览...")
        if 'CarModel' in source_vehicle and 'CarModel' in target_vehicle:
            print("   CarModel差异:")
            for key in ['Variant', 'VIN']:
                if key in source_vehicle['CarModel'] and key in target_vehicle['CarModel']:
                    print(f"     {key}: {target_vehicle['CarModel'][key]} -> {source_vehicle['CarModel'][key]}")
        
        if 'OptionalEquipment' in source_vehicle and 'OptionalEquipment' in target_vehicle:
            source_eq = set(source_vehicle['OptionalEquipment'].keys())
            target_eq = set(target_vehicle['OptionalEquipment'].keys())
            print(f"   OptionalEquipment: {len(target_eq)}项 -> {len(source_eq)}项")
            print(f"     新增: {len(source_eq - target_eq)}项")
            print(f"     删除: {len(target_eq - source_eq)}项")
        
        # 测试替换操作
        print("\n4. 测试Vehicle内容替换...")
        result = replacer.perform_replacement(source_file, test_target_file)
        print(f"   替换结果: {result}")
        
        # 验证替换结果
        print("\n5. 验证替换结果...")
        new_data = replacer.load_yaml_file(test_target_file)
        new_vehicle = replacer.extract_vehicle_content(new_data)
        
        # 检查关键字段是否已替换
        if 'CarModel' in new_vehicle and 'CarModel' in source_vehicle:
            if new_vehicle['CarModel'].get('VIN') == source_vehicle['CarModel'].get('VIN'):
                print("   ✓ VIN替换成功")
            else:
                print("   ✗ VIN替换失败")
        
        if 'OptionalEquipment' in new_vehicle and 'OptionalEquipment' in source_vehicle:
            if len(new_vehicle['OptionalEquipment']) == len(source_vehicle['OptionalEquipment']):
                print("   ✓ OptionalEquipment替换成功")
            else:
                print("   ✗ OptionalEquipment替换失败")
        
        if 'Engine' in new_vehicle and 'Engine' in source_vehicle:
            if new_vehicle['Engine'].get('State') == source_vehicle['Engine'].get('State'):
                print("   ✓ Engine替换成功")
            else:
                print("   ✗ Engine替换失败")
        
        print("\n测试完成!")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        return False
    
    finally:
        # 清理测试文件
        if os.path.exists(test_target_file):
            os.remove(test_target_file)
            print(f"清理测试文件: {test_target_file}")

def run_gui_test():
    """运行GUI测试"""
    print("\n=== GUI 测试 ===")
    try:
        import tkinter as tk
        from vehicle_replacer import VehicleReplacerGUI
        
        root = tk.Tk()
        app = VehicleReplacerGUI(root)
        
        print("GUI启动成功! 请手动测试界面功能...")
        print("测试建议:")
        print("1. 点击'快速替换'按钮测试自动文件检测")
        print("2. 手动选择文件测试文件选择功能")
        print("3. 测试'预览差异'功能")
        print("4. 测试'执行替换'功能")
        
        root.mainloop()
        
    except Exception as e:
        print(f"GUI测试失败: {str(e)}")

if __name__ == "__main__":
    print("Vehicle Replacer 测试程序")
    print("========================")
    
    # 基础功能测试
    success = test_vehicle_replacer()
    
    if success:
        print("\n基础功能测试通过!")
        
        # 询问是否进行GUI测试
        response = input("\n是否启动GUI测试? (y/n): ").lower().strip()
        if response == 'y' or response == 'yes':
            run_gui_test()
    else:
        print("\n基础功能测试失败, 请检查错误信息")
