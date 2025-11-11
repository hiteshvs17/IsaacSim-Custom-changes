import json
import yaml
import os
from isaacsim import SimulationApp

# Path to the config file from which all paths are read
yaml_config_path = "./place_racks.yaml"

# Read YAML configuration
print(f"[RACK PLACER] Reading YAML config: {yaml_config_path}")
with open(yaml_config_path, 'r') as f:
    config = yaml.safe_load(f)

# Get JSON file path from YAML
json_file_path = config.get("json_file_path", "")

# Read JSON to determine warehouse type
print(f"[RACK PLACER] Reading JSON: {json_file_path}")
with open(json_file_path, 'r') as f:
    data = json.load(f)

warehouse_type = data.get("warehouse_type","small").lower()
scale = data["scale"]
racks = data["racks"]

# Determine warehouse USD file based on warehouse type
warehouse_usd_file = config["warehouse_usd_file"].get(warehouse_type, "")
if not warehouse_usd_file or warehouse_usd_file == "default path":
    raise ValueError(f"No valid warehouse USD file path found for warehouse type: {warehouse_type}")

# Determine rack asset file (you can extend this logic based on rack type)
rack_asset_file = config["rack_asset_file"].get("narrow_standard", "")
if not rack_asset_file or rack_asset_file == "default path":
    raise ValueError(f"No valid rack asset file path found")

print(f"[RACK PLACER] Warehouse type: {warehouse_type}")
print(f"[RACK PLACER] Warehouse USD: {warehouse_usd_file}")
print(f"[RACK PLACER] Rack asset: {rack_asset_file}")

# Launch Isaac Sim in headless mode (or with GUI)
simulation_app = SimulationApp({
    "headless": False,  # Set to True for no GUI
    "width": 1920,
    "height": 1080,
})

import isaacsim.core.utils.prims as prim_utils
from pxr import Gf, UsdGeom
import omni.usd
import carb
import time

environment_prim_path = "/World"

print("[RACK PLACER] Starting...")

# Open warehouse
print(f"[RACK PLACER] Opening warehouse: {warehouse_usd_file}")
omni.usd.get_context().open_stage(warehouse_usd_file)

# Wait for stage to load
simulation_app.update()
time.sleep(1)

print(f"[RACK PLACER] Placing {len(racks)} racks...")

# Create racks parent
racks_parent_path = f"{environment_prim_path}/Racks"
if not prim_utils.get_prim_at_path(environment_prim_path):
    prim_utils.create_prim(environment_prim_path, "Xform")
if not prim_utils.get_prim_at_path(racks_parent_path):
    prim_utils.create_prim(racks_parent_path, "Xform")

# Place each rack
successful = 0
for i, rack in enumerate(racks):
    x_m = rack["x"]
    y_m = rack["y"] 
    rack_path = f"{racks_parent_path}/Rack_{i:03d}"
    
    try:
        omni.kit.commands.execute('CreateReference',
            usd_context=omni.usd.get_context(),
            path_to=rack_path,
            asset_path=rack_asset_file,
            instanceable=True
        )
        
        simulation_app.update()
        
        rack_prim = prim_utils.get_prim_at_path(rack_path)
        if rack_prim:
            xformable = UsdGeom.Xformable(rack_prim)
            xformable.AddTranslateOp().Set(Gf.Vec3d(x_m, y_m, 0.0))
            
            if rack["rotation"] != 0:
                xformable.AddRotateZOp().Set(rack["rotation"])
            
            # xformable.AddScaleOp().Set(Gf.Vec3f(
            #     rack["width_m"], 
            #     rack["depth_m"], 
            #     1.0
            # ))
            
            successful += 1
            print(f"[RACK PLACER] ✓ Placed Rack_{i:03d} at ({x_m:.2f}, {y_m:.2f})")
        else:
            print(f"[RACK PLACER] ✗ Failed to get prim for Rack_{i:03d}")
            
    except Exception as e:
        print(f"[RACK PLACER] ✗ Error with Rack_{i:03d}: {e}")

print(f"[RACK PLACER] Complete! Placed {successful}/{len(racks)} racks.")

# Keep the simulation running (remove these lines if you want it to exit immediately)
print("[RACK PLACER] Simulation running. Close window to exit.")
while simulation_app.is_running():
    simulation_app.update()

# Cleanup
simulation_app.close()