import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import yaml
from typing import Dict, List
from tkinterdnd2 import *
from tkinter import font as tkFont

class YamlEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YAML Editor")
        self.root.geometry("500x400")
        
        # Save the YAML files and the current YAML data
        self.yaml_files = {}
        self.current_yaml_data = None
        
        self.setup_ui()
        
        # bind the text change event
        self.current_value.bind('<KeyRelease>', self.on_text_change)
        
    def setup_ui(self):
        # Create the main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create a frame for folder selection and drop area
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Select folder button
        ttk.Button(folder_frame, text="Choose Folder", command=self.select_folder).grid(row=0, column=0, padx=5)
        
        # Add a text box to display the selected folder path
        self.folder_path_display = tk.Text(folder_frame, height=2, width=50) # 可以调整宽度
        self.folder_path_display.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky=(tk.W, tk.E))

        # Define a smaller font and apply it to the text box
        self.small_font = tkFont.Font(family="TkDefaultFont", size=8)
        self.folder_path_display.config(font=self.small_font)

        self.folder_path_display.config(state='normal')
        self.folder_path_display.insert('1.0', "Selected folder path will appear here")
        self.folder_path_display.configure(state='disabled') # Make it read-only
        
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
        
        # Vehicle replacement button
        ttk.Button(main_frame, text="Batch Vehicle Replacer", command=self.open_vehicle_replacer).grid(row=9, column=0, columnspan=2, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=10, column=0, columnspan=2, pady=5)

    def reset_all_fields(self):
        # Reset all selection fields
        self.main_category_var.set('')
        self.sub_category_var.set('')
        self.property_var.set('')
        self.item_sub_property_var.set('')
        self.type_var.set('all')
        
        # Clear all combobox values
        self.main_category_combo['values'] = []
        self.sub_category_combo['values'] = []
        self.property_combo['values'] = []
        self.item_sub_property_combo['values'] = []
        
        # Disable item property combobox
        self.item_sub_property_combo['state'] = 'disabled'
        
        # Clear current value
        self.current_value.delete('1.0', tk.END)
        
        # Clear the folder path display
        self.folder_path_display.configure(state='normal')
        self.folder_path_display.delete('1.0', tk.END)
        self.folder_path_display.insert('1.0', "Selected folder path will appear here")
        self.folder_path_display.configure(state='disabled')

        # Reset status bar
        self.status_var.set('')
        
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            # Reset all fields before loading new data
            self.reset_all_fields()
            
            self.yaml_files.clear()
            for file in os.listdir(folder):
                if file.endswith('.yaml'):
                    file_path = os.path.join(folder, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                            if yaml_data and 'TestCase' in yaml_data:
                                self.yaml_files[file_path] = yaml_data
                    except Exception as e:
                        print(f"Failed to load {file}: {str(e)}")
            

            if self.yaml_files:
                self.update_main_categories()
                self.status_var.set(f"Loaded {len(self.yaml_files)} YAML files")
                # Update the folder path display
                self.folder_path_display.configure(state='normal') # Enable editing temporarily
                self.folder_path_display.delete('1.0', tk.END)
                self.folder_path_display.insert('1.0', folder) # Insert the selected folder path
                self.folder_path_display.configure(state='disabled') # Set back to read-only
            else:
                self.status_var.set("No valid YAML files found")


    def handle_drop(self, event):
        # Reset all fields before loading new files
        self.reset_all_fields()
        
        files = event.data
        # Split the dropped files string and handle both Windows and Unix paths
        file_paths = [path.strip('{}') for path in files.split(' ')]
        
        self.yaml_files.clear()
        valid_files = 0
        
        for file_path in file_paths:
            if file_path.lower().endswith(('.yaml', '.yml')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                        if yaml_data and 'TestCase' in yaml_data:
                            self.yaml_files[file_path] = yaml_data
                            valid_files += 1
                except Exception as e:
                    print(f"Failed to load {os.path.basename(file_path)}: {str(e)}")
        
        if valid_files > 0:
            self.update_main_categories()
            self.status_var.set(f"Loaded {valid_files} YAML files")
            # Enable the drop area text to show loaded files
            self.drop_area.configure(state='normal')
            self.drop_area.delete('1.0', tk.END)
            self.drop_area.insert('1.0', f"Loaded {valid_files} files:\n" + 
                                "\n".join(os.path.basename(f) for f in self.yaml_files.keys()))
            self.drop_area.configure(state='disabled')
        else:
            self.status_var.set("No valid YAML files found")

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
            self.status_var.set(f"Loaded {len(self.yaml_files)} YAML files")
        else:
            self.status_var.set("No valid YAML files found")



    def load_yaml_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # directly use yaml.load instead of safe_load, because these are our own files
                yaml_data = yaml.load(f, Loader=yaml.Loader)
                if yaml_data and 'TestCase' in yaml_data:
                    self.yaml_files[file_path] = yaml_data

        except Exception as e:
            print(f"Failed to load {os.path.basename(file_path)}: {str(e)}")


    def update_main_categories(self):
        if self.yaml_files:
            first_yaml = next(iter(self.yaml_files.values()))
            main_categories = list(first_yaml['TestCase'].keys())
            self.main_category_combo['values'] = main_categories
            self.status_var.set(f"Loaded {len(self.yaml_files)} YAML files")
        else:
            self.status_var.set("No valid YAML files found")



    def on_main_category_selected(self, event):
        # Reset status bar
        self.status_var.set('')
        
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
                # if it's a simple value, read it directly from the file and keep the original format
                file_name = next(iter(self.yaml_files.keys()))
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # find the corresponding line
                for line in lines:
                    if selected_main in line and ":" in line:
                        prop_in_line = line.split(":")[0].strip()

                        if prop_in_line == selected_main:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break

                # clear and disable the sub-category and property selection
                self.sub_category_combo['values'] = []
                self.property_combo['values'] = []
                self.sub_category_var.set('')
                self.property_var.set('')
                self.sub_category_combo['state'] = 'disabled'
                self.property_combo['state'] = 'disabled'
                return
            else:
                # if it's a dictionary, process the sub-category
                self.sub_category_combo['state'] = 'readonly'
                if selected_main == 'Vehicle':
                    vehicle_data = main_value

                    if self.type_var.get() == "seat":
                        # match all projects with seat attributes (including Dashboard and Trunk)
                        sub_categories = []
                        for key, value in vehicle_data.items():
                            if isinstance(value, dict) and ('SeatPosition' in value or 'OccupancySeat' in value):

                                sub_categories.append(key)
                    elif self.type_var.get() == "door":
                        sub_categories = [key for key in vehicle_data.keys() 
                                       if 'Door' in key or key in ['Tailgate','Hood']]
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
        # Reset status bar
        self.status_var.set('')
        
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        
        if not (selected_main and selected_sub):
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        try:
            sub_value = first_yaml['TestCase'][selected_main][selected_sub]
            
            # clear the previous selection
            self.property_var.set('')
            self.item_sub_property_var.set('')
            self.property_combo['values'] = []
            self.item_sub_property_combo['state'] = 'disabled'
            

            # check if it's a simple value
            if not isinstance(sub_value, dict):
                # if it's a simple value, display it directly and disable property selection
                file_name = next(iter(self.yaml_files.keys()))

                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                
                # find the corresponding line
                for line in lines:
                    if selected_sub in line and ":" in line:
                        prop_in_line = line.split(":")[0].strip()

                        if prop_in_line == selected_sub:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break
                
                # disable property selection
                self.property_combo['state'] = 'disabled'
            else:
                # if it's a dictionary, enable property selection
                self.property_combo['state'] = 'readonly'
                properties = list(sub_value.keys())
                self.property_combo['values'] = properties

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
        # Reset status bar
        self.status_var.set('')
        
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
        # Reset status bar
        self.status_var.set('')
        
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
                        if indent > current_indent:  # make sure it's an Item property
                            prop_in_line = line.split(":")[0].strip()
                            if prop_in_line == selected_item_prop:
                                value_lines = []

                                # get the full content of the first line (including the colon and space)
                                first_line = line.split(":", 1)[1]
                                value_lines.append(first_line.rstrip('\n'))
                                
                                # check the following lines
                                next_line_idx = i + 1
                                while next_line_idx < len(lines):

                                    next_line = lines[next_line_idx]
                                    next_indent = len(next_line) - len(next_line.lstrip())

                                    # if the indent is less than or equal to the indent of the current property, it means the next property is found
                                    if next_indent <= indent:
                                        break

                                    # add the original line (keep the space and newline)
                                    value_lines.append(next_line.rstrip('\n'))
                                    next_line_idx += 1

                                # merge all lines and display
                                self.current_value.delete('1.0', tk.END)
                                self.current_value.insert('1.0', '\n'.join(value_lines))
                                break

                    if i > sub_start_line + 20:  # prevent excessive search
                        break
        else:

            # find the normal property in the sub-category
            current_indent = None
            for i in range(sub_start_line, len(lines)):
                line = lines[i]

                if not current_indent and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                if selected_prop in line:
                    indent = len(line) - len(line.lstrip())
                    if indent == current_indent + 2:  # make sure it's a property under the sub-category
                        prop_in_line = line.split(":")[0].strip()
                        if prop_in_line == selected_prop:

                            # get the full value (including all subsequent lines)
                            value_lines = []
                            # get the value of the first line (including all content after the colon, but not including the property name and colon)
                            colon_pos = line.find(':')
                            if colon_pos != -1:

                                first_line = line[colon_pos + 1:].rstrip('\n')  # keep all content after the colon
                                value_lines.append(first_line)
                            
                            # check the following lines
                            next_line_idx = i + 1
                            last_content_line = i  # record the last line with content
                            empty_lines_count = 0  # count the number of empty lines
                            

                            while next_line_idx < len(lines):
                                next_line = lines[next_line_idx].rstrip('\n')
                                if next_line.strip():  # if it's a non-empty line
                                    next_indent = len(next_line) - len(next_line.lstrip())

                                    if next_indent <= indent:  # if the indent is less than or equal to the indent of the current property, it means the next property is found
                                        break
                                    value_lines.append(next_line)

                                    last_content_line = next_line_idx
                                    empty_lines_count = 0  # reset the count of empty lines
                                else:  # if it's an empty line
                                    if empty_lines_count < 10:  # limit the number of empty lines to 10
                                        value_lines.append(next_line)

                                        empty_lines_count += 1
                                    else:
                                        break
                                next_line_idx += 1

                            # merge all lines and display (keep the original format)
                            full_content = '\n'.join(value_lines)
                            if not full_content.endswith('\n'):
                                full_content += '\n'  # make sure there is a newline at the end
                            
                            
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', full_content)
                            break

    def update_value(self):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        selected_prop = self.property_var.get()
        selected_item_prop = self.item_sub_property_var.get()

        # 获取当前文本框内容，并合并为一行
        new_value_text = self.current_value.get('1.0', 'end-1c')
        new_value_single_line = ' '.join([line.strip() for line in new_value_text.splitlines() if line.strip()])

        try:
            for file_name, yaml_data in self.yaml_files.items():
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # === 插入主分类简单值处理 ===
                if selected_main and not selected_sub and not selected_prop and not selected_item_prop:
                    for i, line in enumerate(lines):
                        if line.strip().startswith(f"{selected_main}:"):
                            indent = len(line) - len(line.lstrip())
                            indent_str = ' ' * indent
                            lines[i] = f"{indent_str}{selected_main}: {new_value_single_line}\n"
                            break
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    yaml_data['TestCase'][selected_main] = new_value_single_line
                    continue  # 处理下一个文件

                modified = False
                prop_line_index = -1
                prop_indent = -1
                value_end_index = -1
                target_prop_name = None

                # 1. 确定目标属性名
                if not selected_sub:
                    target_prop_name = selected_main
                elif selected_sub and not selected_prop:
                    target_prop_name = selected_sub
                elif selected_prop:
                    target_prop_name = selected_item_prop if selected_prop == "Item" else selected_prop

                # 2. 找到目标属性行和缩进
                in_main = in_sub = in_item = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    indent = len(line) - len(stripped)
                    if selected_main and stripped == f"{selected_main}:":
                        in_main = True
                        in_sub = False
                        in_item = False
                        continue
                    if in_main and selected_sub and stripped == f"{selected_sub}:":
                        in_sub = True
                        in_item = False
                        continue
                    if in_sub and selected_prop == "Item" and stripped == "Item:":
                        in_item = True
                        continue

                    # 找到目标属性行
                    if (
                        (selected_prop == "Item" and in_item and stripped.startswith(f"{target_prop_name}:")) or
                        (selected_prop != "Item" and in_sub and stripped.startswith(f"{target_prop_name}:"))
                    ):
                        prop_line_index = i
                        prop_indent = indent
                        break
                    # 兼容主分类和子分类直接是简单值的情况
                    if not selected_prop and not selected_item_prop and (
                        (in_main and not in_sub and stripped.startswith(f"{target_prop_name}:")) or
                        (in_sub and stripped.startswith(f"{target_prop_name}:"))
                    ):
                        prop_line_index = i
                        prop_indent = indent
                        break

                if prop_line_index == -1:
                    continue  # 没找到属性，跳过

                # 3. 找到该属性下所有属于它的多行内容
                value_start = prop_line_index
                value_end = prop_line_index
                for j in range(prop_line_index + 1, len(lines)):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    next_indent = len(next_line) - len(next_stripped)
                    if next_stripped == "":
                        value_end = j  # 空行也算
                        continue
                    if next_indent <= prop_indent:
                        break
                    value_end = j

                # 4. 构建新内容
                colon_pos = lines[prop_line_index].find(':')
                line_prefix = lines[prop_line_index][:colon_pos + 1] + ' '
                new_property_line = f"{line_prefix}{new_value_single_line}\n"
                new_lines = lines[:prop_line_index] + [new_property_line] + lines[value_end + 1:]

                # 5. 写回文件
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                modified = True

                # 6. 更新内存数据
                try:
                    if selected_main:
                        if not selected_sub:
                            yaml_data['TestCase'][selected_main] = new_value_single_line
                        elif selected_sub:
                            if not selected_prop:
                                yaml_data['TestCase'][selected_main][selected_sub] = new_value_single_line
                            elif selected_prop == "Item" and selected_item_prop:
                                yaml_data['TestCase'][selected_main][selected_sub][selected_prop][selected_item_prop] = new_value_single_line
                            elif selected_prop != "Item":
                                yaml_data['TestCase'][selected_main][selected_sub][selected_prop] = new_value_single_line
                except Exception as e:
                    print(f"Warning: Failed to update in-memory YAML data for {file_name}: {e}")

            self.status_var.set("Update successfully")
        except Exception as e:
            self.status_var.set(f"Update failed: {str(e)}")

    def on_text_change(self, event=None):
        # no longer limit the editing behavior, allow free editing of multi-line content
        pass
    
    def open_vehicle_replacer(self):
        """Open Vehicle Content Replacer"""
        try:
            from vehicle_replacer import BatchVehicleReplacerGUI
            replacer_window = tk.Toplevel(self.root)
            BatchVehicleReplacerGUI(replacer_window)
        except ImportError as e:
            messagebox.showerror("Error", f"Cannot import Vehicle replacer module: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Vehicle replacer: {str(e)}")


def main():
    root = TkinterDnD.Tk()
    app = YamlEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()