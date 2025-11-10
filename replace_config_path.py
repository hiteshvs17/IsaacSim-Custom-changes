#!/usr/bin/env python3
"""
Script to add/update custom_path variable in get_default_config_file_path() function.
Usage: python replace_config_path.py /path/to/config/file
"""
import sys
import re
import argparse
from pathlib import Path

TARGET_FILE = "/home/hitesh/isaacsim/extscache/isaacsim.replicator.agent.core-0.5.14+106.5.0/isaacsim/replicator/agent/core/config_file/util.py"

def update_path_in_function(file_path, new_config_path):
    """Add or update custom_path variable in get_default_config_file_path() function."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    inside_function = False
    indent_level = None
    updated_lines = []
    custom_path_exists = False
    custom_path_updated = False
    return_statement_found = False
    function_body_start_index = None
    
    for i, line in enumerate(lines):
        # Check if we're entering the target function
        if re.match(r'^\s*def\s+get_default_config_file_path\s*\(', line):
            inside_function = True
            indent_level = len(line) - len(line.lstrip())
            function_body_start_index = len(updated_lines) + 1
            updated_lines.append(line)
            continue
        
        # If we're inside the function
        if inside_function:
            current_indent = len(line) - len(line.lstrip())
            
            # Check if we've exited the function (dedent or new def/class)
            if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                inside_function = False
            
            # Look for existing custom_path variable
            if inside_function and re.match(r'^\s*custom_path\s*=', line):
                custom_path_exists = True
                custom_path_updated = True
                indent = ' ' * current_indent
                updated_lines.append(f'{indent}custom_path = "{new_config_path}"\n')
                #print(f"✓ Updated existing custom_path to: {new_config_path}")
                continue
            
            # Look for return statement to potentially modify it
            if inside_function and re.match(r'^\s*return\s+', line):
                return_statement_found = True
                
                # If custom_path doesn't exist yet, add it before the return
                if not custom_path_exists:
                    indent = ' ' * current_indent
                    updated_lines.append(f'{indent}custom_path = "{new_config_path}"\n')
                    custom_path_exists = True
                    custom_path_updated = True
                    #print(f"✓ Added custom_path variable: {new_config_path}")
                
                # Modify return statement to return custom_path
                indent = ' ' * current_indent
                updated_lines.append(f'{indent}return custom_path\n')
                #print(f"Updated return statement to return custom_path")
                continue
        
        updated_lines.append(line)
    
    if not custom_path_updated:
        print("Warning: Could not find or update custom_path in the function")
    
    # Write updated content
    with open(file_path, 'w') as f:
        f.writelines(updated_lines)

def main():
    parser = argparse.ArgumentParser(
        description='Add/update custom_path in get_default_config_file_path()'
    )
    parser.add_argument(
        'config_path',
        help='Path to the config file'
    )
    
    args = parser.parse_args()
    config_path = Path(args.config_path)
    
    # Validate config path exists
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    # Get absolute path
    config_path_absolute = config_path.resolve()
    print(f"Updating custom_path to: {config_path_absolute}")
    
    target_file_path = Path(TARGET_FILE)
    
    # Validate target file exists
    if not target_file_path.exists():
        print(f"Error: Target file not found: {target_file_path}")
        sys.exit(1)
    
    try:
        update_path_in_function(target_file_path, str(config_path_absolute))
        print("File updated successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()