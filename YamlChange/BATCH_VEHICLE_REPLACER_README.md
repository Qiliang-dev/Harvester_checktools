# Batch Vehicle Content Replacer

## Overview

The Batch Vehicle Content Replacer is a tool designed for batch replacement of Vehicle content in YAML files using a template file. This tool allows you to apply the Vehicle section from one template file to multiple target files efficiently.

## Key Features

1. **Batch Processing** - Apply Vehicle content from a template to multiple target files
2. **Automatic Backup** - Creates timestamped backup files before modification
3. **Template Preview** - Preview template Vehicle content before applying
4. **Smart File Detection** - Auto-detect files in Austauchen folder
5. **Progress Tracking** - Real-time progress bar and status updates
6. **Detailed Logging** - Comprehensive operation logs and results

## Usage Methods

### Method 1: Standalone Launch

```bash
python start_vehicle_replacer.py
```

### Method 2: From Main YAML Editor

1. Run main program: `python YamlChange_noQT.py`
2. Click "Batch Vehicle Replacer" button

### Method 3: Direct Run

```bash
python vehicle_replacer.py
```

## Operation Steps

### Quick Setup Mode (Recommended)

1. Ensure the Austauchen folder contains:
   - Template file (containing `H022296` in filename)
   - Target files (other YAML files)

2. Click **"Quick Setup (Austauchen)"** button
   - Program auto-detects template and target files
   - Ready for batch replacement

### Manual Mode

1. **Select Template File**: Click "Browse" to select template file
2. **Add Target Files**: 
   - Use "Add Files" to select individual files
   - Use "Add Folder" to add all YAML files from a folder
   - Use "Remove Selected" or "Clear All" to manage the list
3. **Preview Template** (Optional): Click "Preview Template" to see template content
4. **Start Batch Replace**: Click to begin the batch operation

## Replacement Content Details

The Vehicle section includes the following 17 sub-sections that will be replaced:

### Core Components
- **CarModel** - Vehicle model information (Model, Variant, VIN, RHD)
- **OptionalEquipment** - Complete optional equipment list
- **Engine** - Engine status and type information

### Door Information
- **DriverDoor**, **PassengerDoor**, **DriverRearDoor**, **PassengerRearDoor**
- **Tailgate**, **Hood**
- Includes door/window status and Item properties

### Seat Information
- **SeatLeftRow1**, **SeatLeftRow2**, **SeatRightRow1**, **SeatRightRow2**, **SeatMidRow2**
- **Dashboard**, **Trunk**
- Includes seat position, occupancy status, seatbelt status, etc.

### Important Note
**Sensors** is NOT part of the Vehicle section - it's an independent node under TestCase and will NOT be replaced by this tool. Use the main YAML editor for Sensors modifications.

## Safety Features

1. **Automatic Backup**: Creates clean backup files in `yaml_backup/` folder before each operation
2. **Operation Confirmation**: Confirmation dialog before batch replacement
3. **Error Recovery**: Automatic file restoration if operation fails
4. **Detailed Logging**: Records every step and result
5. **Clean Backup Management**: Backup files maintain original filenames for easy identification

## File Structure Requirements

- Source and target files must contain `TestCase` root node
- `TestCase` must contain `Vehicle` node
- Files must be valid YAML format
- UTF-8 encoding recommended

## User Interface

### Template Selection
- Browse button to select template file
- Path display field shows selected template

### Target Files Management
- List box displays all target files
- Add/Remove buttons for file management
- Support for individual files or entire folders

### Progress Tracking
- Progress bar shows current operation status
- Status text shows current file being processed
- Real-time updates during batch operation

### Operation Log
- Scrollable text area shows detailed logs
- Success/failure indicators for each file
- Final summary with statistics

## Batch Processing Features

### Progress Tracking
- Real-time progress bar
- Current file being processed
- Completion percentage

### Result Summary
- Success count and failed count
- Detailed status for each file
- Error messages for failed operations

### Error Handling
- Individual file errors don't stop batch processing
- Detailed error logging
- Automatic backup restoration on critical failures

## Command Line Usage

While primarily a GUI tool, you can also use the core functionality programmatically:

```python
from vehicle_replacer import BatchVehicleReplacer

replacer = BatchVehicleReplacer()
results = replacer.perform_batch_replacement(
    template_file_path="template.yaml",
    target_file_paths=["file1.yaml", "file2.yaml"]
)
```

## Troubleshooting

### Common Issues

1. **"Austauchen folder not found"**
   - Ensure running from correct directory
   - Check if Austauchen folder exists

2. **"Template file not found"**
   - Verify template file contains identifying string in filename
   - Check file has .yaml extension

3. **"No target files found"**
   - Ensure target files exist in selected location
   - Verify files have .yaml extension

4. **"Invalid file format"**
   - Validate YAML file syntax
   - Ensure files contain TestCase and Vehicle nodes

5. **"Replacement failed"**
   - Check if files are locked by other programs
   - Verify write permissions
   - Review detailed error messages

### Backup Files

- **Location**: `yaml_backup/` folder within the same directory as each target file
- **Format**: Original filename (e.g., `original_file.yaml`)
- **Duplicates**: If backup exists, timestamp is added (e.g., `original_file_backup_20250919_143808.yaml`)
- **To restore**: Copy file from the local `yaml_backup/` folder back to its parent directory
- **Benefits**: Clean filenames, organized by location, easy to manage and identify
- **Example Structure**:
  ```
  Austauchen/
  ├── file1.yaml                    # Original file
  ├── file2.yaml                    # Original file
  └── yaml_backup/                  # Backup folder
      ├── file1.yaml               # Backup of file1
      └── file2.yaml               # Backup of file2
  ```

## Testing

Run the test script to verify functionality:

```bash
python test_vehicle_replacer.py
```

Tests include:
- File loading verification
- Vehicle content extraction
- Batch processing simulation
- Result validation

## Technical Implementation

- **Language**: Python 3.7+
- **GUI Framework**: Tkinter
- **YAML Processing**: PyYAML
- **File Operations**: Native Python file handling
- **Backup Mechanism**: shutil.copy2

## Version Information

- **Version**: 2.0 (Batch Processing)
- **Compatibility**: Python 3.7+
- **Dependencies**: PyYAML, Tkinter
- **Supported Platforms**: Windows, Linux, macOS

## Migration from Single File Replacer

If upgrading from the single-file Vehicle replacer:
- Interface completely redesigned for batch processing
- All text now in English
- Template-based workflow instead of source/target pair
- Enhanced progress tracking and logging
- Maintains all safety features from previous version

---

**Note**: Always backup important files manually before batch operations, although the program automatically creates backups for added safety.
