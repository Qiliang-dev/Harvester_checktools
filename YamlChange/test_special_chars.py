#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for special character handling in YAML keys
"""

import os
import yaml
import tempfile
from vehicle_replacer import BatchVehicleReplacer

def test_special_char_handling():
    """Test that special characters in YAML keys are properly handled"""
    print("=== Testing Special Character Handling ===")
    
    # Create test template with special characters
    test_template_content = """Version: '1.0'
TestCase:
  Vehicle:
    CarModel:
      Model: TestTemplate
    OptionalEquipment:
      '***':
        Name: Ausleseterminal
        Description: null
      NormalKey:
        Name: Normal Equipment
        Description: null
    Engine:
      State: Stopped
      Type: Electric
"""

    # Create test target
    test_target_content = """Version: '1.0'
TestCase:
  Vehicle:
    CarModel:
      Model: TestTarget
    OptionalEquipment:
      RegularKey:
        Name: Old Equipment
        Description: null
    Engine:
      State: Running
      Type: Gasoline
"""

    # Write test files
    template_file = "test_template_special.yaml"
    target_file = "test_target_special.yaml"
    
    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(test_template_content)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(test_target_content)
        
        print(f"✓ Created test files: {template_file}, {target_file}")
        
        # Test file loading
        replacer = BatchVehicleReplacer()
        
        print("\n1. Testing file loading...")
        template_data = replacer.load_yaml_file(template_file)
        target_data = replacer.load_yaml_file(target_file)
        print("   ✓ Both files loaded successfully")
        
        # Test Vehicle content extraction
        print("\n2. Testing Vehicle content extraction...")
        template_vehicle = replacer.extract_vehicle_content(template_data)
        print(f"   ✓ Template Vehicle has {len(template_vehicle)} sections")
        
        # Check if special key exists
        if '***' in template_vehicle.get('OptionalEquipment', {}):
            print("   ✓ Special key '***' found in template")
        else:
            print("   ✗ Special key '***' not found in template")
            return False
        
        # Test YAML generation
        print("\n3. Testing YAML generation with special characters...")
        yaml_lines = replacer.generate_vehicle_yaml(template_vehicle, "  ")
        
        # Find the special key line
        special_key_line = None
        for line in yaml_lines:
            if '***' in line and ':' in line:
                special_key_line = line
                break
        
        if special_key_line:
            print(f"   ✓ Special key formatted as: {special_key_line.strip()}")
        else:
            print("   ✗ Special key not found in generated YAML")
            return False
        
        # Test complete replacement
        print("\n4. Testing complete replacement...")
        results = replacer.perform_batch_replacement(template_file, [target_file])
        
        if results[0]['status'] == 'Success':
            print("   ✓ Replacement completed successfully")
        else:
            print(f"   ✗ Replacement failed: {results[0]['message']}")
            return False
        
        # Verify the result
        print("\n5. Verifying result...")
        with open(target_file, 'r', encoding='utf-8') as f:
            result_content = f.read()
        
        # Check if special key is present and properly formatted
        if "'***'" in result_content or '"***"' in result_content:
            print("   ✓ Special key '***' properly preserved in result")
        else:
            print("   ✗ Special key '***' not found in result")
            print("   Result content snippet:")
            lines = result_content.split('\n')
            for i, line in enumerate(lines):
                if 'OptionalEquipment' in line:
                    for j in range(max(0, i-2), min(len(lines), i+10)):
                        print(f"   {j+1:3}: {lines[j]}")
                    break
            return False
        
        # Test that result is valid YAML
        try:
            result_data = yaml.load(result_content, Loader=yaml.FullLoader)
            print("   ✓ Result file is valid YAML")
            
            # Check if the special key is accessible
            result_vehicle = result_data['TestCase']['Vehicle']
            if '***' in result_vehicle.get('OptionalEquipment', {}):
                print("   ✓ Special key '***' is accessible in parsed result")
            else:
                print("   ✗ Special key '***' not accessible in parsed result")
                return False
                
        except Exception as e:
            print(f"   ✗ Result file is not valid YAML: {e}")
            return False
        
        print("\n✓ All tests passed! Special character handling is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        for file in [template_file, target_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Cleaned up: {file}")
            
            # Remove backup files
            backup_pattern = f"{file}.backup_"
            for f in os.listdir('.'):
                if f.startswith(os.path.basename(backup_pattern)):
                    os.remove(f)
                    print(f"Cleaned up backup: {f}")

if __name__ == "__main__":
    test_special_char_handling()
