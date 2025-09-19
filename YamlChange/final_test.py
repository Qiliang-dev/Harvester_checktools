#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final test with real files
"""

from vehicle_replacer import BatchVehicleReplacer
import os

def main():
    replacer = BatchVehicleReplacer()
    
    template_file = 'Austauchen/2025_09_19_134119_H022296_E.yaml'
    target_file = 'Austauchen/2025_04_26_000945_DA00097_A.yaml'  # Use a different one
    
    print("=== Final Test with Real Files ===")
    print(f"Template: {template_file}")
    print(f"Target: {target_file}")
    
    # Extract suffixes
    template_suffix = replacer.extract_vehicle_suffix(os.path.basename(template_file))
    target_suffix = replacer.extract_vehicle_suffix(os.path.basename(target_file))
    
    print(f"Template suffix: {template_suffix}")
    print(f"Target suffix: {target_suffix}")
    
    # Predict new filename
    new_filename = replacer.generate_new_filename(os.path.basename(target_file), template_suffix)
    print(f"Expected new filename: {new_filename}")
    
    # Perform replacement
    results = replacer.perform_batch_replacement(template_file, [target_file])
    
    if results[0]['status'] == 'Success':
        print(f"✓ Success: {results[0]['file']} → {results[0]['new_file']}")
        
        # Check if new file exists in Austauchen
        new_file_path = os.path.join('Austauchen', results[0]['new_file'])
        if os.path.exists(new_file_path):
            print(f"✓ New file created: {new_file_path}")
        else:
            print(f"✗ New file not found: {new_file_path}")
    else:
        print(f"✗ Failed: {results[0]['message']}")

if __name__ == "__main__":
    main()
