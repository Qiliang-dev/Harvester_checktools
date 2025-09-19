#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Batch Vehicle Replacer functionality
"""

import os
import sys
import shutil
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vehicle_replacer import BatchVehicleReplacer

def test_batch_vehicle_replacer():
    """Test Batch Vehicle Replacer functionality"""
    print("=== Batch Vehicle Replacer Test ===")
    
    # Check if test files exist
    template_file = "Austauchen/2025_09_19_134119_H022296_E.yaml"
    target_file = "Austauchen/2025_04_15_151228_DA00097_E.yaml"
    
    if not os.path.exists(template_file):
        print(f"Error: Template file not found - {template_file}")
        return False
    
    if not os.path.exists(target_file):
        print(f"Error: Target file not found - {target_file}")
        return False
    
    print(f"Template file: {template_file}")
    print(f"Target file: {target_file}")
    
    # Create test copies
    test_target_files = []
    for i in range(3):
        test_file = target_file.replace('.yaml', f'_test_{i}.yaml')
        shutil.copy2(target_file, test_file)
        test_target_files.append(test_file)
        print(f"Created test copy: {test_file}")
    
    try:
        # Create batch replacer instance
        replacer = BatchVehicleReplacer()
        
        # Test file loading
        print("\n1. Testing file loading...")
        template_data = replacer.load_yaml_file(template_file)
        print("   Template file loaded successfully")
        
        # Test Vehicle content extraction
        print("\n2. Testing Vehicle content extraction...")
        template_vehicle = replacer.extract_vehicle_content(template_data)
        print(f"   Template Vehicle contains: {len(template_vehicle)} main sections")
        
        # Show template content summary
        print("\n3. Template content summary...")
        for section in template_vehicle.keys():
            if section == "OptionalEquipment" and isinstance(template_vehicle[section], dict):
                print(f"   {section}: {len(template_vehicle[section])} items")
            elif isinstance(template_vehicle[section], dict):
                print(f"   {section}: {len(template_vehicle[section])} sub-items")
            else:
                print(f"   {section}: {template_vehicle[section]}")
        
        # Test batch replacement
        print("\n4. Testing batch replacement...")
        
        def progress_callback(current, total, current_file):
            print(f"   Progress: {current}/{total} - {current_file}")
        
        results = replacer.perform_batch_replacement(
            template_file, 
            test_target_files, 
            progress_callback
        )
        
        # Display results
        print("\n5. Batch replacement results...")
        success_count = 0
        failed_count = 0
        
        for result in results:
            status_symbol = "✓" if result['status'] == 'Success' else "✗"
            print(f"   {status_symbol} {result['file']}: {result['message']}")
            if result['status'] == 'Success':
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\n   Summary: {success_count} successful, {failed_count} failed")
        
        # Verify replacement results
        print("\n6. Verifying replacement results...")
        for test_file in test_target_files:
            if os.path.exists(test_file):
                new_data = replacer.load_yaml_file(test_file)
                new_vehicle = replacer.extract_vehicle_content(new_data)
                
                # Check key fields
                if 'CarModel' in new_vehicle and 'CarModel' in template_vehicle:
                    if new_vehicle['CarModel'].get('VIN') == template_vehicle['CarModel'].get('VIN'):
                        print(f"   ✓ {os.path.basename(test_file)}: VIN replacement verified")
                    else:
                        print(f"   ✗ {os.path.basename(test_file)}: VIN replacement failed")
                
                if 'OptionalEquipment' in new_vehicle and 'OptionalEquipment' in template_vehicle:
                    if len(new_vehicle['OptionalEquipment']) == len(template_vehicle['OptionalEquipment']):
                        print(f"   ✓ {os.path.basename(test_file)}: OptionalEquipment replacement verified")
                    else:
                        print(f"   ✗ {os.path.basename(test_file)}: OptionalEquipment replacement failed")
        
        print("\nBatch test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nBatch test failed: {str(e)}")
        return False
    
    finally:
        # Clean up test files
        print("\nCleaning up test files...")
        for test_file in test_target_files:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"Removed: {test_file}")
            
            # Also remove backup files
            backup_pattern = f"{test_file}.backup_"
            for file in os.listdir(os.path.dirname(test_file)):
                if file.startswith(os.path.basename(backup_pattern)):
                    backup_file = os.path.join(os.path.dirname(test_file), file)
                    os.remove(backup_file)
                    print(f"Removed backup: {backup_file}")

def test_gui_functionality():
    """Test GUI functionality"""
    print("\n=== GUI Functionality Test ===")
    try:
        import tkinter as tk
        from vehicle_replacer import BatchVehicleReplacerGUI
        
        root = tk.Tk()
        app = BatchVehicleReplacerGUI(root)
        
        print("GUI launched successfully!")
        print("\nManual testing suggestions:")
        print("1. Click 'Quick Setup (Austauchen)' to auto-detect files")
        print("2. Test 'Preview Template' functionality")
        print("3. Add/remove target files manually")
        print("4. Test 'Start Batch Replace' with small file set")
        print("5. Verify progress tracking and logging")
        print("\nClose the GUI window when testing is complete.")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"GUI test failed: {str(e)}")
        return False

def test_integration_with_main_editor():
    """Test integration with main YAML editor"""
    print("\n=== Integration Test ===")
    try:
        import tkinter as tk
        from YamlChange_noQT import YamlEditorApp
        
        root = tk.Tk()
        app = YamlEditorApp(root)
        
        print("Main YAML Editor launched successfully!")
        print("Click 'Batch Vehicle Replacer' button to test integration")
        print("Close the window when testing is complete.")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Batch Vehicle Replacer Test Suite")
    print("=" * 40)
    
    # Run batch functionality test
    success = test_batch_vehicle_replacer()
    
    if success:
        print("\n✓ Batch functionality test passed!")
        
        # Ask for GUI test
        response = input("\nRun GUI test? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            test_gui_functionality()
        
        # Ask for integration test
        response = input("\nRun integration test? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            test_integration_with_main_editor()
    else:
        print("\n✗ Batch functionality test failed!")
    
    print("\nTest suite completed.")
