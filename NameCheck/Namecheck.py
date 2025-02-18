import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Regular expression to match '20xx_xx_xx_xxxxxx' format
filename_pattern = r'20\d{2}_\d{2}_\d{2}_\d{6}'

# Function to extract the basic part of the filename (20xx_xx_xx_xxxxxx)
def extract_filename_base(file_name):
    match = re.search(filename_pattern, file_name)
    if match:
        return match.group(0)  # Return the matched filename_pattern
    return None

# Function to split cell contents using multiple delimiters
def split_filenames(cell_value):
    if isinstance(cell_value, str):
        # Use common delimiters: newline, comma, semicolon, space
        delimiters = r'[\n,; ]+'
        return re.split(delimiters, cell_value)
    return []

# Function to scan entire Excel for filenames that match the pattern
def scan_excel_for_filenames(df):
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

# Select Excel path
def select_excel_file():
    file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx")])
    excel_path_var.set(file_path)
    if file_path:
        try:
            # Read all sheet names from the Excel file
            sheet_names = pd.ExcelFile(file_path).sheet_names
            sheet_var.set(sheet_names[0])  # Default to the first sheet
            sheet_menu['menu'].delete(0, 'end')  # Clear old menu
            for sheet in sheet_names:
                sheet_menu['menu'].add_command(label=sheet, command=tk._setit(sheet_var, sheet))
        except Exception as e:
            messagebox.showerror("Error", f"Unable to read sheets from Excel: {str(e)}")

# Select Folder path
def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder")
    folder_path_var.set(folder_path)

# Create a new class for the result window
class ResultWindow:
    def __init__(self, parent, result_text):
        self.window = tk.Toplevel(parent)
        self.window.title("Comparison Results")
        self.window.geometry("600x400")

        # Save the original text for undo
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
        
        # Add copy button
        ttk.Button(button_frame, text="Copy Results (with newlines)", command=self.copy_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy as Single Line", command=self.copy_as_single_line).pack(side=tk.LEFT, padx=5)

    def apply_suffix(self):
        suffix = self.suffix_var.get()
        if suffix:
            # Get all text content
            content = self.text_widget.get("1.0", tk.END).strip()
            lines = content.split('\n')
            
            # Process each line
            new_content = []
            for line in lines:
                if line.strip() and not line.startswith("In Excel") and not line.startswith("In Folder"):
                    line = line + suffix
                new_content.append(line)
            
            # Update text box content
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", '\n'.join(new_content))

    def undo_changes(self):
        # Restore to original text
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", self.original_text)

    def copy_text(self):
        # Copy text with newlines
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text_widget.get("1.0", tk.END))
        messagebox.showinfo("Success", "Results copied to clipboard!")

    def copy_as_single_line(self):
        # Copy as single line (remove newlines and title lines)
        content = self.text_widget.get("1.0", tk.END).strip()
        lines = content.split('\n')
        
        # Filter out title lines and empty lines, only keep file names, and remove all whitespace characters
        filenames = [line.strip() for line in lines 
                    if line.strip() and not line.startswith("In Excel") and not line.startswith("In Folder")]
        
        # Connect all file names directly (without adding any separators)
        single_line = ''.join(filenames)
        
        # Ensure to remove any possible newline characters
        single_line = single_line.replace('\n', '').replace('\r', '')
        
        self.window.clipboard_clear()
        self.window.clipboard_append(single_line)
        messagebox.showinfo("Success", "Results copied as single line!")

# Function to check file completeness for each number
def check_file_completeness(folder_path, folder_filenames):
    # Dictionary to store files for each base number
    files_by_number = {}
    
    # Group files by their base number
    for filename in folder_filenames:
        # Use existing extract_filename_base function to get the full date-number string
        base_name = extract_filename_base(filename)
        if base_name:
            # Use the complete date-number string as key
            if base_name not in files_by_number:
                files_by_number[base_name] = set()
            files_by_number[base_name].add(filename)
    
    # Check completeness for each number
    incomplete_numbers = []
    for number, files in files_by_number.items():
        if len(files) < 4:  # If less than 4 files, it's incomplete
            incomplete_numbers.append(number)
    
    return incomplete_numbers

# Compare the filenames from Excel and Folder
def compare_files():
    excel_file_path = excel_path_var.get()
    folder_path = folder_path_var.get()
    selected_sheet = sheet_var.get()
    
    if not excel_file_path or not folder_path:
        messagebox.showerror("Error", "Please select again")
        return
    
    try:
        # Read the selected sheet from the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)

        # Scan the entire Excel for filenames matching the pattern and get duplicates
        excel_filenames, duplicates, test_count = scan_excel_for_filenames(df)

        # Get the file list from Folder
        folder_filenames = os.listdir(folder_path)

        # Extract the relevant file name from Folder and use a set to remove duplicates
        folder_filenames_base = set([extract_filename_base(f) for f in folder_filenames if extract_filename_base(f)])

        # Comparing filenames (Only the pattern)
        excel_not_in_folder = excel_filenames[~excel_filenames.isin(folder_filenames_base)]
        folder_not_in_excel = [f for f in folder_filenames_base if f not in excel_filenames.values]

        # Check file completeness
        incomplete_files = check_file_completeness(folder_path, folder_filenames)

        result = ""
        has_issues = False

        # In Excel but not in Folder
        if not excel_not_in_folder.empty:
            has_issues = True
            result += "In Excel but not in Folder:\n"
            result += "\n".join(excel_not_in_folder) + "\n\n"
        
        # In Folder but not in Excel
        if folder_not_in_excel:
            has_issues = True
            result += "In Folder but not in Excel:\n"
            result += "\n".join(folder_not_in_excel) + "\n\n"
        
        # Add incomplete files information
        if incomplete_files:
            has_issues = True
            result += "Numbers with incomplete files (less than 4 files):\n"
            result += ", ".join(incomplete_files) + "\n\n"

        # Add duplicate files information
        if duplicates:
            has_issues = True
            result += "Duplicate filenames found in Excel:\n"
            result += "\n".join(duplicates) + "\n\n"
        else:
            result += "No duplicate filenames found in Excel.\n\n"

        # If no issues found, show the complete success message
        if not has_issues:
            result = "All numbers have complete file sets (4 files each) and Excel matches Folder.\nNo duplicate filenames found in Excel."

        # Add test count information at the beginning of the result
        result = f"Now we have {test_count} different test numbers in the current Excel file ({selected_sheet}).\n\n" + result

        # Show results in the new window
        ResultWindow(root, result)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create GUI
root = tk.Tk()
root.title("Filename Comparison Tool")

# Save the path
excel_path_var = tk.StringVar()
folder_path_var = tk.StringVar()
sheet_var = tk.StringVar()

# layout
tk.Label(root, text="Select Excel File:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=excel_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_excel_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Select Sheet:").grid(row=1, column=0, padx=10, pady=10)
sheet_menu = tk.OptionMenu(root, sheet_var, '')  # Default empty menu
sheet_menu.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Select Folder:").grid(row=2, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=2, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_folder).grid(row=2, column=2, padx=10, pady=10)

tk.Button(root, text="Start Comparison", command=compare_files).grid(row=3, column=1, padx=10, pady=20)

root.mainloop()
