"""
File Name Check Tool - Original Single File Version
Function: Compare filenames in Excel files with files in folders, check file completeness
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import re
from typing import List, Set, Dict, Optional, Tuple

# Configuration constants
FILENAME_PATTERN = r'20\d{2}_\d{2}_\d{2}_\d{6}'
FILES_PER_TEST = 4  # Default value, can be changed by user
WINDOW_TITLE = "File Name Check Tool"
RESULT_WINDOW_TITLE = "Comparison Results"
RESULT_WINDOW_WIDTH = 600
RESULT_WINDOW_HEIGHT = 400

def extract_filename_base(file_name: str) -> Optional[str]:
    """
    Extract the basic part of filename that matches the pattern (20xx_xx_xx_xxxxxx)
    
    Args:
        file_name: filename to process
        
    Returns:
        matched filename basic part, or None if no match
    """
    match = re.search(FILENAME_PATTERN, file_name)
    if match:
        return match.group(0)  # return matched pattern
    return None

def get_folder_files(folder_path: str) -> List[str]:
    """
    Get all files in the folder
    
    Args:
        folder_path: folder path
        
    Returns:
        list of files in the folder
    """
    return os.listdir(folder_path)

def extract_folder_filename_bases(folder_filenames: List[str]) -> Set[str]:
    """
    Extract filename basic parts that match the pattern from folder file list
    
    Args:
        folder_filenames: list of files in folder
            
    Returns:
        set of filename basic parts that match the pattern
    """
    return set([extract_filename_base(f) for f in folder_filenames if extract_filename_base(f)])

def check_file_completeness(folder_path: str, folder_filenames: List[str]) -> List[str]:
    """
    Check if each test number has a complete file set
    
    Args:
        folder_path: folder path
        folder_filenames: list of files in folder
        
    Returns:
        list of incomplete test numbers
    """
    # Group files by test number
    files_by_number = {}
    
    # Group files by their basic number
    for filename in folder_filenames:
        # Use extract_filename_base function to get complete date-number string
        base_name = extract_filename_base(filename)
        if base_name:
            # Use complete date-number string as key
            if base_name not in files_by_number:
                files_by_number[base_name] = set()
            files_by_number[base_name].add(filename)
    
    # Check completeness of each number
    incomplete_numbers = []
    for number, files in files_by_number.items():
        if len(files) < FILES_PER_TEST:  # incomplete if file count less than FILES_PER_TEST
            incomplete_numbers.append(number)
    
    return incomplete_numbers

def check_file_completeness_custom(folder_path: str, folder_filenames: List[str], files_per_test: int) -> List[str]:
    """
    Check if each test number has a complete file set with custom file count requirement
    
    Args:
        folder_path: folder path
        folder_filenames: list of files in folder
        files_per_test: required number of files per test number
        
    Returns:
        list of incomplete test numbers
    """
    # Group files by test number
    files_by_number = {}
    
    # Group files by their basic number
    for filename in folder_filenames:
        # Use extract_filename_base function to get complete date-number string
        base_name = extract_filename_base(filename)
        if base_name:
            # Use complete date-number string as key
            if base_name not in files_by_number:
                files_by_number[base_name] = set()
            files_by_number[base_name].add(filename)
    
    # Check completeness of each number
    incomplete_numbers = []
    for number, files in files_by_number.items():
        if len(files) < files_per_test:  # incomplete if file count less than files_per_test
            incomplete_numbers.append(number)
    
    return incomplete_numbers

def split_filenames(cell_value):
    """
    Split cell content using multiple delimiters
    
    Args:
        cell_value: cell content
        
    Returns:
        list of split filenames
    """
    if isinstance(cell_value, str):
        # Use common delimiters: newline, comma, semicolon, space
        delimiters = r'[\n,; ]+'
        return re.split(delimiters, cell_value)
    return []

def scan_excel_for_filenames(df: pd.DataFrame) -> Tuple[pd.Series, List[str], int]:
    """
    Scan entire Excel table to find all filenames matching the pattern
    
    Args:
        df: pandas DataFrame object
        
    Returns:
        Tuple containing:
        - all unique filenames (pandas.Series)
        - list of duplicate filenames
        - count of different test numbers
    """
    all_filenames = []
    for col in df.columns:
        column_data = df[col].dropna().apply(split_filenames).explode()
        column_filenames = column_data.apply(lambda x: extract_filename_base(str(x))).dropna()
        all_filenames.extend(column_filenames)
    
    # Convert to Series and find duplicates
    filename_series = pd.Series(all_filenames)
    duplicates = filename_series[filename_series.duplicated()].unique()
    unique_filenames = filename_series.drop_duplicates()
    
    # Calculate count of different test numbers
    test_numbers = set()
    for filename in all_filenames:
        if filename:
            test_number = filename[-6:]  # get last 6 digits of filename
            test_numbers.add(test_number)
    
    return unique_filenames, duplicates.tolist(), len(test_numbers)

def get_excel_sheets(file_path: str) -> List[str]:
    """
    Get all sheet names from Excel file
    
    Args:
        file_path: Excel file path
        
    Returns:
        list of sheet names
    """
    return pd.ExcelFile(file_path).sheet_names

def sort_filenames_by_time(filenames: List[str]) -> List[str]:
    """
    Sort filenames by time order (date from early to late, number from small to large)
    
    Args:
        filenames: list of filenames to sort
        
    Returns:
        sorted list of filenames
    """
    def sort_key(filename):
        # Extract date part (first 8 characters: 20xx_xx_xx)
        date_part = filename[:8]
        # Extract number part (last 6 characters: xxxxxx)
        number_part = int(filename[9:])
        # Sort by date first, then by number
        return (date_part, number_part)
    
    return sorted(filenames, key=sort_key)

class ResultWindow:
    """
    Window class for displaying comparison results
    """
    def __init__(self, parent, result_text):
        """
        Initialize result window
        
        Args:
            parent: parent window
            result_text: result text to display
        """
        self.window = tk.Toplevel(parent)
        self.window.title(RESULT_WINDOW_TITLE)
        self.window.geometry(f"{RESULT_WINDOW_WIDTH}x{RESULT_WINDOW_HEIGHT}")

        # Save original text for undo
        self.original_text = result_text

        # Add input box and button frame
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(pady=5)
        
        # Add input box
        self.suffix_var = tk.StringVar()
        ttk.Label(self.input_frame, text="Add suffix:").pack(side=tk.LEFT, padx=5)
        self.suffix_entry = ttk.Entry(self.input_frame, textvariable=self.suffix_var)
        self.suffix_entry.pack(side=tk.LEFT, padx=5)
        
        # Add apply suffix button and undo button
        ttk.Button(self.input_frame, text="Apply Suffix", command=self.apply_suffix).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="Undo", command=self.undo_changes).pack(side=tk.LEFT, padx=5)

        # Create text box
        self.text_widget = tk.Text(self.window, wrap=tk.WORD, width=70, height=20)
        self.text_widget.insert(tk.END, result_text)
        self.text_widget.pack(padx=10, pady=10)

        # Create button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=5)
        
        # Add copy buttons
        ttk.Button(button_frame, text="Copy Results (Keep Line Breaks)", command=self.copy_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy as Single Line", command=self.copy_as_single_line).pack(side=tk.LEFT, padx=5)

    def apply_suffix(self):
        """
        Add suffix to all filenames
        """
        suffix = self.suffix_var.get()
        if suffix:
            # Get all text content
            content = self.text_widget.get("1.0", tk.END).strip()
            lines = content.split('\n')
            
            # Process each line
            new_content = []
            for line in lines:
                if line.strip() and not line.startswith("In Excel but not in folder") and not line.startswith("In folder but not in Excel"):
                    line = line + suffix
                new_content.append(line)
            
            # Update text box content
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", '\n'.join(new_content))

    def undo_changes(self):
        """
        Undo changes, restore original text
        """
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", self.original_text)

    def copy_text(self):
        """
        Copy text (keep line breaks)
        """
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text_widget.get("1.0", tk.END))
        messagebox.showinfo("Success", "Results copied to clipboard!")

    def copy_as_single_line(self):
        """
        Copy as single line (remove line breaks and title lines)
        """
        content = self.text_widget.get("1.0", tk.END).strip()
        lines = content.split('\n')
        
        # Filter out title lines and empty lines, keep only filenames, remove all whitespace
        filenames = [line.strip() for line in lines 
                    if line.strip() and not line.startswith("In Excel but not in folder") and not line.startswith("In folder but not in Excel")]
        
        # Directly connect all filenames (no separators)
        single_line = ''.join(filenames)
        
        # Ensure all possible line breaks are removed
        single_line = single_line.replace('\n', '').replace('\r', '')
        
        self.window.clipboard_clear()
        self.window.clipboard_append(single_line)
        messagebox.showinfo("Success", "Results copied as single line!")

class MainWindow:
    """
    Main window class, responsible for file selection and comparison operations
    """
    def __init__(self, root):
        """
        Initialize main window
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title(WINDOW_TITLE)
        
        # Save paths
        self.excel_path_var = tk.StringVar()
        self.folder_path_var = tk.StringVar()
        self.sheet_var = tk.StringVar()
        self.files_per_test_var = tk.StringVar(value=str(FILES_PER_TEST))  # Default value
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Setup UI components
        """
        # Excel file selection
        tk.Label(self.root, text="Select Excel File:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.excel_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.select_excel_file).grid(row=0, column=2, padx=10, pady=10)
        
        # Sheet selection
        tk.Label(self.root, text="Select Sheet:").grid(row=1, column=0, padx=10, pady=10)
        self.sheet_menu = tk.OptionMenu(self.root, self.sheet_var, '')  # default empty menu
        self.sheet_menu.grid(row=1, column=1, padx=10, pady=10)
        
        # Folder selection
        tk.Label(self.root, text="Select Folder:").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.folder_path_var, width=50).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.select_folder).grid(row=2, column=2, padx=10, pady=10)
        
        # Files per test number setting
        tk.Label(self.root, text="Files per Test Number:").grid(row=3, column=0, padx=10, pady=10)
        files_entry = tk.Entry(self.root, textvariable=self.files_per_test_var, width=10)
        files_entry.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        tk.Label(self.root, text="(Default: 4)").grid(row=3, column=1, padx=120, pady=10, sticky='w')
        
        # Start comparison button
        tk.Button(self.root, text="Start Comparison", command=self.compare_files).grid(row=4, column=1, padx=10, pady=20)
    
    def select_excel_file(self):
        """
        Select Excel file
        """
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx")])
        self.excel_path_var.set(file_path)
        if file_path:
            try:
                # Read all sheet names from Excel file
                sheet_names = get_excel_sheets(file_path)
                self.sheet_var.set(sheet_names[0])  # default select first sheet
                self.sheet_menu['menu'].delete(0, 'end')  # clear old menu
                for sheet in sheet_names:
                    self.sheet_menu['menu'].add_command(label=sheet, command=tk._setit(self.sheet_var, sheet))
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read sheets from Excel: {str(e)}")
    
    def select_folder(self):
        """
        Select folder
        """
        folder_path = filedialog.askdirectory(title="Select Folder")
        self.folder_path_var.set(folder_path)
    
    def compare_files(self):
        """
        Compare files
        """
        excel_file_path = self.excel_path_var.get()
        folder_path = self.folder_path_var.get()
        selected_sheet = self.sheet_var.get()
        
        if not excel_file_path or not folder_path:
            messagebox.showerror("Error", "Please select Excel file and folder again")
            return
        
        # Get and validate files per test number
        try:
            files_per_test = int(self.files_per_test_var.get())
            if files_per_test <= 0:
                messagebox.showerror("Error", "Files per test number must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Files per test number must be a valid number")
            return
        
        try:
            # Read selected Excel sheet
            df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)
            
            # Scan entire Excel for filenames matching pattern and get duplicates
            excel_filenames, duplicates, test_count = scan_excel_for_filenames(df)
            
            # Get file list from folder
            folder_filenames = get_folder_files(folder_path)
            
            # Extract relevant filenames from folder and use set to remove duplicates
            folder_filenames_base = extract_folder_filename_bases(folder_filenames)
            
            # Compare filenames (only match patterns)
            excel_not_in_folder = excel_filenames[~excel_filenames.isin(folder_filenames_base)]
            folder_not_in_excel = [f for f in folder_filenames_base if f not in excel_filenames.values]
            
            # Check file completeness with custom files_per_test value
            incomplete_files = check_file_completeness_custom(folder_path, folder_filenames, files_per_test)
            
            # Sort all filename lists by time order
            excel_not_in_folder_sorted = sort_filenames_by_time(excel_not_in_folder.tolist())
            folder_not_in_excel_sorted = sort_filenames_by_time(folder_not_in_excel)
            incomplete_files_sorted = sort_filenames_by_time(incomplete_files)
            duplicates_sorted = sort_filenames_by_time(duplicates)
            
            result = ""
            has_issues = False
            
            # In Excel but not in folder
            if excel_not_in_folder_sorted:
                has_issues = True
                result += f"In Excel but not in folder ({len(excel_not_in_folder_sorted)} files):\n"
                result += "\n".join(excel_not_in_folder_sorted) + "\n\n"
            
            # In folder but not in Excel
            if folder_not_in_excel_sorted:
                has_issues = True
                result += f"In folder but not in Excel ({len(folder_not_in_excel_sorted)} files):\n"
                result += "\n".join(folder_not_in_excel_sorted) + "\n\n"
            
            # Add incomplete file information
            if incomplete_files_sorted:
                has_issues = True
                result += f"Incomplete file numbers (less than {files_per_test} files) ({len(incomplete_files_sorted)} numbers):\n"
                result += ", ".join(incomplete_files_sorted) + "\n\n"
            
            # Add duplicate file information
            if duplicates_sorted:
                has_issues = True
                result += f"Duplicate filenames found in Excel ({len(duplicates_sorted)} duplicates):\n"
                result += "\n".join(duplicates_sorted) + "\n\n"
            else:
                result += "No duplicate filenames found in Excel.\n\n"
            
            # If no issues found, show complete success message
            if not has_issues:
                result = f"All numbers have complete file sets ({files_per_test} files each), Excel and folder match.\nNo duplicate filenames found in Excel."
            
            # Add test count information at the beginning of result
            result = f"Current Excel file ({selected_sheet}) has {test_count} different test numbers.\n\n" + result
            
            # Show result window
            ResultWindow(self.root, result)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    """
    Program main entry function
    """
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
