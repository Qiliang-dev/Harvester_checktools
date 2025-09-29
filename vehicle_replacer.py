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
    
    # File renaming is handled by a separate tool; no conflict handling needed here
    
    def update_testcase_fields(self, yaml_data: Dict[str, Any], new_filename_without_ext: str) -> None:
        """Update TestCase.Name and TestCase.Filename fields"""
        if 'TestCase' in yaml_data:
            # Update Name field (without extension)
            yaml_data['TestCase']['Name'] = new_filename_without_ext
            
            # Update Filename field (with .blf extension)
            yaml_data['TestCase']['Filename'] = f"{new_filename_without_ext}.blf"
    
    def replace_block_content(self, target_file_path: str, block_name: str, source_block_data: Any) -> bool:
        """Replace a top-level TestCase block (e.g., Vehicle, Catalog) in target file.
        Creates the block if missing.
        """
        try:
            # Create backup
            backup_path = self.create_backup(target_file_path)
            print(f"Backup created: {backup_path}")
            
            # Read target file
            with open(target_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find TestCase start and the target block start/end positions
            testcase_start = -1
            block_start = -1
            block_end = -1
            testcase_indent = ""
            block_indent = ""
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped == "TestCase:":
                    testcase_start = i
                    testcase_indent = line[:line.find('TestCase:')]
                    continue
                if testcase_start != -1 and stripped == f"{block_name}:":
                    block_start = i
                    block_indent = line[:line.find(f'{block_name}:')]
                    break
            
            if testcase_start == -1:
                raise ValueError("TestCase node not found")
            
            # If block not present, we will insert at the end of TestCase block
            # Determine end of existing block (if present) or end of TestCase
            base_indent_len = len(block_indent) if block_start != -1 else len(testcase_indent)
            
            search_from = (block_start + 1) if block_start != -1 else (testcase_start + 1)
            for i in range(search_from, len(lines)):
                line = lines[i]
                if line.strip():
                    current_indent_len = len(line) - len(line.lstrip())
                    # stop when going out of the current scope (block or TestCase)
                    if current_indent_len <= base_indent_len:
                        block_end = i - 1
                        break
            
            if block_end == -1:
                block_end = len(lines) - 1
            
            # Generate new block YAML content
            # For null (None) source, just set to null
            if source_block_data is None:
                new_block_yaml = [f"{(block_indent or testcase_indent + '  ')}{block_name}: null\n"]
            else:
                # Ensure we always emit the block header
                block_header_indent = block_indent or (testcase_indent + "  ")
                new_block_yaml = [f"{block_header_indent}{block_name}:\n"]
                if isinstance(source_block_data, dict):
                    new_block_yaml += self.generate_vehicle_yaml(source_block_data, block_header_indent + "  ")
                else:
                    # Scalar or list - dump as YAML under correct indent
                    dumped = yaml.dump({block_name: source_block_data}, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    dumped_lines = dumped.splitlines()
                    # First line will be like 'block_name: ...' — replace with header already written
                    for dl in dumped_lines[1:]:
                        new_block_yaml.append(block_header_indent + dl + "\n")
            
            # Build new file content
            if block_start == -1:
                # Insert new block at the end of TestCase block
                insert_pos = block_end + 1
                new_lines = lines[:insert_pos] + new_block_yaml + lines[insert_pos:]
            else:
                new_lines = (
                    lines[:block_start] +
                    new_block_yaml +
                    lines[block_end + 1:]
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

    def replace_root_block_content(self, target_file_path: str, block_name: str, source_block_data: Any) -> bool:
        """Replace or insert a root-level block (e.g., Catalog) in target file"""
        try:
            backup_path = self.create_backup(target_file_path)
            print(f"Backup created: {backup_path}")

            with open(target_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            block_start = -1
            block_end = -1
            block_indent = ""

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped == f"{block_name}:":
                    block_start = i
                    block_indent = line[:line.find(f'{block_name}:')]
                    break

            base_indent_len = len(block_indent)
            search_from = block_start + 1 if block_start != -1 else 0
            for i in range(search_from, len(lines)):
                line = lines[i]
                if line.strip():
                    current_indent_len = len(line) - len(line.lstrip())
                    if block_start == -1:
                        # root-level: stop on next top-level key (indent == 0)
                        if current_indent_len == 0 and i > 0:
                            block_end = i - 1
                            break
                    else:
                        if current_indent_len <= base_indent_len:
                            block_end = i - 1
                            break

            if block_end == -1:
                block_end = len(lines) - 1

            # Build new block YAML text
            if source_block_data is None:
                new_block_yaml = [f"{block_indent}{block_name}: null\n"]
            else:
                new_block_yaml = [f"{block_indent}{block_name}:\n"]
                if isinstance(source_block_data, dict):
                    new_block_yaml += self.generate_vehicle_yaml(source_block_data, block_indent + "  ")
                else:
                    dumped = yaml.dump({block_name: source_block_data}, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    dumped_lines = dumped.splitlines()
                    for dl in dumped_lines[1:]:
                        new_block_yaml.append(block_indent + dl + "\n")

            if block_start == -1:
                # append at end with a newline if needed
                if len(lines) > 0 and lines[-1] and not lines[-1].endswith('\n'):
                    lines[-1] = lines[-1] + '\n'
                new_lines = lines + new_block_yaml
            else:
                new_lines = lines[:block_start] + new_block_yaml + lines[block_end + 1:]

            with open(target_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True

        except Exception as e:
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
    
    def update_vehicle_and_fields_in_place(self, target_file_path: str, source_vehicle_data: Dict[str, Any], new_vehicle_suffix: str) -> None:
        """Replace Vehicle content and update TestCase fields in place (no renaming)"""
        try:
            target_filename = os.path.basename(target_file_path)
            if not self.validate_filename_format(target_filename):
                raise ValueError(f"Invalid filename format: {target_filename}")

            # Create backup
            backup_path = self.create_backup(target_file_path)
            print(f"Backup created: {backup_path}")

            # Compute new base name for fields only
            new_filename = self.generate_new_filename(target_filename, new_vehicle_suffix)
            new_base_name = os.path.splitext(new_filename)[0]

            # Load and modify YAML content
            with open(target_file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.load(f, Loader=yaml.FullLoader)

            yaml_data['TestCase']['Vehicle'] = source_vehicle_data
            self.update_testcase_fields(yaml_data, new_base_name)

            # Write back to the same file preserving Vehicle formatting
            self.write_updated_yaml_file(target_file_path, yaml_data, source_vehicle_data)

        except Exception as e:
            # Attempt to restore from backup on failure
            if 'backup_path' in locals() and os.path.exists(backup_path):
                shutil.copy2(backup_path, target_file_path)
            raise Exception(f"In-place update failed: {str(e)}")
    
    def write_updated_yaml_file(self, file_path: str, yaml_data: Dict[str, Any], block_data: Dict[str, Any], block_name: str = "Vehicle") -> None:
        """Write updated YAML file with proper formatting"""
        # First write the YAML data with basic dump
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Then read back and replace the Vehicle section with proper formatting
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and replace selected block section
        block_start = -1
        block_end = -1
        block_indent = ""
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == f"{block_name}:":
                block_start = i
                block_indent = line[:line.find(f'{block_name}:')]
                break
        
        if block_start != -1:
            # Find block section end
            base_indent_len = len(block_indent)
            for i in range(block_start + 1, len(lines)):
                line = lines[i]
                if line.strip():
                    current_indent_len = len(line) - len(line.lstrip())
                    if current_indent_len <= base_indent_len:
                        block_end = i - 1
                        break
            
            if block_end == -1:
                block_end = len(lines) - 1
            
            # Generate new Vehicle YAML content
            new_block_yaml = self.generate_vehicle_yaml(block_data, block_indent + "  ") if isinstance(block_data, dict) else [f"{block_indent}  {block_data}\n"]
            
            # Replace Vehicle section
            new_lines = (
                lines[:block_start + 1] +
                new_block_yaml +
                lines[block_end + 1:]
            )
            
            # Write the final result
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    
    def perform_batch_replacement(self, template_file_path: str, target_file_paths: list, progress_callback=None, block_name: str = "Vehicle") -> list:
        """Execute batch replacement in place (no file renaming)"""
        self.processing_results = []
        
        try:
            # Load template file and extract vehicle suffix
            template_data = self.load_yaml_file(template_file_path)
            # Determine where the block lives: root-level or under TestCase
            root_level_block = None
            testcase_block = None
            if block_name in template_data:
                root_level_block = template_data.get(block_name)
            elif 'TestCase' in template_data and block_name in template_data['TestCase']:
                testcase_block = template_data['TestCase'].get(block_name)
            else:
                raise ValueError(f"Template missing block: {block_name}")
            
            template_filename = os.path.basename(template_file_path)
            template_vehicle_suffix = self.extract_vehicle_suffix(template_filename)
            
            total_files = len(target_file_paths)
            
            self.log_operation(f"Template vehicle suffix: {template_vehicle_suffix}")
            self.log_operation(f"Processing {total_files} target files for block '{block_name}' ...")
            
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
                    _ = self.load_yaml_file(target_file_path)
                    
                    # Execute in-place update for selected block
                    if root_level_block is not None:
                        self.replace_root_block_content(target_file_path, block_name, root_level_block)
                    else:
                        self.replace_block_content(target_file_path, block_name, testcase_block)
                    
                    # Vehicle-specific field sync (only when Vehicle is under TestCase)
                    if block_name == "Vehicle" and testcase_block is not None:
                        # Load, update Name/Filename based on template suffix
                        with open(target_file_path, 'r', encoding='utf-8') as f:
                            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                        new_filename = self.generate_new_filename(target_filename, template_vehicle_suffix)
                        new_base_name = os.path.splitext(new_filename)[0]
                        self.update_testcase_fields(yaml_data, new_base_name)
                        # Write back with preserved Vehicle formatting
                        self.write_updated_yaml_file(target_file_path, yaml_data, yaml_data['TestCase']['Vehicle'], block_name="Vehicle")
                    
                    result = {
                        'file': target_filename,
                        'new_file': None,
                        'status': 'Success',
                        'message': f"Block '{block_name}' replaced successfully"
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
                progress_callback(total_files, total_files, "Batch processing completed")
            
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
        self.root.title("YAML Block Replacer - Batch replace blocks in YAML files")
        self.root.geometry("700x500")
        
        self.replacer = BatchVehicleReplacer()
        # Override the log_operation method to use GUI logging
        self.replacer.log_operation = self.log_message
        self.template_file_path = None
        self.target_file_paths = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup User Interface"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="YAML Block Replacer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 8))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Use one template to replace any block (Vehicle, Catalog, ...) across files",
                              font=("Arial", 9))
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Template file selection
        ttk.Label(main_frame, text="Template File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.template_file_var = tk.StringVar()
        self.template_entry = ttk.Entry(main_frame, textvariable=self.template_file_var, width=60)
        self.template_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_template_file).grid(row=2, column=2, pady=5)
        
        # Scope + Block selection
        ttk.Label(main_frame, text="Scope:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.scope_var = tk.StringVar()
        self.scope_combo = ttk.Combobox(main_frame, textvariable=self.scope_var, state='readonly', width=20)
        self.scope_combo['values'] = ["Root", "TestCase"]
        self.scope_combo.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.scope_combo.bind('<<ComboboxSelected>>', self.on_scope_changed)

        ttk.Label(main_frame, text="Block:").grid(row=3, column=1, sticky=tk.E, pady=5)
        self.block_name_var = tk.StringVar()
        self.block_combo = ttk.Combobox(main_frame, textvariable=self.block_name_var, state='readonly', width=35)
        self.block_combo.grid(row=3, column=1, padx=(140,5), pady=5, sticky=tk.W)
        ttk.Button(main_frame, text="Refresh Blocks", command=self.refresh_blocks_from_template).grid(row=3, column=2, pady=5)
        
        # Target files selection
        ttk.Label(main_frame, text="Target Files:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Target files frame
        target_frame = ttk.Frame(main_frame)
        target_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Target files listbox with scrollbar
        listbox_frame = ttk.Frame(target_frame)
        listbox_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.target_listbox = tk.Listbox(listbox_frame, height=4, width=70)
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
        operation_frame.grid(row=6, column=0, columnspan=3, pady=15)
        
        ttk.Button(operation_frame, text="Start Batch Replace", command=self.start_batch_replacement, 
                  style="Accent.TButton").grid(row=0, column=0, padx=10)
        
        # Center the button
        operation_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=7, column=1, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Results display area
        ttk.Label(main_frame, text="Operation Log:").grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        
        # Create text box and scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.result_text = tk.Text(text_frame, height=8, width=80)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure weights for window resizing
        main_frame.rowconfigure(10, weight=1)
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
            # Refresh available blocks from template
            self.refresh_blocks_from_template()

    def refresh_blocks_from_template(self):
        """Populate block selector from the selected template's TestCase keys"""
        if not self.template_file_path:
            messagebox.showwarning("Warning", "Please select a template file first")
            return
        try:
            template_data = self.replacer.load_yaml_file(self.template_file_path)
            testcase = template_data.get('TestCase', {})
            # Split root-level and TestCase-level blocks
            root_blocks = []
            for k, v in template_data.items():
                if k == 'TestCase':
                    continue
                # 允许 dict/list/None 作为块；跳过纯标量简单值
                if isinstance(v, (dict, list)) or v is None:
                    root_blocks.append(k)
            testcase_blocks = list(testcase.keys())
            root_blocks.sort()
            testcase_blocks.sort()
            # Store for scope switching
            self._root_blocks = root_blocks
            self._testcase_blocks = testcase_blocks
            # Default scope优先TestCase
            default_scope = 'TestCase' if testcase_blocks else 'Root'
            self.scope_combo.set(default_scope)
            self.update_block_list_by_scope()
            self.log_message(
                f"Blocks found - Root: {', '.join(root_blocks) or '∅'}; TestCase: {', '.join(testcase_blocks) or '∅'}"
            )
        except Exception as e:
            self.log_message(f"Failed to read blocks from template: {e}")

    def on_scope_changed(self, event=None):
        self.update_block_list_by_scope()

    def update_block_list_by_scope(self):
        scope = (self.scope_var.get() or 'TestCase').strip()
        if scope == 'Root':
            values = getattr(self, '_root_blocks', [])
        else:
            values = getattr(self, '_testcase_blocks', [])
        self.block_combo['values'] = values
        # 默认选择 Vehicle（仅在TestCase域且存在时），否则选第一项
        if scope == 'TestCase' and 'Vehicle' in values:
            self.block_combo.set('Vehicle')
        elif values:
            self.block_combo.set(values[0])
    
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
            # Determine selected block
            selected_block = self.block_name_var.get().strip() or 'Vehicle'
            self.log_message(f"Selected block: {selected_block}")
            results = self.replacer.perform_batch_replacement(
                self.template_file_path, 
                self.target_file_paths, 
                self.update_progress,
                block_name=selected_block
            )
            
            # Display results
            self.log_message("=== Batch Replacement Results (In-Place) ===")
            self.log_message(f"Backups saved in yaml_backup/ within each file's directory")
            self.log_message("")
            success_count = 0
            failed_count = 0
            
            for result in results:
                status_symbol = "✓" if result['status'] == 'Success' else "✗"
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
