# NameCheck File Name Check Tool - Original Single File Version

## Project Description

This is a file name check tool used to compare filenames in Excel files with files in folders, and check file completeness.

## Features

- Select Excel files and folders for comparison
- Support Excel multi-Sheet selection
- Check file completeness (each test number should have 4 files)
- **NEW**: Customizable file count requirement (default: 4, user can change)
- Detect duplicate filenames
- Display comparison results
- Support adding suffixes to filenames
- Support copying results (keep line breaks or single line format)
- **NEW**: Show file count for each category
- **NEW**: Automatic time-based sorting of all results

## File Structure

```
NameCheck/
├── NameCheck_original.py    # Restored single file version
├── requirements.txt         # Python dependencies
└── README_original.md      # This documentation
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Run Python file directly:
   ```bash
   python NameCheck_original.py
   ```

2. In the program interface:
   - Select Excel file (.xlsx format)
   - Select Sheet to compare
   - Select folder to compare
   - Click "Start Comparison" button

## Filename Format Requirements

The program recognizes filenames matching the following format:
- Format: `20xx_xx_xx_xxxxxx`
- Example: `2024_01_15_123456`

## New File Count Feature

The program now displays the count of files/numbers for each category:
- "In Excel but not in folder (X files):" - Shows how many files are missing from folder
- "In folder but not in Excel (X files):" - Shows how many extra files are in folder
- "Incomplete file numbers (less than X files) (Y numbers):" - Shows how many test numbers are incomplete
- "Duplicate filenames found in Excel (X duplicates):" - Shows how many duplicates exist

## Customizable File Count Requirement

- **Default setting**: 4 files per test number
- **Customizable**: Users can change this number in the interface
- **Input validation**: Ensures the number is valid and greater than 0
- **Dynamic results**: All messages and checks update based on the custom setting

## Time-Based Sorting Feature

- **Automatic sorting**: All file numbers are automatically sorted by time order
- **Sorting rules**: 
  - First priority: Date (from early to late)
  - Second priority: Number (from small to large within the same date)
- **Example**: `2024_01_15_123456` → `2024_01_15_456789` → `2024_01_16_123456`
- **Applied to**: All result categories (missing files, extra files, incomplete files, duplicates)

## System Requirements

- Python 3.6+
- tkinter (usually installed with Python)
- pandas
- openpyxl

## Notes

- Ensure Excel file format is .xlsx
- Folder should contain files to compare
- Each test number typically needs 4 related files
