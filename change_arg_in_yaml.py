#!/bin/python3
# Copyright (c) 2024-2025 Piaggio Fast Forward (PFF), Inc.
# All Rights Reserved. Reproduction, publication,
# or re-transmittal not allowed without written permission of PFF, Inc.

"""
Script to change a specific argument in a yaml.
Pure bash methods usually remove all the whitespace from the yaml which is annoying for git tracking.
"""

import argparse
import re
import yaml

def read_parameter(filename:str, param_name:str):
    """
    Find and return the value of the parameter in the given yaml file.
    @param filename: The path to the file.
    @param param_name: The name of the parameter to search for. If nested in a subsection, provide full path as section1.section2.param
    """
    # If the param name has one or more "." in it, treat as nested param.
    param_tree = param_name.split(".")
    # Read the file and find the param.
    with open(filename, 'r') as f:
        config = yaml.full_load(f)
        # Abuse dynamic typing to recurse through the param tree to the final value.
        for p in param_tree:
            try:
                config = config[p]
            except:
                print(f"Exception while searching for parameter '{param_name}' from '{filename}', at stage '{p}' in {config}")
                return None
        print(f"Read parameter {param_name} as {config} from {filename}")
        return config
    # Should not make it here.
    return None

def replace_parameter(filename:str, param_name:str, new_value:str):
    """
    Replaces the line containing a specific parameter name with a new value in the given file.
    @param filename: The path to the file to be modified.
    @param param_name: The name of the parameter to search for. If nested in a subsection, provide full path as section1.section2.param
    @param new_value: The new value to replace the existing value for the parameter.

    Example usage:
    replace_parameter("config/known_paths.yaml", "spoof_kpc_bag_as_kpt", "true")
    replace_parameter("config/features.yaml", "kilo-v1.lidar_mapper", "false")
    replace_parameter("config/sensor_manager.yaml", "replay_data_dir", "\"/opt/pff/storage/replay/\"")
    """
    # Convert to lowercase string if another type is passed.
    if type(new_value) is not str:
        new_value = str(new_value).lower()
    # If the param name has one or more "." in it, treat as nested param. Also accept ":" as separator.
    param_tree = param_name.replace(':', '.').split(".")
    # Find the line numbers for each param in the tree, enforcing that they must appear in the same order.
    with open(filename, "r+") as file:
        lines = file.readlines()
        replaced = False
        match_str:str = ""
        for i, line in enumerate(lines):
            # Look for the next param in the tree.
            param_name = param_tree[0]
            # Allow param_name to be only partially complete, missing part at either the beginning or end.
            # So, look for any or no whitespace (\s*), followed by a string with no whitespace which contains param_name (\S*{param_name}\S*), then a colon (:), then anything else (.*).
            search_pattern = fr"^\s*\S*{param_name}\S*:.*$"
            if re.search(search_pattern, line):
                colon_index:int = line.index(":")
                # Since the regex works even for partial param name, fill with true name for output confirmation message.
                match_str += ("" if match_str == "" else ".") + line[:colon_index].strip()
                if len(param_tree) > 1:
                    # If this is not the terminal node, keep searching.
                    param_tree = param_tree[1:]
                    continue
                # Preserve the line's structure, just replacing the arg value.
                # Assume the line is in the format `  param: value # comment`
                if "#" in line:
                    comment_index:int = line.index("#")
                    new_line = line[:colon_index+1] + " " + new_value + " " + line[comment_index:]
                else:
                    # If there is no comment, use the end of the line.
                    new_line = line[:colon_index+1] + " " + new_value + "\n"
                lines[i] = new_line
                replaced = True
                break

        if replaced:
            with open(filename, "w") as file:
                file.writelines(lines)
            print(f"Replaced parameter '{match_str}' with '{new_value}' in {filename}")
        else:
            print(f"Parameter '{param_name}' not found in {filename}")


def main():
    parser = argparse.ArgumentParser(description='Read or modify the value of a parameter in a yaml file')
    parser.add_argument('-f', '--file', action="store", dest="filepath", required=True, type=str, help='Local or global path to the yaml file.')
    parser.add_argument('-p', '--param', action="store", dest="param", required=True, type=str, help='Parameter to change. If nested in a subsection, provide full path as section1.section2.param')
    parser.add_argument('-v', '--value', action="store", dest="value", required=False, type=str, default=None, help='Value to assign the parameter. Omit to just read the value. Enclose strings in escaped quotes, e.g., \\\"new_value\\\"')
    args = parser.parse_args()

    if args.value is None:
        read_parameter(args.filepath, args.param)
    else:
        replace_parameter(args.filepath, args.param, args.value)


if __name__ == "__main__":
    main()
