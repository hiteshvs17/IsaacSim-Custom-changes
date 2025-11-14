#!/bin/bash
set -e

# Setting current dir and Downloads dir
CURR_DIR="$(pwd)"
DOWNLOADS_DIR="${HOME}/Downloads"
change_arg_in_yaml_py="$CURR_DIR/change_arg_in_yaml.py"
create_yaml_py="$CURR_DIR/create_ira_yaml.py"

# --- Function to set params inside config files --- #
function set_flag_in_yaml {
    # Check that all required arguments were provided.
    if [[ $# -ne 3 ]]; then
        echo "Usage: set_flag_in_yaml <yaml_filename> <param> <value>"
        return 1
    fi
    # Run the python script to change the specified param.
    python3 $change_arg_in_yaml_py -f $1 -p $2 -v $3
}

# --- Function to create new config file for IsaacSim Replicator --- #
function create_yaml {
    # Check that all required arguments were provided.
    if [[ $# -ne 2 ]]; then
        echo "Usage: create_yaml <path_to_scene> <path_to_command_file>"
        return 1
    fi
    # Run the python script to change the specified param.
    python3 $create_yaml_py --scene_path $1 --command_file $2
}

# Process 1: Start the warehouse gen app, user will save the files for path and json
echo "Running warehouse_generator.py..."
python3 warehouse_generator.py

echo "File generation complete. Finding latest files in ${CURR_DIR}..."

# Read the latest saved files and assign those paths to variables
# Finds the latest file ending in .json, sorts by time (newest first), and takes the top one.
LAYOUT_JSON_PATH=$(
    find "$CURR_DIR" -maxdepth 1 -type f -name "*.json" -printf '%T@ %p\n' | 
    sort -n | 
    tail -1 | 
    cut -d' ' -f2-
)

# Finds the latest file ending in .txt, sorts by time (newest first), and takes the top one.
HUMAN_MOTION_TXT_PATH=$(
    find "$CURR_DIR" -maxdepth 1 -type f -name "*.txt" -printf '%T@ %p\n' | 
    sort -n | 
    tail -1 | 
    cut -d' ' -f2-
)

# Exception - path(s) not available
if [ -z "$LAYOUT_JSON_PATH" ] || [ -z "$HUMAN_MOTION_TXT_PATH" ]; then
    echo "Error: Could not find one or both of the latest .json or .txt files."
    exit 1
fi

# Update yaml with the layout json path
set_flag_in_yaml place_racks.yaml json_file_path $LAYOUT_JSON_PATH

# Process 2: Show the layout in usd in IsaacSim (Launch the place racks script)
echo "Opening the layout in IsaacSim for visualization, editing..."
./python.sh ./place_racks_startup.py

# User will save the usd location, get that
echo "Finding latest .usd file in ${DOWNLOADS_DIR}..."
USD_FILE_PATH=$(
    find "$DOWNLOADS_DIR" -maxdepth 1 -type f -name "*.usd" -printf '%T@ %p\n' | 
    sort -n | 
    tail -1 | 
    cut -d' ' -f2-
)

# File not found error
if [ -z "$USD_FILE_PATH" ]; then
    echo "Error: Could not find any .usd file in $DOWNLOADS_DIR."
    exit 1
fi

# Process 3: Launch the same file in full isaacsim app to promt user to create navmaesh
echo Opening the .usd in full application to create NavMesh Volume
echo Steps to create NavMesh Volume:
echo 1. Create -> Navigation -> NavMesh Volume
echo 2. Inside the Property tab for the NavMesh Volume, Click on Bake NavMesh
./isaac-sim.sh --exec "open_stage.py file://$USD_FILE_PATH"

# User will save to new location (hopefully same file, but we can be extra careful)
NEW_USD_FILE_PATH=$(
    find "$DOWNLOADS_DIR" -maxdepth 1 -type f -name "*.usd" -printf '%T@ %p\n' | 
    sort -n | 
    tail -1 | 
    cut -d' ' -f2-
)

# Process 4: Update this usd location, human motion text, in the isaac yaml file
create_yaml $NEW_USD_FILE_PATH $HUMAN_MOTION_TXT_PATH
ISAAC_YAML_FILE_PATH="$DOWNLOADS_DIR/test_case.yaml"

echo "--- Process 4: Updating YAML Configuration ---"

if [ ! -f "$ISAAC_YAML_FILE_PATH" ]; then
    echo "Error: YAML configuration file not found at $ISAAC_YAML_FILE_PATH. Cannot proceed."
    exit 1
fi

echo "Final configuration set in YAML:"
echo "  USD Path: $NEW_USD_FILE_PATH"
echo "  Motion Path: $HUMAN_MOTION_TXT_PATH"
echo "-------------------------------------------"


# Process 5: Launch isaac sim with the agent sdg default yaml path as the path above
./launch-isaac-sim.sh -config $ISAAC_YAML_FILE_PATH

