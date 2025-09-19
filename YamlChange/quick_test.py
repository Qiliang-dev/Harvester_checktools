#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test of new backup location
"""

from vehicle_replacer import BatchVehicleReplacer
import os

def main():
    # Test with actual files
    replacer = BatchVehicleReplacer()
    template_file = 'Austauchen/2025_09_19_134119_H022296_E.yaml'
    
    # Use one file for testing
    target_files = ['Austauchen/2025_04_26_000924_DA00097_A.yaml']
    
    print('Testing new backup location with real files...')
    print(f'Template: {template_file}')
    print(f'Target: {target_files[0]}')
    
    # Perform replacement
    results = replacer.perform_batch_replacement(template_file, target_files)
    
    if results[0]['status'] == 'Success':
        print('✓ Replacement successful')
        
        # Check if backup was created in Austauchen/yaml_backup/
        backup_dir = 'Austauchen/yaml_backup'
        if os.path.exists(backup_dir):
            print(f'✓ Backup directory created: {backup_dir}')
            backup_files = os.listdir(backup_dir)
            for backup_file in backup_files:
                print(f'  - Backup file: {backup_file}')
        else:
            print('✗ Backup directory not found')
    else:
        print(f'✗ Replacement failed: {results[0]["message"]}')

if __name__ == "__main__":
    main()
