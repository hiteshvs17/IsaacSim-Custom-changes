#!/bin/bash
set -e

# Setting current dir and Downloads dir
CURR_DIR="."
DOWNLOADS_DIR="${HOME}/Downloads"

# --- Helper Function for YAML Update (Requires 'sed' utility) ---
update_yaml_config() {
    local usd_path="$1"
    local motion_path="$2"
    local yaml_file="$3"

    echo "Updating YAML config file: $yaml_file"

    sed -i "
        /asset_path:/ c\asset_path: $usd_path
        /command_file:/ c\command_file: $motion_path
    " "$yaml_file"
    echo "YAML update complete."
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
ISAAC_YAML_FILE_PATH="$DOWNLOADS_DIR/demo_motion.yaml"

echo "--- Process 4: Updating YAML Configuration ---"

if [ ! -f "$ISAAC_YAML_FILE_PATH" ]; then
    echo "Error: YAML configuration file not found at $ISAAC_YAML_FILE_PATH. Cannot proceed."
    exit 1
fi

update_yaml_config "$NEW_USD_FILE_PATH" "$HUMAN_MOTION_TXT_PATH" "$ISAAC_YAML_FILE_PATH"
echo "Final configuration set in YAML:"
echo "  USD Path: $NEW_USD_FILE_PATH"
echo "  Motion Path: $HUMAN_MOTION_TXT_PATH"
echo "-------------------------------------------"


# Process 5: Launch isaac sim with the agent sdg default yaml path as the path above
./launch-isaac-sim.sh -config $ISAAC_YAML_FILE_PATH

