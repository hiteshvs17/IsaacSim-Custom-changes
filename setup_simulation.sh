#!/bin/bash
set -e

# Process 1: Start the warehouse gen app, user will save the files for path and json
python3 warehouse_generator.py

# Read the latest saved files and assign those paths to variables
LAYOUT_JSON_PATH="/path" 
HUMAN_MOTION_TXT_PATH="/another_path"

# Process 2: Show the layout in usd in IsaacSim (Launch the place racks script)
# User will save the usd location, get that
USD_LOCATION="/usd_path" 

# Process 3: Launch the same file in full isaacsim app
# Prompt user to create navmesh
# User will save to new location (hopefully same file, but we can be extra careful)
NEW_USD_LOCATION="/new_usd_path"

# Process 4: Update this usd location, human motion text, in the isaac yaml file
ISAAC_YAML_FILE_PATH="/yaml_path" 

# Process 5: Launch isaac sim with the agent sdg default yaml path as the path above
./launch-isaac-sim.sh -config /home/hitesh/Downloads/demo_motion.yaml

# Cleanup - Remove current motion txt file, json file in current folder. 
