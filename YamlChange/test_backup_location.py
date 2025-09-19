#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test backup location logic - backup should be in same directory as target file
"""

import os
import shutil
from vehicle_replacer import BatchVehicleReplacer

def test_backup_location():
    """Test that backup is created in the same directory as the target file"""
    print("=== Testing Backup Location Logic ===")
    
    # Create test directory structure
    test_dirs = ["test_dir1", "test_dir2/subdir"]
    test_files = []
    
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test file in each directory
        test_file = os.path.join(test_dir, "test_file.yaml")
        test_content = f"""Version: '1.0'
TestCase:
  Name: Test File in {test_dir}
  Vehicle:
    CarModel:
      Model: TestModel
    Engine:
      State: Stopped
      Type: Electric
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        test_files.append(test_file)
        print(f"Created: {test_file}")
    
    # Create template file
    template_file = "test_template.yaml"
    template_content = """Version: '1.0'
TestCase:
  Name: Template File
  Vehicle:
    CarModel:
      Model: TemplateModel
    Engine:
      State: Running
      Type: Gasoline
"""
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    try:
        # Test backup location logic
        replacer = BatchVehicleReplacer()
        
        print("\n1. Testing batch replacement with location-specific backups...")
        results = replacer.perform_batch_replacement(template_file, test_files)
        
        # Check backup locations
        print("\n2. Verifying backup locations...")
        for test_file in test_files:
            file_dir = os.path.dirname(test_file)
            expected_backup_dir = os.path.join(file_dir, "yaml_backup")
            expected_backup_file = os.path.join(expected_backup_dir, os.path.basename(test_file))
            
            if os.path.exists(expected_backup_dir):
                print(f"✓ Backup directory created: {expected_backup_dir}")
                
                if os.path.exists(expected_backup_file):
                    print(f"✓ Backup file exists: {expected_backup_file}")
                    
                    # Verify backup content
                    try:
                        import yaml
                        with open(expected_backup_file, 'r', encoding='utf-8') as f:
                            backup_data = yaml.load(f, Loader=yaml.FullLoader)
                        print(f"✓ Backup file is valid YAML")
                    except Exception as e:
                        print(f"✗ Backup file invalid: {e}")
                else:
                    print(f"✗ Backup file not found: {expected_backup_file}")
            else:
                print(f"✗ Backup directory not created: {expected_backup_dir}")
        
        # Test the expected directory structure
        print("\n3. Checking directory structure:")
        for test_dir in test_dirs:
            backup_dir = os.path.join(test_dir, "yaml_backup")
            if os.path.exists(backup_dir):
                backup_files = os.listdir(backup_dir)
                print(f"  {test_dir}/")
                print(f"  ├── test_file.yaml")
                print(f"  └── yaml_backup/")
                for backup_file in backup_files:
                    print(f"      └── {backup_file}")
            else:
                print(f"  {test_dir}/ (no backup created)")
        
        print("\n✓ Backup location test completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        
        # Remove template file
        if os.path.exists(template_file):
            os.remove(template_file)
            print(f"Removed: {template_file}")
        
        # Remove test directories and their contents
        for test_dir in ["test_dir1", "test_dir2"]:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
                print(f"Removed: {test_dir}/")

if __name__ == "__main__":
    test_backup_location()
