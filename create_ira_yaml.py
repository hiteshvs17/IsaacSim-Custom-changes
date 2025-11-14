#!/usr/bin/python3
# config_updater.py

import argparse
import yaml
import os
from typing import Any, Dict, List

# 1. Define the YAML content as a string 
YAML_CONFIG_STRING = """
isaacsim.replicator.agent:
  version: 0.5.0
  global:
    seed: 123
    simulation_length: 750
  scene:
    asset_path: # This will be replaced
  sensor:
    camera_num: 1
  character:
    asset_path: https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/People/Characters/
    command_file: # This will be replaced
    filters: ''
    num: 1
  robot:
    command_file: default_robot_command.txt
    nova_carter_num: 0
    transporter_num: 0
    write_data: false
  replicator:
    writer: IRABasicWriter
    parameters:
      object_info_bounding_box_2d_tight: false
      output_dir: /home/user/ReplicatorResult
      # ... (rest of the parameters)
"""

def get_nested_key(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Helper function to traverse the nested dictionary to the parent of the final key."""
    current = data
    for key in keys[:-1]:
        if key not in current:
            raise KeyError(f"Key '{key}' not found in the configuration path.")
        current = current[key]
    return current


def update_and_save_config(scene_asset_path: str, char_command_file: str):
    """
    Loads the original configuration, updates the specified values,
    and saves the new configuration to the Downloads folder.
    """
    # Load the YAML content from the string (simulating reading from a file)
    config = yaml.full_load(YAML_CONFIG_STRING)

    # --- 1. Update scene.asset_path ---
    ROOT_KEY = "isaacsim.replicator.agent"
    NESTED_PATH_SCENE = "scene.asset_path" 
    
    # Start traversal from the dictionary that is the value of the ROOT_KEY
    start_config = config.get(ROOT_KEY)
    if start_config is None:
        print(f"Error: Root key '{ROOT_KEY}' not found in the configuration.")
        return

    path_scene_list = NESTED_PATH_SCENE.split('.')
    try:
        # Pass the sub-dictionary and the list of nested keys to the helper function
        parent_dict = get_nested_key(start_config, path_scene_list) 
        parent_dict[path_scene_list[-1]] = scene_asset_path
        print(f"Updated scene.asset_path to: {scene_asset_path}")
    except KeyError as e:
        print(f"Error updating scene.asset_path: {e}")
        return

    # --- 2. Update character.command_file ---
    NESTED_PATH_CHAR = "character.command_file"
    path_char_list = NESTED_PATH_CHAR.split('.')
    try:
        # Pass the sub-dictionary and the list of nested keys to the helper function
        parent_dict = get_nested_key(start_config, path_char_list)
        parent_dict[path_char_list[-1]] = char_command_file
        print(f"Updated character.command_file to: {char_command_file}")
    except KeyError as e:
        print(f"Error updating character.command_file: {e}")
        return

    # --- 3. Save the new configuration file ---
    
    # Get the user's home directory and construct the output path
    downloads_dir = os.path.expanduser('~/Downloads')
    new_filename = os.path.join(downloads_dir, 'test_case.yaml')
    
    # Save the updated dictionary back to a new YAML file
    # The 'sort_keys=False' is important to keep the original parameter order
    with open(new_filename, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    
    print(f"\n✅ Successfully created new config file at: {new_filename}")


def main():
    parser = argparse.ArgumentParser(description='Create a new YAML file based on an existing config, with updated scene and character paths.')
    parser.add_argument(
        '--scene_path', 
        action="store", 
        dest="scene_asset_path", 
        required=True, 
        type=str, 
        help='New value for scene.asset_path.'
    )
    parser.add_argument(
        '--command_file', 
        action="store", 
        dest="char_command_file", 
        required=True, 
        type=str, 
        help='New value for character.command_file.'
    )
    args = parser.parse_args()

    update_and_save_config(args.scene_asset_path, args.char_command_file)


if __name__ == "__main__":
    main()