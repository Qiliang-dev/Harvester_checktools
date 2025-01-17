from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import Qt
import sys
import os
import yaml
from View.Template.yamlchange_ui import Ui_Form

class YamlEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # 保存YAML文件和数据
        self.yaml_files = {}
        
        # 设置按钮连接
        self.ui.pushButton.clicked.connect(self.select_folder)
        self.ui.pushButton_2.clicked.connect(self.update_value)
        
        # 设置下拉框事件
        self.ui.comboBox_1.currentIndexChanged.connect(self.on_main_category_selected)
        self.ui.comboBox_2.currentIndexChanged.connect(self.on_sub_category_selected)
        self.ui.comboBox_3.currentIndexChanged.connect(self.on_property_selected)
        self.ui.comboBox_4.currentIndexChanged.connect(self.on_item_sub_property_selected)
        
        # 禁用Item属性下拉框
        self.ui.comboBox_4.setEnabled(False)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.yaml_files.clear()
            for file in os.listdir(folder_path):
                if file.endswith('.yaml'):
                    file_path = os.path.join(folder_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            yaml_data = yaml.safe_load(f)
                            if yaml_data and 'TestCase' in yaml_data:
                                self.yaml_files[file_path] = yaml_data
                    except Exception as e:
                        print(f"Error loading {file}: {str(e)}")
            
            if self.yaml_files:
                first_yaml = next(iter(self.yaml_files.values()))
                main_categories = list(first_yaml['TestCase'].keys())
                self.ui.comboBox_1.clear()
                self.ui.comboBox_1.addItems(main_categories)

    def on_main_category_selected(self, index):
        # Clear all sub-level selections
        self.ui.comboBox_2.clear()
        self.ui.comboBox_3.clear()
        self.ui.comboBox_4.clear()
        self.ui.textEdit_2.clear()
        
        # Disable Item property combobox
        self.ui.comboBox_4.setEnabled(False)
        
        selected = self.ui.comboBox_1.currentText()
        
        if selected == 'Vehicle':
            # TODO: 处理Vehicle的radio buttons
            # 这部分需要在UI文件中添加radio buttons
            pass
        
        self.update_sub_categories()

    def update_sub_categories(self):
        selected_main = self.ui.comboBox_1.currentText()
        if not selected_main:
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        sub_categories = []
        
        try:
            if selected_main == 'Vehicle':
                vehicle_data = first_yaml['TestCase']['Vehicle']
                if self.type_var.get() == "seat":
                    sub_categories = [key for key in vehicle_data.keys() if 'Seat' in key]
                elif self.type_var.get() == "door":
                    sub_categories = [key for key in vehicle_data.keys() if 'Door' in key or key == 'Tailgate']
                else:
                    sub_categories = list(vehicle_data.keys())
            else:
                # Check the type of the value
                main_value = first_yaml['TestCase'][selected_main]
                if isinstance(main_value, dict):
                    sub_categories = list(main_value.keys())
                else:
                    # If it's a simple value, display it directly
                    self.current_value.delete('1.0', tk.END)
                    self.current_value.insert('1.0', str(main_value))
                    return
        except KeyError as e:
            self.status_var.set(f"Error accessing data structure: {str(e)}")
            return
        
        self.sub_category_combo['values'] = sub_categories
        self.property_combo['values'] = []
        self.current_value.delete('1.0', tk.END)

    def on_sub_category_selected(self, event):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        selected_prop = self.property_var.get()
        selected_item_prop = self.item_sub_property_var.get()
        
        if not (selected_main and selected_sub):
            return
        
        first_yaml = next(iter(self.yaml_files.values()))
        sub_value = first_yaml['TestCase'][selected_main][selected_sub]
        
        # Check if it's a simple value
        if not isinstance(sub_value, dict):
            # If it's a simple value, display it directly and disable property selection
            file_name = next(iter(self.yaml_files.keys()))
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the corresponding line in the file
            for line in lines:
                if selected_sub in line and ":" in line:
                    prop_in_line = line.split(":")[0].strip()
                    if prop_in_line == selected_sub:
                        value = line.split(":", 1)[1].strip()
                        self.current_value.delete('1.0', tk.END)
                        self.current_value.insert('1.0', value)
                        break
            
            # Disable property selection
            self.property_combo['values'] = []
            self.property_var.set('')
            self.item_sub_property_combo['state'] = 'disabled'
            self.item_sub_property_var.set('')
        else:
            # If it's a dictionary, update the property list and keep the current selection
            properties = list(sub_value.keys())
            self.property_combo['values'] = properties
            
            # If the currently selected property exists in the new list, keep it selected and update the value
            if selected_prop in properties:
                if selected_prop == "Item" and selected_item_prop:
                    if "Item" in sub_value and selected_item_prop in sub_value["Item"]:
                        self.show_current_value()  # Update the current value display
                elif selected_prop:
                    self.show_current_value()  # Update the current value display

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
        for i, line in enumerate(lines):
            if f"{selected_sub}:" in line and line.strip() == f"{selected_sub}:":
                sub_start_line = i
                break
        
        if sub_start_line == -1:
            return
        
        if selected_prop == "Item":
            selected_item_prop = self.item_sub_property_var.get()
            if selected_item_prop:
                # Find the Item property within the sub-category
                item_section_found = False
                for i in range(sub_start_line, len(lines)):
                    line = lines[i]
                    if "Item:" in line and line.strip() == "Item:":
                        item_section_found = True
                        continue
                    if item_section_found and selected_item_prop in line and ":" in line:
                        prop_in_line = line.split(":")[0].strip()
                        if prop_in_line == selected_item_prop:
                            value = line.split(":", 1)[1].strip()
                            self.current_value.delete('1.0', tk.END)
                            self.current_value.insert('1.0', value)
                            break
                    if i > sub_start_line + 10:  # Prevent excessive search
                        break
        else:
            # Find the normal property within the sub-category
            for i in range(sub_start_line, len(lines)):
                line = lines[i]
                if selected_prop in line and ":" in line:
                    prop_in_line = line.split(":")[0].strip()
                    if prop_in_line == selected_prop:
                        value = line.split(":", 1)[1].strip()
                        self.current_value.delete('1.0', tk.END)
                        self.current_value.insert('1.0', value)
                        break
                if i > sub_start_line + 10:  # Prevent excessive search
                    break

    def update_value(self):
        selected_main = self.main_category_var.get()
        selected_sub = self.sub_category_var.get()
        selected_prop = self.property_var.get()
        new_value = self.current_value.get('1.0', 'end-1c')
        
        try:
            for file_name, yaml_data in self.yaml_files.items():
                # Read the file content
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if selected_prop == "Item":
                    selected_item_prop = self.item_sub_property_var.get()
                    if not selected_item_prop:
                        self.status_var.set("Please select the specific property of Item")
                        return
                    
                    # Find the line to modify
                    target_line = None
                    indent = ""
                    for i, line in enumerate(lines):
                        if selected_item_prop in line and ":" in line:
                            prop_in_line = line.split(":")[0].strip()
                            if prop_in_line == selected_item_prop:
                                target_line = i
                                indent = line[:line.find(selected_item_prop)]
                                break
                else:
                    # Find the line to modify
                    target_line = None
                    indent = ""
                    for i, line in enumerate(lines):
                        if selected_prop in line and ":" in line:
                            prop_in_line = line.split(":")[0].strip()
                            if prop_in_line == selected_prop:
                                target_line = i
                                indent = line[:line.find(selected_prop)]
                                break
                
                if target_line is not None:
                    # Determine how to format based on the value type
                    if new_value.lower() == 'null':
                        formatted_value = 'null'
                    elif new_value.isdigit():
                        formatted_value = new_value
                    elif new_value.lower() == 'true' or new_value.lower() == 'false':
                        formatted_value = new_value.lower()
                    else:
                        formatted_value = new_value  # Keep the original format
                    
                    # Update the line
                    if selected_prop == "Item":
                        lines[target_line] = f"{indent}{selected_item_prop}: {formatted_value}\n"
                        yaml_data['TestCase'][selected_main][selected_sub][selected_prop][selected_item_prop] = formatted_value
                    else:
                        lines[target_line] = f"{indent}{selected_prop}: {formatted_value}\n"
                        yaml_data['TestCase'][selected_main][selected_sub][selected_prop] = formatted_value
                    
                    # Write back to the file
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
            
            self.status_var.set("Update successful")
        except Exception as e:
            self.status_var.set(f"Update failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = YamlEditorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()