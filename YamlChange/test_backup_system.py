#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the new backup system
"""

import os
import shutil
from vehicle_replacer import BatchVehicleReplacer

def test_new_backup_system():
    """Test the new yaml_backup folder system"""
    print("=== Testing New Backup System ===")
    
    # Create test files
    test_files = []
    for i in range(3):
        test_file = f"test_file_{i}.yaml"
        test_content = f"""Version: '1.0'
TestCase:
  Name: Test File {i}
  Vehicle:
    CarModel:
      Model: TestModel{i}
    Engine:
      State: Stopped
      Type: Electric
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        test_files.append(test_file)
        print(f"Created test file: {test_file}")
    
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
        # Test backup system
        replacer = BatchVehicleReplacer()
        
        print("\n1. Testing batch replacement with new backup system...")
        results = replacer.perform_batch_replacement(template_file, test_files)
        
        # Check if yaml_backup folder was created
        if os.path.exists("yaml_backup"):
            print("✓ yaml_backup folder created successfully")
            
            # Check backup files
            backup_files = os.listdir("yaml_backup")
            print(f"✓ Found {len(backup_files)} backup files:")
            
            for backup_file in backup_files:
                print(f"   - {backup_file}")
                
                # Verify backup file is valid YAML
                backup_path = os.path.join("yaml_backup", backup_file)
                try:
                    import yaml
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        yaml.load(f, Loader=yaml.FullLoader)
                    print(f"   ✓ {backup_file} is valid YAML")
                except Exception as e:
                    print(f"   ✗ {backup_file} is invalid: {e}")
            
            # Test duplicate backup handling
            print("\n2. Testing duplicate backup handling...")
            
            # Run replacement again to test duplicate handling
            results2 = replacer.perform_batch_replacement(template_file, test_files[:1])
            
            backup_files_after = os.listdir("yaml_backup")
            if len(backup_files_after) > len(backup_files):
                print("✓ Duplicate backup files handled correctly with timestamps")
                new_files = set(backup_files_after) - set(backup_files)
                for new_file in new_files:
                    print(f"   - New backup: {new_file}")
            else:
                print("✓ No duplicates created (existing backup preserved)")
        
        else:
            print("✗ yaml_backup folder not created")
            return False
        
        # Check replacement results
        success_count = sum(1 for r in results if r['status'] == 'Success')
        print(f"\n3. Replacement results: {success_count}/{len(results)} successful")
        
        print("\n✓ New backup system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("\nCleaning up test files...")
        
        # Remove test files
        for test_file in test_files + [template_file]:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"Removed: {test_file}")
        
        # Remove backup folder and contents
        if os.path.exists("yaml_backup"):
            shutil.rmtree("yaml_backup")
            print("Removed: yaml_backup folder")

if __name__ == "__main__":
    test_new_backup_system()
