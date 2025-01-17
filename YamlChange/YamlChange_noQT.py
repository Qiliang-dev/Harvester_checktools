import tkinter as tk
from tkinter import ttk, filedialog
import os
import yaml
from typing import Dict, List
from tkinterdnd2 import *

class YamlEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YAML Editor")
        self.root.geometry("500x400")
        
        # Save the YAML files and the current YAML data
        self.yaml_files = {}
        self.current_yaml_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create the main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create a frame for folder selection and drop area
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Select folder button
        ttk.Button(folder_frame, text="Choose Folder", command=self.select_folder).grid(row=0, column=0, padx=5)
        
        # Drop area
        self.drop_area = tk.Text(folder_frame, height=2, width=40)
        self.drop_area.grid(row=0, column=1, padx=5)
        self.drop_area.insert('1.0', "Drag and drop YAML files here")
        self.drop_area.configure(state='disabled')
        
        # Bind drag and drop events
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Main category selection
        ttk.Label(main_frame, text="Choose Main Category:").grid(row=2, column=0, pady=5)
        self.main_category_var = tk.StringVar()
        self.main_category_combo = ttk.Combobox(main_frame, textvariable=self.main_category_var)
        self.main_category_combo.grid(row=2, column=1, pady=5)
        self.main_category_combo.bind('<<ComboboxSelected>>', self.on_main_category_selected)
        
        # Type selection (only displayed for Vehicle class)
        self.type_frame = ttk.Frame(main_frame)
        self.type_frame.grid(row=3, column=0, columnspan=2, pady=5)
        self.type_var = tk.StringVar()
        self.type_radio_frame = ttk.Frame(self.type_frame)
        
        # Subcategory selection
        ttk.Label(main_frame, text="Choose Subcategory:").grid(row=4, column=0, pady=5)
        self.sub_category_var = tk.StringVar()
        self.sub_category_combo = ttk.Combobox(main_frame, textvariable=self.sub_category_var)
        self.sub_category_combo.grid(row=4, column=1, pady=5)
        self.sub_category_combo.bind('<<ComboboxSelected>>', self.on_sub_category_selected)
        
        # Property selection
        ttk.Label(main_frame, text="Choose Property:").grid(row=5, column=0, pady=5)
        self.property_var = tk.StringVar()
        self.property_combo = ttk.Combobox(main_frame, textvariable=self.property_var)
        self.property_combo.grid(row=5, column=1, pady=5)
        self.property_combo.bind('<<ComboboxSelected>>', self.on_property_selected)
        
        # Item property selection
        ttk.Label(main_frame, text="Item property:").grid(row=6, column=0, pady=5)
        self.item_sub_property_var = tk.StringVar()
        self.item_sub_property_combo = ttk.Combobox(main_frame, textvariable=self.item_sub_property_var, state='disabled')
        self.item_sub_property_combo.grid(row=6, column=1, pady=5)
        self.item_sub_property_combo.bind('<<ComboboxSelected>>', self.on_item_sub_property_selected)
        
        # Current value display and editing
        ttk.Label(main_frame, text="Current value:").grid(row=7, column=0, pady=5)
        self.current_value = tk.Text(main_frame, height=3, width=40)
        self.current_value.grid(row=7, column=1, pady=5)
        
        # Update button
        ttk.Button(main_frame, text="Update value", command=self.update_value).grid(row=8, column=0, columnspan=2, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=9, column=0, columnspan=2, pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.yaml_files.clear()
            # 使用 os.walk 递归遍历所有子文件夹
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.yaml'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                yaml_data = yaml.safe_load(f)
                                if yaml_data and 'TestCase' in yaml_data:
                                    self.yaml_files[file_path] = yaml_data
                        except Exception as e:
                            self.status_var.set(f"Error loading {file}: {str(e)}")
            
            if self.yaml_files:
                self.update_main_categories()
                self.status_var.set(f"已加载 {len(self.yaml_files)} 个YAML文件")
            else:
                self.status_var.set("没有找到有效的YAML文件")

    def handle_drop(self, event):
        files = event.data
        file_paths = files.split(' ')
        self.yaml_files.clear()
        for file_path in file_paths:
            file_path = file_path.strip('{}')
            if file_path.lower().endswith('.yaml'):
                self.load_yaml_file(file_path)
        self.update_main_categories()

    def load_yaml_files_from_folder(self, folder_path):
        self.yaml_files.clear()
        yaml_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    yaml_files.append(os.path.join(root, file))
        
        for file_path in yaml_files:
            self.load_yaml_file(file_path)
        
        if self.yaml_files:
            self.update_main_categories()
            self.status_var.set(f"已加载 {len(self.yaml_files)} 个YAML文件")
        else:
            self.status_var.set("没有找到有效的YAML文件")

    def load_yaml_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data and 'TestCase' in yaml_data:
                    self.yaml_files[file_path] = yaml_data
        except Exception as e:
            self.status_var.set(f"Error loading {os.path.basename(file_path)}: {str(e)}")

    def update_main_categories(self):
        if self.yaml_files:
            first_yaml = next(iter(self.yaml_files.values()))
            main_categories = list(first_yaml['TestCase'].keys())
            self.main_category_combo['values'] = main_categories
            self.status_var.set(f"已加载 {len(self.yaml_files)} 个YAML文件")
        else:
            self.status_var.set("没有找到有效的YAML文件")

    def on_main_category_selected(self, event):
        # Clear all sub-level selections
        self.sub_category_var.set('')
        self.property_var.set('')
        self.item_sub_property_var.set('')
        self.current_value.delete('1.0', tk.END)
        
        # Clear the sub-level option lists
        self.sub_category_combo['values'] = []
        self.property_combo['values'] = []
        self.item_sub_property_combo['values'] = []
        self.item_sub_property_combo['state'] = 'disabled'
        
        selected = self.main_category_var.get()
        self.type_radio_frame.grid_forget()
        
        if selected == 'Vehicle':
            # Display Seat/Door options
            self.type_radio_frame = ttk.Frame(self.type_frame)
            self.type_radio_frame.grid(row=0, column=0)
            ttk.Radiobutton(self.type_radio_frame, text="All", variable=self.type_var, 
                          value="all", command=self.update_sub_categories).grid(row=0, column=0)
            ttk.Radiobutton(self.type_radio_frame, text="Seat", variable=self.type_var,
                          value="seat", command=self.update_sub_categories).grid(row=0, column=1)
            ttk.Radiobutton(self.type_radio_frame, text="Door", variable=self.type_var,
                          value="door", command=self.update_sub_categories).grid(row=0, column=2)
            self.type_var.set("all")
        
        self.update_sub_categories()
        self.show_current_value()

    def update_sub_categories(self):
        selected_main = self.main_category_var.get()
        if not selected_main:
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        
        try:
            main_value = first_yaml['TestCase'][selected_main]
            if not isinstance(main_value, dict):
                # 如果是简单值，直接从文件中读取保持原始格式
                file_name = next(iter(self.yaml_files.keys()))
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 查找对应的行
                for line in lines:
                    if selected_main in line and ":" in line:
                        prop_in_line = line.split(":")[0].strip()
                        if prop_in_line == selected_main:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break
                
                # 清除并禁用子类别和属性选择
                self.sub_category_combo['values'] = []
                self.property_combo['values'] = []
                self.sub_category_var.set('')
                self.property_var.set('')
                self.sub_category_combo['state'] = 'disabled'
                self.property_combo['state'] = 'disabled'
                return
            else:
                # 如果是字典，处理子类别
                self.sub_category_combo['state'] = 'readonly'
                if selected_main == 'Vehicle':
                    vehicle_data = main_value
                    if self.type_var.get() == "seat":
                        sub_categories = [key for key in vehicle_data.keys() if 'Seat' in key]
                    elif self.type_var.get() == "door":
                        sub_categories = [key for key in vehicle_data.keys() if 'Door' in key or key == 'Tailgate']
                    else:
                        sub_categories = list(vehicle_data.keys())
                else:
                    sub_categories = list(main_value.keys())
                
                self.sub_category_combo['values'] = sub_categories
                self.property_combo['values'] = []
                self.current_value.delete('1.0', tk.END)
                
        except KeyError as e:
            self.status_var.set(f"Error accessing data structure: {str(e)}")
            return

    def on_sub_category_selected(self, event):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        
        if not (selected_main and selected_sub):
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        try:
            sub_value = first_yaml['TestCase'][selected_main][selected_sub]
            
            # 清除之前的选择
            self.property_var.set('')
            self.item_sub_property_var.set('')
            self.property_combo['values'] = []
            self.item_sub_property_combo['state'] = 'disabled'
            
            # 检查是否是简单值
            if not isinstance(sub_value, dict):
                # 如果是简单值，直接显示并禁用属性选择
                file_name = next(iter(self.yaml_files.keys()))
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 查找对应的行
                for line in lines:
                    if selected_sub in line and ":" in line:
                        prop_in_line = line.split(":")[0].strip()
                        if prop_in_line == selected_sub:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break
                
                # 禁用属性选择
                self.property_combo['state'] = 'disabled'
            else:
                # 如果是字典，启用属性选择
                self.property_combo['state'] = 'readonly'
                properties = list(sub_value.keys())
                self.property_combo['values'] = properties
                
                # 如果有OccupancyComment属性，自动选择它
                if 'OccupancyComment' in properties:
                    self.property_var.set('OccupancyComment')
                    self.show_current_value()
        except KeyError as e:
            self.status_var.set(f"Error accessing data structure: {str(e)}")

    def update_properties(self):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        
        if not (selected_main and selected_sub):
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        sub_value = first_yaml['TestCase'][selected_main][selected_sub]
        
        # Check if it's a simple value
        if not isinstance(sub_value, dict):
            # If it's a simple value, display it directly
            file_name = next(iter(self.yaml_files.keys()))
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the corresponding line in the file
            for line in lines:
                if selected_sub in line and ":" in line:
                    prop_in_line = line.split(":")[0].strip()
                    if prop_in_line == selected_sub:
                        # Extract the original value (including quotes)
                        value = line.split(":", 1)[1].strip()
                        self.current_value.delete('1.0', tk.END)
                        self.current_value.insert('1.0', value)
                        break
            
            # Clear and disable property selection
            self.property_combo['values'] = []
            self.property_var.set('')
            self.item_sub_property_combo['state'] = 'disabled'
            self.item_sub_property_var.set('')
            return
        
        # If it's a dictionary, process it as before
        properties = list(sub_value.keys())
        current_prop = self.property_var.get()
        
        self.property_combo['values'] = properties
        if current_prop in properties:
            self.property_combo.set(current_prop)
            if current_prop == "Item":
                current_item_prop = self.item_sub_property_var.get()
                item_properties = list(sub_value['Item'].keys())
                self.item_sub_property_combo['values'] = item_properties
                if current_item_prop in item_properties:
                    self.item_sub_property_combo.set(current_item_prop)

    def on_property_selected(self, event):
        selected_prop = self.property_var.get()
        if selected_prop == "Item":
            # If Item is selected, enable the sub-property selector and set the available values
            self.item_sub_property_combo['state'] = 'readonly'
            first_yaml = next(iter(self.yaml_files.values()))
            selected_main = self.main_category_var.get()
            selected_sub = self.sub_category_var.get()
            item_properties = list(first_yaml['TestCase'][selected_main][selected_sub]['Item'].keys())
            self.item_sub_property_combo['values'] = item_properties
        else:
            # If other properties are selected, disable the sub-property selector and clear the selection
            self.item_sub_property_combo['state'] = 'disabled'
            self.item_sub_property_combo.set('')
            self.show_current_value()

    def on_item_sub_property_selected(self, event):
        self.show_current_value()

    def show_current_value(self):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        selected_prop = self.property_var.get()
        
        if not (selected_main and selected_sub and selected_prop):
            return
        
        file_name = next(iter(self.yaml_files.keys()))
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the start of the sub-category
        sub_start_line = -1
        in_main_category = False
        for i, line in enumerate(lines):
            if selected_main in line and line.strip() == f"{selected_main}:":
                in_main_category = True
                continue
            if in_main_category and selected_sub in line and line.strip() == f"{selected_sub}:":
                sub_start_line = i
                break
        
        if sub_start_line == -1:
            return
        
        if selected_prop == "Item":
            selected_item_prop = self.item_sub_property_var.get()
            if selected_item_prop:
                # Find the Item property within the sub-category
                item_section_found = False
                current_indent = None
                for i in range(sub_start_line, len(lines)):
                    line = lines[i]
                    if not current_indent and line.strip():
                        current_indent = len(line) - len(line.lstrip())
                    if "Item:" in line and line.strip() == "Item:":
                        item_section_found = True
                        continue
                    if item_section_found and selected_item_prop in line:
                        indent = len(line) - len(line.lstrip())
                        if indent > current_indent:  # 确保是Item下的属性
                            prop_in_line = line.split(":")[0].strip()
                            if prop_in_line == selected_item_prop:
                                value = line.split(":", 1)[1].strip()
                                self.current_value.delete('1.0', tk.END)
                                self.current_value.insert('1.0', value)
                                break
                    if i > sub_start_line + 20:  # 防止过度搜索
                        break
        else:
            # 在子类别中查找普通属性
            current_indent = None
            for i in range(sub_start_line, len(lines)):
                line = lines[i]
                if not current_indent and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                if selected_prop in line:
                    indent = len(line) - len(line.lstrip())
                    if indent == current_indent + 2:  # 确保是子类别直接下的属性
                        prop_in_line = line.split(":")[0].strip()
                        if prop_in_line == selected_prop:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break
                if i > sub_start_line + 20:  # 防止过度搜索
                    break

    def update_value(self):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        selected_prop = self.property_var.get()
        selected_item_prop = self.item_sub_property_var.get()
        new_value = self.current_value.get('1.0', 'end-1c')
        
        try:
            for file_name, yaml_data in self.yaml_files.items():
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                
                # 处理简单值（如 TestNotes）
                if not selected_sub:
                    for i, line in enumerate(lines):
                        if line.strip().startswith(f"{selected_main}:"):
                            indent = line[:line.find(selected_main)]
                            lines[i] = f"{indent}{selected_main}: {new_value}\n"
                            yaml_data['TestCase'][selected_main] = new_value
                            modified = True
                            break
                
                # 处理子类别的值
                elif not selected_prop:
                    in_main = False
                    for i, line in enumerate(lines):
                        if not in_main and line.strip() == f"{selected_main}:":
                            in_main = True
                            continue
                        if in_main and selected_sub in line and ":" in line:
                            indent = line[:line.find(selected_sub)]
                            lines[i] = f"{indent}{selected_sub}: {new_value}\n"
                            yaml_data['TestCase'][selected_main][selected_sub] = new_value
                            modified = True
                            break
                
                # 处理属性值
                elif selected_prop and not selected_item_prop:
                    in_main = False
                    in_sub = False
                    for i, line in enumerate(lines):
                        if not in_main and line.strip() == f"{selected_main}:":
                            in_main = True
                            continue
                        if in_main and not in_sub and line.strip() == f"{selected_sub}:":
                            in_sub = True
                            continue
                        if in_sub and selected_prop in line and ":" in line:
                            indent = line[:line.find(selected_prop)]
                            lines[i] = f"{indent}{selected_prop}: {new_value}\n"
                            yaml_data['TestCase'][selected_main][selected_sub][selected_prop] = new_value
                            modified = True
                            break
                
                if modified:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
            
            self.status_var.set("更新成功")
            self.show_current_value()
            
        except Exception as e:
            self.status_var.set(f"更新失败: {str(e)}")

def main():
    root = TkinterDnD.Tk()
    app = YamlEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()