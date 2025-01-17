import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

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
    all_filenames = [] # Create a empty file to save the data from Excel
    for col in df.columns:
        # dropna: Ignore all the empty value
        # apply: apple the function split_filenames to all the no_empty box
        # explode: extend the list element to the row (relese the name split by symbol)
        column_data = df[col].dropna().apply(split_filenames).explode()
        column_filenames = column_data.apply(lambda x: extract_filename_base(str(x))).dropna()
        all_filenames.extend(column_filenames)
    return pd.Series(all_filenames).drop_duplicates()

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

        # Scan the entire Excel for filenames matching the pattern 
        excel_filenames = scan_excel_for_filenames(df)

        # Get the file list from Folder
        folder_filenames = os.listdir(folder_path)

        # Extract the relevant file name from Folder and use a set to remove duplicates
        folder_filenames_base = set([extract_filename_base(f) for f in folder_filenames if extract_filename_base(f)])

        # Comparing filenames (Only the pattern)
        excel_not_in_folder = excel_filenames[~excel_filenames.isin(folder_filenames_base)]
        folder_not_in_excel = [f for f in folder_filenames_base if f not in excel_filenames.values]

        result = ""
        # In Excel but not in Folder
        if not excel_not_in_folder.empty:
            result += "In Excel but not in Folder:\n"
            result += "\n".join(excel_not_in_folder) + "\n"
        # In Folder but not in Excel
        if folder_not_in_excel:
            result += "\nIn Folder but not in Excel:\n"
            result += "\n".join(folder_not_in_excel) + "\n"

        # If no differences, show a unified message
        if not result:
            result = "All filenames in Excel match those in the Folder."

        # Show the result
        messagebox.showinfo("Comparison Result", result)

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
