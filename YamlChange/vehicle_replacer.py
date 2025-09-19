#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Vehicle Content Replacer for YAML Files
Tool for batch replacing Vehicle content in YAML files using a template file
"""

import os
import yaml
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Optional, Tuple
import shutil
from datetime import datetime
import re


class BatchVehicleReplacer:
    """Batch Vehicle Content Replacer"""
    
    def __init__(self):
        self.template_file = None
        self.target_files = []
        self.template_vehicle_data = None
        self.processing_results = []
    
    def load_yaml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """加载YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if data and 'TestCase' in data and 'Vehicle' in data['TestCase']:
                    return data
                else:
                    raise ValueError("Invalid file format: missing TestCase or Vehicle node")
        except Exception as e:
            raise Exception(f"Failed to load file: {str(e)}")
    
    def extract_vehicle_content(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Vehicle content from YAML data"""
        return yaml_data['TestCase']['Vehicle']
    
    def extract_vehicle_suffix(self, filename: str) -> str:
        """Extract vehicle suffix (e.g., H022296_E) from filename"""
        # Pattern: (_[A-Z]{1,2}\d{5,6})_([A-Z])(?=\.yaml$)
        # Examples: _H022296_E, _DA00097_A
        pattern = r'(_[A-Z]{1,2}\d{5,6})_([A-Z])(?=\.yaml$)'
        match = re.search(pattern, filename)
        
        if match:
            vehicle_code = match.group(1)[1:]  # Remove leading underscore
            version_letter = match.group(2)
            return f"{vehicle_code}_{version_letter}"
        else:
            raise ValueError(f"Invalid filename format: {filename}. Expected format: YYYY_MM_DD_HHMMSS_VEHICLECODE_VERSION.yaml")
    
    def validate_filename_format(self, filename: str) -> bool:
        """Validate if filename follows the expected format"""
        pattern = r'^\d{4}_\d{2}_\d{2}_\d{6}_[A-Z]{1,2}\d{5,6}_[A-Z]\.yaml$'
        return bool(re.match(pattern, filename))
    
    def generate_new_filename(self, original_filename: str, new_suffix: str) -> str:
        """Generate new filename by replacing vehicle suffix"""
        # Extract the timestamp prefix and replace the suffix
        pattern = r'^(\d{4}_\d{2}_\d{2}_\d{6})_[A-Z]{1,2}\d{5,6}_[A-Z](\.yaml)$'
        match = re.match(pattern, original_filename)
        
        if not match:
            raise ValueError(f"Cannot parse filename: {original_filename}")
        
        timestamp_prefix = match.group(1)
        extension = match.group(2)
        
        new_filename = f"{timestamp_prefix}_{new_suffix}{extension}"
        return new_filename
    
    def handle_filename_conflict(self, target_path: str) -> str:
        """Handle filename conflicts by adding timestamp"""
        if not os.path.exists(target_path):
            return target_path
        
        # Add timestamp to avoid conflict
        directory = os.path.dirname(target_path)
        filename = os.path.basename(target_path)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%H%M%S")
        
        new_filename = f"{name}_copy_{timestamp}{ext}"
        new_path = os.path.join(directory, new_filename)
        
        return new_path
    
    def update_testcase_fields(self, yaml_data: Dict[str, Any], new_filename_without_ext: str) -> None:
        """Update TestCase.Name and TestCase.Filename fields"""
        if 'TestCase' in yaml_data:
            # Update Name field (without extension)
            yaml_data['TestCase']['Name'] = new_filename_without_ext
            
            # Update Filename field (with .blf extension)
            yaml_data['TestCase']['Filename'] = f"{new_filename_without_ext}.blf"
    
    def replace_vehicle_content(self, target_file_path: str, source_vehicle_data: Dict[str, Any]) -> bool:
        """Replace Vehicle content in target file"""
        try:
            # Create backup
            backup_path = self.create_backup(target_file_path)
            print(f"Backup created: {backup_path}")
            
            # Read target file
            with open(target_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find Vehicle section start and end positions
            vehicle_start = -1
            vehicle_end = -1
            vehicle_indent = ""
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped == "Vehicle:":
                    vehicle_start = i
                    vehicle_indent = line[:line.find('Vehicle:')]
                    break
            
            if vehicle_start == -1:
                raise ValueError("Vehicle node not found")
            
            # Find Vehicle node end position
            # Determine Vehicle block end by checking indentation
            base_indent_len = len(vehicle_indent)
            
            for i in range(vehicle_start + 1, len(lines)):
                line = lines[i]
                if line.strip():  # 非空行
                    current_indent_len = len(line) - len(line.lstrip())
                    if current_indent_len <= base_indent_len:
                        vehicle_end = i - 1
                        break
            
            if vehicle_end == -1:
                vehicle_end = len(lines) - 1
            
            # Generate new Vehicle YAML content
            new_vehicle_yaml = self.generate_vehicle_yaml(source_vehicle_data, vehicle_indent + "  ")
            
            # Build new file content
            new_lines = (
                lines[:vehicle_start + 1] +  # Content before Vehicle: line (including Vehicle: line)
                new_vehicle_yaml +           # New Vehicle content
                lines[vehicle_end + 1:]      # Content after Vehicle block
            )
            
            # Write new content
            with open(target_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
            
        except Exception as e:
            # If error occurs, try to restore backup
            if 'backup_path' in locals():
                shutil.copy2(backup_path, target_file_path)
            raise Exception(f"Replacement failed: {str(e)}")
    
    def generate_vehicle_yaml(self, vehicle_data: Dict[str, Any], base_indent: str) -> list:
        """Generate Vehicle section YAML content"""
        lines = []
        
        def add_dict_content(data: Dict[str, Any], indent: str):
            for key, value in data.items():
                formatted_key = self.format_yaml_key(key)
                if isinstance(value, dict):
                    lines.append(f"{indent}{formatted_key}:\n")
                    add_dict_content(value, indent + "  ")
                elif isinstance(value, list):
                    lines.append(f"{indent}{formatted_key}:\n")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"{indent}  -\n")
                            add_dict_content(item, indent + "    ")
                        else:
                            lines.append(f"{indent}  - {self.format_yaml_value(item)}\n")
                else:
                    lines.append(f"{indent}{formatted_key}: {self.format_yaml_value(value)}\n")
        
        add_dict_content(vehicle_data, base_indent)
        return lines
    
    def format_yaml_key(self, key: str) -> str:
        """Format YAML key with proper escaping if needed"""
        # Characters that require quoting in YAML keys
        special_chars = ['*', '&', '!', '|', '>', '%', '@', '`', ' ', ':', '"', "'", '\n', '\t', '[', ']', '{', '}', ',']
        
        # Check if key needs quoting
        needs_quotes = (
            any(char in key for char in special_chars) or
            key.startswith(('-', '?', ':', '@', '`')) or
            key in ['true', 'false', 'null', 'True', 'False', 'Null', 'NULL'] or
            (key.replace('.', '').replace('-', '').isdigit())  # Numeric-like keys
        )
        
        if needs_quotes:
            # Choose appropriate quote type
            if '"' not in key:
                return f'"{key}"'
            elif "'" not in key:
                return f"'{key}'"
            else:
                # Escape double quotes
                escaped_key = key.replace('"', '\\"')
                return f'"{escaped_key}"'
        
        return key
    
    def format_yaml_value(self, value: Any) -> str:
        """Format YAML value"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, str):
            # If string contains special characters, add quotes
            if any(char in value for char in [' ', ':', '"', "'", '\n', '\t']) and not (value.startswith('"') and value.endswith('"')):
                return f'"{value}"' if '"' not in value else f"'{value}'"
            return value
        else:
            return str(value)
    
    def create_backup(self, file_path: str) -> str:
        """Create file backup in yaml_backup folder within the same directory as the target file"""
        # Get the directory where the target file is located
        file_dir = os.path.dirname(file_path)
        backup_dir = os.path.join(file_dir, "yaml_backup")
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            print(f"Created backup directory: {backup_dir}")
        
        # Get just the filename from the full path
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, filename)
        
        # If backup already exists, add timestamp to avoid overwrite
        if os.path.exists(backup_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def replace_vehicle_with_renaming(self, target_file_path: str, source_vehicle_data: Dict[str, Any], new_vehicle_suffix: str) -> Tuple[str, str]:
        """Replace Vehicle content and rename file with new vehicle suffix"""
        try:
            # Validate target filename format
            target_filename = os.path.basename(target_file_path)
            if not self.validate_filename_format(target_filename):
                raise ValueError(f"Target file has invalid format: {target_filename}")
            
            # Create backup
            backup_path = self.create_backup(target_file_path)
            print(f"Backup created: {backup_path}")
            
            # Generate new filename
            new_filename = self.generate_new_filename(target_filename, new_vehicle_suffix)
            new_file_path = os.path.join(os.path.dirname(target_file_path), new_filename)
            
            # Handle filename conflicts
            new_file_path = self.handle_filename_conflict(new_file_path)
            new_filename = os.path.basename(new_file_path)
            
            # Load and modify YAML content
            with open(target_file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.load(f, Loader=yaml.FullLoader)
            
            # Replace Vehicle content
            yaml_data['TestCase']['Vehicle'] = source_vehicle_data
            
            # Update TestCase fields
            new_filename_without_ext = os.path.splitext(new_filename)[0]
            self.update_testcase_fields(yaml_data, new_filename_without_ext)
            
            # Write to new file using the original replace_vehicle_content method for formatting consistency
            self.write_updated_yaml_file(new_file_path, yaml_data, source_vehicle_data)
            
            # Remove original file if new filename is different
            if new_file_path != target_file_path:
                os.remove(target_file_path)
                print(f"Original file removed: {target_filename}")
                print(f"New file created: {new_filename}")
            else:
                print(f"File updated in place: {new_filename}")
            
            return new_file_path, new_filename
            
        except Exception as e:
            # If error occurs, try to restore backup if it exists
            if 'backup_path' in locals() and os.path.exists(backup_path):
                if os.path.exists(target_file_path):
                    os.remove(target_file_path)
                shutil.copy2(backup_path, target_file_path)
            raise Exception(f"Enhanced replacement failed: {str(e)}")
    
    def write_updated_yaml_file(self, file_path: str, yaml_data: Dict[str, Any], vehicle_data: Dict[str, Any]) -> None:
        """Write updated YAML file with proper formatting"""
        # First write the YAML data with basic dump
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Then read back and replace the Vehicle section with proper formatting
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and replace Vehicle section
        vehicle_start = -1
        vehicle_end = -1
        vehicle_indent = ""
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "Vehicle:":
                vehicle_start = i
                vehicle_indent = line[:line.find('Vehicle:')]
                break
        
        if vehicle_start != -1:
            # Find Vehicle section end
            base_indent_len = len(vehicle_indent)
            for i in range(vehicle_start + 1, len(lines)):
                line = lines[i]
                if line.strip():
                    current_indent_len = len(line) - len(line.lstrip())
                    if current_indent_len <= base_indent_len:
                        vehicle_end = i - 1
                        break
            
            if vehicle_end == -1:
                vehicle_end = len(lines) - 1
            
            # Generate new Vehicle YAML content
            new_vehicle_yaml = self.generate_vehicle_yaml(vehicle_data, vehicle_indent + "  ")
            
            # Replace Vehicle section
            new_lines = (
                lines[:vehicle_start + 1] +
                new_vehicle_yaml +
                lines[vehicle_end + 1:]
            )
            
            # Write the final result
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    
    def perform_batch_replacement(self, template_file_path: str, target_file_paths: list, progress_callback=None) -> list:
        """Execute enhanced batch replacement operation with file renaming"""
        self.processing_results = []
        
        try:
            # Load template file and extract vehicle suffix
            template_data = self.load_yaml_file(template_file_path)
            template_vehicle = self.extract_vehicle_content(template_data)
            
            template_filename = os.path.basename(template_file_path)
            template_vehicle_suffix = self.extract_vehicle_suffix(template_filename)
            
            total_files = len(target_file_paths)
            
            self.log_operation(f"Template vehicle suffix: {template_vehicle_suffix}")
            self.log_operation(f"Processing {total_files} target files...")
            
            for i, target_file_path in enumerate(target_file_paths):
                try:
                    # Update progress
                    if progress_callback:
                        progress_callback(i, total_files, os.path.basename(target_file_path))
                    
                    target_filename = os.path.basename(target_file_path)
                    
                    # Validate target file format
                    if not self.validate_filename_format(target_filename):
                        raise ValueError(f"Invalid filename format: {target_filename}")
                    
                    # Validate target file content
                    target_data = self.load_yaml_file(target_file_path)
                    
                    # Execute enhanced replacement with renaming
                    new_file_path, new_filename = self.replace_vehicle_with_renaming(
                        target_file_path, template_vehicle, template_vehicle_suffix
                    )
                    
                    result = {
                        'file': target_filename,
                        'new_file': new_filename,
                        'status': 'Success',
                        'message': f"Vehicle replaced and file renamed to {new_filename}"
                    }
                    
                except Exception as e:
                    result = {
                        'file': os.path.basename(target_file_path),
                        'new_file': None,
                        'status': 'Failed',
                        'message': str(e)
                    }
                
                self.processing_results.append(result)
            
            # Final progress update
            if progress_callback:
                progress_callback(total_files, total_files, "Enhanced batch processing completed")
            
            return self.processing_results
            
        except Exception as e:
            error_result = {
                'file': 'Template',
                'new_file': None,
                'status': 'Failed',
                'message': f"Template file error: {str(e)}"
            }
            self.processing_results.append(error_result)
            return self.processing_results
    
    def log_operation(self, message: str):
        """Log operation message (can be overridden by GUI)"""
        print(message)


class BatchVehicleReplacerGUI:
    """Batch Vehicle Replacer Graphical User Interface"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Vehicle Content Replacer - YAML Vehicle Content Batch Replacement Tool")
        self.root.geometry("800x600")
        
        self.replacer = BatchVehicleReplacer()
        # Override the log_operation method to use GUI logging
        self.replacer.log_operation = self.log_message
        self.template_file_path = None
        self.target_file_paths = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup User Interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Batch Vehicle Content Replacer", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Replace Vehicle content in multiple YAML files using a template file",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Template file selection
        ttk.Label(main_frame, text="Template File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.template_file_var = tk.StringVar()
        self.template_entry = ttk.Entry(main_frame, textvariable=self.template_file_var, width=60)
        self.template_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_template_file).grid(row=2, column=2, pady=5)
        
        # Target files selection
        ttk.Label(main_frame, text="Target Files:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Target files frame
        target_frame = ttk.Frame(main_frame)
        target_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Target files listbox with scrollbar
        listbox_frame = ttk.Frame(target_frame)
        listbox_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.target_listbox = tk.Listbox(listbox_frame, height=6, width=70)
        target_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.target_listbox.yview)
        self.target_listbox.configure(yscrollcommand=target_scrollbar.set)
        
        self.target_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        target_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Target files buttons
        button_frame = ttk.Frame(target_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add Files", command=self.add_target_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Add Folder", command=self.add_target_folder).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_files).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all_files).grid(row=0, column=3, padx=5)
        
        # Operation buttons
        operation_frame = ttk.Frame(main_frame)
        operation_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(operation_frame, text="Preview Template", command=self.preview_template).grid(row=0, column=0, padx=5)
        ttk.Button(operation_frame, text="Start Batch Replace", command=self.start_batch_replacement).grid(row=0, column=1, padx=5)
        ttk.Button(operation_frame, text="Quick Setup (Austauchen)", command=self.quick_setup_austauchen).grid(row=0, column=2, padx=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Results display area
        ttk.Label(main_frame, text="Operation Log:").grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        
        # Create text box and scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.result_text = tk.Text(text_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure weights for window resizing
        main_frame.rowconfigure(9, weight=1)
        main_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
    
    def select_template_file(self):
        """Select template file"""
        file_path = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            initialdir="Austauchen"
        )
        if file_path:
            self.template_file_path = file_path
            self.template_file_var.set(file_path)
            self.log_message(f"Template file selected: {os.path.basename(file_path)}")
    
    def add_target_files(self):
        """Add target files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Target Files",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            initialdir="Austauchen"
        )
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.target_file_paths:
                    self.target_file_paths.append(file_path)
                    self.target_listbox.insert(tk.END, os.path.basename(file_path))
            self.log_message(f"Added {len(file_paths)} target files")
    
    def add_target_folder(self):
        """Add all YAML files from a folder"""
        folder_path = filedialog.askdirectory(
            title="Select Folder with Target Files",
            initialdir="Austauchen"
        )
        if folder_path:
            yaml_files = []
            for file in os.listdir(folder_path):
                if file.endswith('.yaml'):
                    file_path = os.path.join(folder_path, file)
                    if file_path not in self.target_file_paths:
                        yaml_files.append(file_path)
                        self.target_file_paths.append(file_path)
                        self.target_listbox.insert(tk.END, os.path.basename(file_path))
            self.log_message(f"Added {len(yaml_files)} files from folder: {os.path.basename(folder_path)}")
    
    def remove_selected_files(self):
        """Remove selected files from the list"""
        selected_indices = self.target_listbox.curselection()
        if selected_indices:
            # Remove in reverse order to maintain indices
            for index in reversed(selected_indices):
                self.target_listbox.delete(index)
                del self.target_file_paths[index]
            self.log_message(f"Removed {len(selected_indices)} files")
    
    def clear_all_files(self):
        """Clear all target files"""
        self.target_listbox.delete(0, tk.END)
        self.target_file_paths.clear()
        self.log_message("Cleared all target files")
    
    def quick_setup_austauchen(self):
        """Quick setup using Austauchen folder"""
        austauchen_dir = "Austauchen"
        if not os.path.exists(austauchen_dir):
            self.log_message("Error: Austauchen folder not found")
            return
        
        # Find template file (H022296)
        template_file = None
        target_files = []
        
        for file in os.listdir(austauchen_dir):
            if file.endswith('.yaml'):
                file_path = os.path.join(austauchen_dir, file)
                if 'H022296' in file:
                    template_file = file_path
                else:
                    target_files.append(file_path)
        
        if not template_file:
            self.log_message("Error: Template file (H022296) not found in Austauchen folder")
            return
        
        if not target_files:
            self.log_message("Error: No target files found in Austauchen folder")
            return
        
        # Set template file
        self.template_file_path = template_file
        self.template_file_var.set(template_file)
        
        # Clear and set target files
        self.clear_all_files()
        self.target_file_paths = target_files
        for file_path in target_files:
            self.target_listbox.insert(tk.END, os.path.basename(file_path))
        
        self.log_message(f"Quick setup completed:")
        self.log_message(f"  Template file: {os.path.basename(template_file)}")
        self.log_message(f"  Target files: {len(target_files)} files")
    
    def preview_template(self):
        """Preview template file content"""
        if not self.template_file_path:
            messagebox.showwarning("Warning", "Please select a template file first")
            return
        
        try:
            template_data = self.replacer.load_yaml_file(self.template_file_path)
            template_vehicle = self.replacer.extract_vehicle_content(template_data)
            
            self.log_message("=== Template Preview ===")
            self.log_message(f"Template file: {os.path.basename(self.template_file_path)}")
            self.log_message("")
            
            # Show template content summary
            self.log_message("Vehicle sections in template:")
            for section in template_vehicle.keys():
                if section == "OptionalEquipment" and isinstance(template_vehicle[section], dict):
                    self.log_message(f"  {section}: {len(template_vehicle[section])} items")
                elif isinstance(template_vehicle[section], dict):
                    self.log_message(f"  {section}: {len(template_vehicle[section])} sub-items")
                else:
                    self.log_message(f"  {section}: {template_vehicle[section]}")
            
            self.log_message("")
            self.log_message("This Vehicle content will be applied to all target files")
            
        except Exception as e:
            self.log_message(f"Preview failed: {str(e)}")
    
    def compare_sections(self, source: dict, target: dict, section_name: str):
        """比较特定部分的差异"""
        self.log_message(f"--- {section_name} 部分差异 ---")
        
        if section_name not in source and section_name not in target:
            self.log_message(f"  两个文件都没有{section_name}部分")
            return
        
        if section_name not in source:
            self.log_message(f"  源文件缺少{section_name}部分")
            return
        
        if section_name not in target:
            self.log_message(f"  目标文件缺少{section_name}部分")
            return
        
        source_section = source[section_name]
        target_section = target[section_name]
        
        if section_name == "OptionalEquipment":
            source_keys = set(source_section.keys()) if isinstance(source_section, dict) else set()
            target_keys = set(target_section.keys()) if isinstance(target_section, dict) else set()
            
            only_in_source = source_keys - target_keys
            only_in_target = target_keys - source_keys
            
            self.log_message(f"  源文件独有装备: {len(only_in_source)}个")
            for key in sorted(only_in_source):
                name = source_section[key].get('Name', 'Unknown') if isinstance(source_section[key], dict) else ''
                self.log_message(f"    {key}: {name}")
            
            self.log_message(f"  目标文件独有装备: {len(only_in_target)}个")
            for key in sorted(only_in_target):
                name = target_section[key].get('Name', 'Unknown') if isinstance(target_section[key], dict) else ''
                self.log_message(f"    {key}: {name}")
        
        elif section_name == "CarModel":
            for key in ["Model", "Variant", "VIN", "RHD"]:
                if key in source_section and key in target_section:
                    if source_section[key] != target_section[key]:
                        self.log_message(f"  {key}: {target_section[key]} -> {source_section[key]}")
                elif key in source_section:
                    self.log_message(f"  {key}: (新增) -> {source_section[key]}")
                elif key in target_section:
                    self.log_message(f"  {key}: {target_section[key]} -> (删除)")
        
        elif section_name == "Engine":
            for key in ["State", "Type"]:
                if key in source_section and key in target_section:
                    if source_section[key] != target_section[key]:
                        self.log_message(f"  {key}: {target_section[key]} -> {source_section[key]}")
                elif key in source_section:
                    self.log_message(f"  {key}: (新增) -> {source_section[key]}")
                elif key in target_section:
                    self.log_message(f"  {key}: {target_section[key]} -> (删除)")
        
        self.log_message("")
    
    def start_batch_replacement(self):
        """Start batch replacement operation"""
        if not self.template_file_path:
            messagebox.showwarning("Warning", "Please select a template file first")
            return
        
        if not self.target_file_paths:
            messagebox.showwarning("Warning", "Please add target files first")
            return
        
        # Confirm operation
        result = messagebox.askyesno("Confirm Operation", 
                                   f"This will replace Vehicle content in {len(self.target_file_paths)} files "
                                   f"using template: {os.path.basename(self.template_file_path)}\n\n"
                                   f"All target files will be modified and backup files will be created.\n\n"
                                   f"Continue with batch replacement?")
        
        if not result:
            return
        
        try:
            self.log_message("=== Starting Batch Replacement ===")
            self.log_message(f"Template: {os.path.basename(self.template_file_path)}")
            self.log_message(f"Target files: {len(self.target_file_paths)}")
            self.log_message("")
            
            # Reset progress
            self.progress_bar['maximum'] = len(self.target_file_paths)
            self.progress_bar['value'] = 0
            
            # Perform batch replacement
            results = self.replacer.perform_batch_replacement(
                self.template_file_path, 
                self.target_file_paths, 
                self.update_progress
            )
            
            # Display results
            self.log_message("=== Batch Replacement Results ===")
            self.log_message(f"Backup files saved in yaml_backup/ folders within each file's directory")
            self.log_message("")
            success_count = 0
            failed_count = 0
            
            for result in results:
                status_symbol = "✓" if result['status'] == 'Success' else "✗"
                if result['status'] == 'Success' and result.get('new_file'):
                    self.log_message(f"{status_symbol} {result['file']} → {result['new_file']}")
                    self.log_message(f"    {result['message']}")
                    success_count += 1
                else:
                    self.log_message(f"{status_symbol} {result['file']}: {result['message']}")
                    if result['status'] == 'Success':
                        success_count += 1
                    else:
                        failed_count += 1
            
            self.log_message("")
            self.log_message(f"Batch operation completed: {success_count} successful, {failed_count} failed")
            self.log_message(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            messagebox.showinfo("Batch Replacement Complete", 
                              f"Batch replacement completed!\n\n"
                              f"Successful: {success_count}\n"
                              f"Failed: {failed_count}")
            
        except Exception as e:
            error_msg = f"Batch replacement failed: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def update_progress(self, current, total, current_file):
        """Update progress bar and status"""
        self.progress_bar['value'] = current
        if current < total:
            self.progress_var.set(f"Processing {current}/{total}: {current_file}")
        else:
            self.progress_var.set(f"Completed {total}/{total} files")
        self.root.update()
    
    def log_message(self, message: str):
        """Log message to the text area"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update()


def main():
    """Main function"""
    root = tk.Tk()
    app = BatchVehicleReplacerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
