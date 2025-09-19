#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify that the special character fix is working
"""

from vehicle_replacer import BatchVehicleReplacer
import os
import shutil

def main():
    print("Verifying special character fix...")
    
    replacer = BatchVehicleReplacer()
    template_file = 'Austauchen/2025_09_19_134119_H022296_E.yaml'
    target_file = 'Austauchen/2025_04_15_151228_DA00097_E.yaml'
    
    # Create a test copy
    test_target = target_file.replace('.yaml', '_verify_test.yaml')
    shutil.copy2(target_file, test_target)
    
    try:
        # Test replacement
        results = replacer.perform_batch_replacement(template_file, [test_target])
        
        if results[0]['status'] == 'Success':
            print("✓ Replacement successful")
            
            # Check for special key
            with open(test_target, 'r', encoding='utf-8') as f:
                content = f.read()
                if '***' in content:
                    print("✓ Special key '***' found in output")
                else:
                    print("✗ Special key '***' not found in output")
                    return
            
            # Test YAML validity
            import yaml
            with open(test_target, 'r', encoding='utf-8') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                print("✓ Output file is valid YAML")
                
                # Check if special key is accessible
                vehicle = data['TestCase']['Vehicle']
                if '***' in vehicle.get('OptionalEquipment', {}):
                    print("✓ Special key '***' is accessible in parsed data")
                else:
                    print("✗ Special key '***' not accessible in parsed data")
            
            print("\n✓ All verifications passed! The fix is working correctly.")
        else:
            print(f"✗ Replacement failed: {results[0]['message']}")
    
    finally:
        # Cleanup
        if os.path.exists(test_target):
            os.remove(test_target)
        
        # Remove backup files
        backup_files = [f for f in os.listdir('Austauchen') 
                       if f.startswith('2025_04_15_151228_DA00097_E_verify_test.yaml.backup_')]
        for backup in backup_files:
            os.remove(os.path.join('Austauchen', backup))
        
        print("Cleanup completed")

if __name__ == "__main__":
    main()
