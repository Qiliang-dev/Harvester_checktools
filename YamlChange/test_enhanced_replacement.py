#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test enhanced vehicle replacement with file renaming and field synchronization
"""

import os
import shutil
import yaml
from vehicle_replacer import BatchVehicleReplacer

def test_enhanced_replacement():
    """Test the enhanced replacement functionality"""
    print("=== Testing Enhanced Vehicle Replacement ===")
    
    # Create test template
    template_content = """Version: '1.5'
TestCase:
  Name: 2025_09_19_134119_H022296_E
  Description: Template File
  Time: 19/09/2025 13:41:19
  TestNotes: ''
  Filename: 2025_09_19_134119_H022296_E.blf
  Vehicle:
    CarModel:
      Model: BMW
      Variant: NA0
      VIN: WBA31JB00RH022296
      RHD: false
    Engine:
      State: Running
      Type: Electric
    OptionalEquipment:
      '***':
        Name: Ausleseterminal
        Description: null
"""
    
    # Create test target files
    target1_content = """Version: '1.4'
TestCase:
  Name: 2025_04_26_000924_DA00097_A
  Description: Target File 1
  Time: 26/04/2025 00:09:24
  TestNotes: ''
  Filename: 2025_04_26_000924_DA00097_A.blf
  Vehicle:
    CarModel:
      Model: BMW
      Variant: NA5
      VIN: WBA31HR000DA22097
      RHD: false
    Engine:
      State: Stopped
      Type: Electric
    OptionalEquipment:
      S248A:
        Name: Lenkradheizung
        Description: null
"""
    
    template_file = "test_template_H022296_E.yaml"
    target_file = "test_target_DA00097_A.yaml"
    
    # Use proper naming format
    template_file = "2025_09_19_134119_H022296_E.yaml"
    target_file = "2025_04_26_000924_DA00097_A.yaml"
    
    try:
        # Write test files
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(target1_content)
        
        print(f"Created template: {template_file}")
        print(f"Created target: {target_file}")
        
        # Test enhanced replacement
        replacer = BatchVehicleReplacer()
        
        print("\n1. Testing filename extraction...")
        template_suffix = replacer.extract_vehicle_suffix(template_file)
        print(f"   Template suffix: {template_suffix}")
        
        target_suffix = replacer.extract_vehicle_suffix(target_file)
        print(f"   Target suffix: {target_suffix}")
        
        print("\n2. Testing filename validation...")
        template_valid = replacer.validate_filename_format(template_file)
        target_valid = replacer.validate_filename_format(target_file)
        print(f"   Template valid: {template_valid}")
        print(f"   Target valid: {target_valid}")
        
        print("\n3. Testing new filename generation...")
        new_filename = replacer.generate_new_filename(target_file, template_suffix)
        print(f"   New filename: {new_filename}")
        
        print("\n4. Testing enhanced batch replacement...")
        results = replacer.perform_batch_replacement(template_file, [target_file])
        
        # Check results
        if results[0]['status'] == 'Success':
            print("   ✓ Replacement successful")
            print(f"   ✓ File renamed: {results[0]['file']} → {results[0]['new_file']}")
            
            # Verify the new file exists
            new_file_path = results[0]['new_file']
            if os.path.exists(new_file_path):
                print(f"   ✓ New file exists: {new_file_path}")
                
                # Check YAML content
                with open(new_file_path, 'r', encoding='utf-8') as f:
                    new_data = yaml.load(f, Loader=yaml.FullLoader)
                
                # Verify TestCase fields
                expected_name = os.path.splitext(new_file_path)[0]
                expected_filename = f"{expected_name}.blf"
                
                if new_data['TestCase']['Name'] == expected_name:
                    print(f"   ✓ TestCase.Name updated: {new_data['TestCase']['Name']}")
                else:
                    print(f"   ✗ TestCase.Name incorrect: {new_data['TestCase']['Name']}")
                
                if new_data['TestCase']['Filename'] == expected_filename:
                    print(f"   ✓ TestCase.Filename updated: {new_data['TestCase']['Filename']}")
                else:
                    print(f"   ✗ TestCase.Filename incorrect: {new_data['TestCase']['Filename']}")
                
                # Verify Vehicle content
                if new_data['TestCase']['Vehicle']['CarModel']['VIN'] == 'WBA31JB00RH022296':
                    print("   ✓ Vehicle content replaced successfully")
                else:
                    print("   ✗ Vehicle content not replaced")
                
                # Check special key handling
                if '***' in new_data['TestCase']['Vehicle']['OptionalEquipment']:
                    print("   ✓ Special characters in keys handled correctly")
                else:
                    print("   ✗ Special characters in keys not handled")
            
            # Check backup
            backup_dir = "yaml_backup"
            if os.path.exists(backup_dir):
                backup_files = os.listdir(backup_dir)
                if backup_files:
                    print(f"   ✓ Backup created: {backup_files[0]}")
                else:
                    print("   ✗ No backup files found")
            else:
                print("   ✗ Backup directory not created")
        
        else:
            print(f"   ✗ Replacement failed: {results[0]['message']}")
        
        print("\n✓ Enhanced replacement test completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        cleanup_files = [template_file, target_file]
        
        # Add potential new file
        if 'new_file_path' in locals():
            cleanup_files.append(new_file_path)
        
        # Clean up files
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed: {file}")
        
        # Clean up backup directory
        if os.path.exists("yaml_backup"):
            shutil.rmtree("yaml_backup")
            print("Removed: yaml_backup directory")

if __name__ == "__main__":
    test_enhanced_replacement()
