#!/usr/bin/env python3
"""
Warehouse Rack Layout Designer for Ubuntu
A specialized GUI tool for designing warehouse rack layouts with precise dimensions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math
from PIL import Image, ImageDraw

class Rack:
    """Represents a single rack with position and dimensions"""
    def __init__(self, x, y, width_m, depth_m, rotation=0, rack_type="SmallRack"):
        self.x = x  # Canvas coordinates
        self.y = y
        self.width_m = width_m  # Real-world meters
        self.depth_m = depth_m
        self.rotation = rotation
        self.rack_type = rack_type
        self.canvas_id = None
        
    def to_dict(self, origin_x_m, origin_y_m, scale):
        """Convert to dict with world coordinates relative to origin"""
        # Convert canvas pixels to meters
        x_m = self.x / scale
        y_m = self.y / scale
        
        # Transform to world coordinates (origin-relative)
        world_x = x_m - origin_x_m
        world_y = y_m - origin_y_m
        
        # Swap x and y for the JSON output
        return {
            'type': self.rack_type,
            'x': round(world_y, 3),  # Canvas Y becomes world X
            'y': round(world_x, 3),  # Canvas X becomes world Y
            'width_m': self.width_m,
            'depth_m': self.depth_m,
            'rotation': self.rotation
        }
    
    @staticmethod
    def from_dict(data, origin_x_m, origin_y_m, scale):
        """Create rack from dict with world coordinates"""
        # Swap back: JSON x is canvas y, JSON y is canvas x
        world_x = data['y']  # JSON Y becomes canvas X
        world_y = data['x']  # JSON X becomes canvas Y
        
        # Convert from world coordinates to canvas coordinates
        x_m = world_x + origin_x_m
        y_m = world_y + origin_y_m
        
        x_px = x_m * scale
        y_px = y_m * scale
        
        return Rack(x_px, y_px, data['width_m'], 
                   data['depth_m'], data.get('rotation', 0),
                   data.get('type', 'SmallRack'))


class WarehouseDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Warehouse Rack Layout Designer")
        self.root.geometry("1400x900")
        
        # Scale: pixels per meter
        self.scale = 50  # 50 pixels = 1 meter
        
        # Warehouse presets (width, height in meters)
        self.warehouse_presets = {
            "Small": (30, 20),
            "Big": (54, 32),
            "Factory": (60, 34),
            "Custom": (40, 30)
        }
        
        # Default warehouse dimensions
        self.warehouse_width_m = 30
        self.warehouse_height_m = 20
        
        # World origin (in meters from top-left corner)
        self.origin_x_m = 15  # Default to center
        self.origin_y_m = 10
        
        # Racks storage
        self.racks = []
        self.selected_rack = None
        self.selected_rack_idx = None
        
        # Path waypoints storage
        self.waypoints = []
        self.path_lines = []
        self.waypoint_markers = []
        
        # Drawing state
        self.mode = "single"  # single, row, grid, select, path
        self.drag_start = None
        self.temp_line = None
        
        # Preset rack dimensions (in meters)
        self.rack_presets = {
            "SmallRack": (2.0, 0.96),
            "Custom": (1.0, 1.0)
        }
        
        self.setup_ui()
        self.update_warehouse_size()

    def load_preset_list(self):
        """Load list of preset template files"""
        self.preset_files = []
        presets_dir = "presets"
        
        # Check if presets directory exists
        import os
        if os.path.exists(presets_dir) and os.path.isdir(presets_dir):
            # Get all JSON files in presets directory
            for file in os.listdir(presets_dir):
                if file.endswith('.json'):
                    self.preset_files.append(file.replace('.json', ''))
        
        # Sort alphabetically
        self.preset_files.sort()

    def refresh_preset_list(self):
        """Refresh the preset list"""
        self.load_preset_list()
        self.preset_combo['values'] = self.preset_files
        if self.preset_files:
            self.preset_combo.current(0)
        messagebox.showinfo("Success", f"Found {len(self.preset_files)} preset(s)")

    def load_preset_template(self):
        """Load a preset template"""
        if not self.preset_files:
            messagebox.showwarning("Warning", "No presets found in 'presets' folder")
            return
        
        preset_name = self.preset_combo.get()
        if not preset_name:
            messagebox.showwarning("Warning", "Please select a preset")
            return
        
        import os
        filename = os.path.join("presets", preset_name + ".json")
        
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Preset file not found: {filename}")
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear existing
            self.canvas.delete('all')
            self.racks.clear()
            self.waypoints.clear()
            self.path_lines.clear()
            self.waypoint_markers.clear()
            
            # Load settings (same as load_layout)
            self.scale = data.get('scale', 50)
            self.scale_var.set(str(self.scale))
            
            self.warehouse_width_m = data.get('warehouse_width_m', 40)
            self.warehouse_height_m = data.get('warehouse_height_m', 30)
            self.wh_width_var.set(str(self.warehouse_width_m))
            self.wh_height_var.set(str(self.warehouse_height_m))
            
            warehouse_type = data.get('warehouse_type', 'Custom')
            self.warehouse_var.set(warehouse_type)
            
            origin = data.get('world_origin', {'x': self.warehouse_width_m/2, 
                                            'y': self.warehouse_height_m/2})
            self.origin_x_m = origin['x']
            self.origin_y_m = origin['y']
            self.origin_x_var.set(str(self.origin_x_m))
            self.origin_y_var.set(str(self.origin_y_m))
            
            # Load racks
            for rack_data in data['racks']:
                rack = Rack.from_dict(rack_data, self.origin_x_m, 
                                    self.origin_y_m, self.scale)
                self.racks.append(rack)
            
            # Load path
            if 'path' in data and 'waypoints' in data['path']:
                self.waypoints_from_dict(data['path']['waypoints'])
            
            self.update_warehouse_size()
            messagebox.showinfo("Success", f"Preset '{preset_name}' loaded\n"
                            f"Racks: {len(self.racks)}\n"
                            f"Waypoints: {len(self.waypoints)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {e}")
        
    def setup_ui(self):
        """Create the GUI layout"""
        # Top toolbar
        toolbar = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="Scale:").pack(side=tk.LEFT, padx=5)
        self.scale_var = tk.StringVar(value="50")
        scale_spin = ttk.Spinbox(toolbar, from_=10, to=200, width=8,
                                textvariable=self.scale_var, 
                                command=self.update_scale)
        scale_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="px/m").pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, 
                                                        fill=tk.Y, padx=10)
        
        ttk.Button(toolbar, text="Save Test Case", 
                  command=self.save_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Load Test Case", 
                  command=self.load_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Export Path TXT", 
                  command=self.export_path_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Export PNG", 
                  command=self.export_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Tools with scrollbar
        left_panel_container = ttk.Frame(main_container, width=250)
        left_panel_container.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        left_panel_container.pack_propagate(False)

        # Create canvas for scrolling
        left_canvas = tk.Canvas(left_panel_container, width=250)
        left_scrollbar = ttk.Scrollbar(left_panel_container, orient=tk.VERTICAL, command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create frame inside canvas
        left_panel = ttk.Frame(left_canvas)
        left_canvas_window = left_canvas.create_window((0, 0), window=left_panel, anchor=tk.NW)

        # Update scrollregion when frame changes size
        def configure_scroll_region(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            
        left_panel.bind('<Configure>', configure_scroll_region)

        # Bind mousewheel for scrolling
        def on_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        left_canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
        left_canvas.bind_all("<Button-4>", lambda e: left_canvas.yview_scroll(-1, "units"))  # Linux scroll up
        left_canvas.bind_all("<Button-5>", lambda e: left_canvas.yview_scroll(1, "units"))   # Linux scroll down
        
        # Warehouse size selection
        warehouse_frame = ttk.LabelFrame(left_panel, text="Warehouse Size", padding=10)
        warehouse_frame.pack(fill=tk.X, pady=5)
        
        self.warehouse_var = tk.StringVar(value="Small")
        for preset in self.warehouse_presets.keys():
            ttk.Radiobutton(warehouse_frame, text=preset, value=preset,
                          variable=self.warehouse_var,
                          command=self.update_warehouse_preset).pack(anchor=tk.W, pady=2)
        
        # Custom warehouse dimensions
        wh_dim_frame = ttk.Frame(warehouse_frame)
        wh_dim_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(wh_dim_frame, text="Width (m):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.wh_width_var = tk.StringVar(value="30")
        ttk.Entry(wh_dim_frame, textvariable=self.wh_width_var, width=8).grid(
            row=0, column=1, pady=2)
        
        ttk.Label(wh_dim_frame, text="Height (m):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.wh_height_var = tk.StringVar(value="20")
        ttk.Entry(wh_dim_frame, textvariable=self.wh_height_var, width=8).grid(
            row=1, column=1, pady=2)
        
        ttk.Button(wh_dim_frame, text="Apply Size",
                  command=self.apply_warehouse_size).grid(
                      row=2, column=0, columnspan=2, pady=5)
        
        # World origin settings
        origin_frame = ttk.LabelFrame(left_panel, text="World Origin (meters)", padding=10)
        origin_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(origin_frame, text="Origin X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.origin_x_var = tk.StringVar(value="15.0")
        ttk.Entry(origin_frame, textvariable=self.origin_x_var, width=10).grid(
            row=0, column=1, pady=2)
        
        ttk.Label(origin_frame, text="Origin Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.origin_y_var = tk.StringVar(value="10.0")
        ttk.Entry(origin_frame, textvariable=self.origin_y_var, width=10).grid(
            row=1, column=1, pady=2)
        
        ttk.Button(origin_frame, text="Update Origin",
                  command=self.update_origin).grid(
                      row=2, column=0, columnspan=2, pady=5)
        ttk.Button(origin_frame, text="Set to Center",
                  command=self.set_origin_center).grid(
                      row=3, column=0, columnspan=2, pady=2)
        
        # Preset Templates
        presets_frame = ttk.LabelFrame(left_panel, text="Test Case Presets", padding=10)
        presets_frame.pack(fill=tk.X, pady=5)

        ttk.Label(presets_frame, text="Load Template:").pack(anchor=tk.W, pady=2)

        # Scan for preset files
        self.load_preset_list()

        self.preset_combo = ttk.Combobox(presets_frame, values=self.preset_files, 
                                        state='readonly', width=20)
        if self.preset_files:
            self.preset_combo.current(0)
        self.preset_combo.pack(fill=tk.X, pady=2)

        ttk.Button(presets_frame, text="Load Preset",
                command=self.load_preset_template).pack(fill=tk.X, pady=2)
        ttk.Button(presets_frame, text="Refresh List",
                command=self.refresh_preset_list).pack(fill=tk.X, pady=2)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(left_panel, text="Placement Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.mode_var = tk.StringVar(value="single")
        modes = [
            ("Single Rack", "single"),
            ("Row Generator", "row"),
            ("Grid Generator", "grid"),
            ("Select/Move", "select"),
            ("Draw Path", "path")
        ]
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, value=mode,
                          variable=self.mode_var,
                          command=self.change_mode).pack(anchor=tk.W, pady=2)
        
        # Rack preset selection
        preset_frame = ttk.LabelFrame(left_panel, text="Rack Type", padding=10)
        preset_frame.pack(fill=tk.X, pady=5)
        
        self.preset_var = tk.StringVar(value="SmallRack")
        for preset in self.rack_presets.keys():
            ttk.Radiobutton(preset_frame, text=preset, value=preset,
                          variable=self.preset_var,
                          command=self.update_dimensions).pack(anchor=tk.W, pady=2)
        
        # Rack dimensions
        dim_frame = ttk.LabelFrame(left_panel, text="Rack Dimensions (m)", padding=10)
        dim_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dim_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value="2.0")
        ttk.Entry(dim_frame, textvariable=self.width_var, width=10).grid(
            row=0, column=1, pady=2)
        
        ttk.Label(dim_frame, text="Depth:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.depth_var = tk.StringVar(value="0.96")
        ttk.Entry(dim_frame, textvariable=self.depth_var, width=10).grid(
            row=1, column=1, pady=2)
        
        ttk.Label(dim_frame, text="Rotation:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.rotation_var = tk.StringVar(value="0")
        ttk.Entry(dim_frame, textvariable=self.rotation_var, width=10).grid(
            row=2, column=1, pady=2)
        
        # Row/Grid parameters
        gen_frame = ttk.LabelFrame(left_panel, text="Row/Grid Parameters", padding=10)
        gen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gen_frame, text="Count:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.count_var = tk.StringVar(value="5")
        ttk.Entry(gen_frame, textvariable=self.count_var, width=10).grid(
            row=0, column=1, pady=2)
        
        ttk.Label(gen_frame, text="Spacing (m):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.spacing_var = tk.StringVar(value="2.5")
        ttk.Entry(gen_frame, textvariable=self.spacing_var, width=10).grid(
            row=1, column=1, pady=2)
        
        ttk.Label(gen_frame, text="Rows:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.rows_var = tk.StringVar(value="3")
        ttk.Entry(gen_frame, textvariable=self.rows_var, width=10).grid(
            row=2, column=1, pady=2)
        
        ttk.Label(gen_frame, text="Row Spacing (m):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.row_spacing_var = tk.StringVar(value="4.0")
        ttk.Entry(gen_frame, textvariable=self.row_spacing_var, width=10).grid(
            row=3, column=1, pady=2)
        
        # Action buttons
        action_frame = ttk.LabelFrame(left_panel, text="Actions", padding=10)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Delete Selected",
                  command=self.delete_selected).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Duplicate Selected",
                  command=self.duplicate_selected).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Clear Path",
                  command=self.clear_path).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Load Path TXT",
                  command=self.load_path_txt).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Undo Last Waypoint",
                  command=self.undo_last_waypoint).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Apply Rotation",
                  command=self.apply_rotation_to_selected).pack(fill=tk.X, pady=2)
        
        # Statistics
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Total Racks: 0\nArea: 30m x 20m\nWaypoints: 0")
        self.stats_label.pack(anchor=tk.W)
        
        # Canvas frame with scrollbars
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL,
                                command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, 
                            xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.canvas.bind('<B1-Motion>', self.canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.canvas_release)
        self.canvas.bind('<Delete>', lambda e: self.delete_selected())
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_warehouse_preset(self):
        """Update warehouse dimensions based on preset"""
        preset = self.warehouse_var.get()
        width, height = self.warehouse_presets[preset]
        self.wh_width_var.set(str(width))
        self.wh_height_var.set(str(height))
        if preset != "Custom":
            self.apply_warehouse_size()
    
    def apply_warehouse_size(self):
        """Apply custom warehouse size"""
        try:
            width = float(self.wh_width_var.get())
            height = float(self.wh_height_var.get())
            
            if width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive")
            
            self.warehouse_width_m = width
            self.warehouse_height_m = height
            self.update_warehouse_size()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid warehouse dimensions: {e}")
            self.wh_width_var.set(str(self.warehouse_width_m))
            self.wh_height_var.set(str(self.warehouse_height_m))
    
    def update_warehouse_size(self):
        """Update canvas size and redraw"""
        canvas_width = int(self.warehouse_width_m * self.scale)
        canvas_height = int(self.warehouse_height_m * self.scale)
        
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self.draw_warehouse_boundary()
        self.draw_grid()
        self.draw_origin()
        self.redraw_all_racks()
        self.redraw_path()
        self.update_stats()
    
    def draw_warehouse_boundary(self):
        """Draw warehouse boundary rectangle"""
        self.canvas.delete('boundary')
        width_px = self.warehouse_width_m * self.scale
        height_px = self.warehouse_height_m * self.scale
        
        # Draw thick border
        self.canvas.create_rectangle(0, 0, width_px, height_px,
                                     outline='black', width=3, tags='boundary')
        self.canvas.tag_lower('boundary')
    
    def draw_grid(self):
        """Draw background grid"""
        self.canvas.delete('grid')
        
        # Draw meter grid lines
        for i in range(0, int(self.warehouse_width_m) + 1):
            x = i * self.scale
            self.canvas.create_line(x, 0, x, self.warehouse_height_m * self.scale,
                                  fill='lightgray', tags='grid')
            if i % 5 == 0:  # Label every 5 meters
                self.canvas.create_text(x, 10, text=f'{i}m', 
                                      fill='gray', tags='grid')
        
        for i in range(0, int(self.warehouse_height_m) + 1):
            y = i * self.scale
            self.canvas.create_line(0, y, self.warehouse_width_m * self.scale, y,
                                  fill='lightgray', tags='grid')
            if i % 5 == 0:
                self.canvas.create_text(10, y, text=f'{i}m',
                                      fill='gray', tags='grid')
        
        self.canvas.tag_lower('grid')
    
    def draw_origin(self):
        """Draw world origin marker"""
        self.canvas.delete('origin')
        
        ox = self.origin_x_m * self.scale
        oy = self.origin_y_m * self.scale
        
        size = 20
        # Draw crosshair
        self.canvas.create_line(ox - size, oy, ox + size, oy,
                               fill='blue', width=2, tags='origin')
        self.canvas.create_line(ox, oy - size, ox, oy + size,
                               fill='blue', width=2, tags='origin')
        self.canvas.create_oval(ox - 5, oy - 5, ox + 5, oy + 5,
                               fill='blue', outline='darkblue', tags='origin')
        self.canvas.create_text(ox + 25, oy - 15, text='Origin (0,0)',
                               fill='blue', font=('Arial', 10, 'bold'), tags='origin')
    
    def update_origin(self):
        """Update world origin from entry fields"""
        try:
            self.origin_x_m = float(self.origin_x_var.get())
            self.origin_y_m = float(self.origin_y_var.get())
            self.draw_origin()
            messagebox.showinfo("Success", "Origin updated")
        except ValueError:
            messagebox.showerror("Error", "Invalid origin coordinates")
            self.origin_x_var.set(str(self.origin_x_m))
            self.origin_y_var.set(str(self.origin_y_m))
    
    def set_origin_center(self):
        """Set origin to warehouse center"""
        self.origin_x_m = self.warehouse_width_m / 2
        self.origin_y_m = self.warehouse_height_m / 2
        self.origin_x_var.set(f"{self.origin_x_m:.1f}")
        self.origin_y_var.set(f"{self.origin_y_m:.1f}")
        self.draw_origin()
    
    def update_scale(self):
        """Update the scale and redraw everything"""
        try:
            new_scale = float(self.scale_var.get())
            if new_scale < 10 or new_scale > 200:
                raise ValueError()
            
            # Calculate scale factor
            scale_factor = new_scale / self.scale
            self.scale = new_scale
            
            # Scale all rack positions
            for rack in self.racks:
                rack.x *= scale_factor
                rack.y *= scale_factor
            
            # Scale waypoints
            for i in range(len(self.waypoints)):
                x, y = self.waypoints[i]
                self.waypoints[i] = (x * scale_factor, y * scale_factor)
            
            self.update_warehouse_size()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid scale value")
            self.scale_var.set(str(self.scale))
    
    def update_dimensions(self):
        """Update dimensions based on preset"""
        preset = self.preset_var.get()
        width, depth = self.rack_presets[preset]
        self.width_var.set(str(width))
        self.depth_var.set(str(depth))
    
    def change_mode(self):
        """Change placement mode"""
        self.mode = self.mode_var.get()
        self.selected_rack = None
        self.selected_rack_idx = None
        self.redraw_all_racks()
        
        if self.mode == "path":
            self.status_bar.config(text="Path Mode: Click to add waypoints")
        else:
            self.status_bar.config(text=f"Mode: {self.mode}")
    
    def canvas_click(self, event):
        """Handle canvas click"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Check if click is within warehouse bounds
        if x < 0 or x > self.warehouse_width_m * self.scale or \
           y < 0 or y > self.warehouse_height_m * self.scale:
            return
        
        if self.mode == "single":
            self.place_rack(x, y)
        elif self.mode == "row":
            self.drag_start = (x, y)
            self.temp_line = self.canvas.create_line(x, y, x, y, 
                                                     fill='blue', dash=(5, 5))
        elif self.mode == "grid":
            self.place_grid(x, y)
        elif self.mode == "select":
            self.select_rack(x, y)
            if self.selected_rack:
                self.drag_start = (x, y)
        elif self.mode == "path":
            self.add_waypoint(x, y)
    
    def canvas_drag(self, event):
        """Handle canvas drag"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.mode == "row" and self.drag_start and self.temp_line:
            x1, y1 = self.drag_start
            self.canvas.coords(self.temp_line, x1, y1, x, y)
        elif self.mode == "select" and self.selected_rack and self.drag_start:
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            
            # Keep within bounds
            new_x = self.selected_rack.x + dx
            new_y = self.selected_rack.y + dy
            
            if 0 <= new_x <= self.warehouse_width_m * self.scale and \
               0 <= new_y <= self.warehouse_height_m * self.scale:
                self.selected_rack.x = new_x
                self.selected_rack.y = new_y
                self.drag_start = (x, y)
                self.draw_rack(self.selected_rack, selected=True)
    
    def canvas_release(self, event):
        """Handle canvas release"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.mode == "row" and self.drag_start:
            x1, y1 = self.drag_start
            self.place_row(x1, y1, x, y)
            if self.temp_line:
                self.canvas.delete(self.temp_line)
                self.temp_line = None
            self.drag_start = None
        elif self.mode == "select":
            self.drag_start = None
    
    def add_waypoint(self, x, y):
        """Add a waypoint to the path"""
        self.waypoints.append((x, y))
        self.redraw_path()
        self.update_stats()
        self.status_bar.config(text=f"Path Mode: {len(self.waypoints)} waypoints")
    
    def clear_path(self):
        """Clear all waypoints"""
        if self.waypoints and messagebox.askyesno("Confirm", "Clear all waypoints?"):
            self.waypoints.clear()
            self.redraw_path()
            self.update_stats()
            self.status_bar.config(text="Path cleared")
    
    def undo_last_waypoint(self):
        """Remove the last waypoint from the path"""
        if self.waypoints:
            self.waypoints.pop()
            self.redraw_path()
            self.update_stats()
            remaining = len(self.waypoints)
            self.status_bar.config(text=f"Path Mode: {remaining} waypoint{'s' if remaining != 1 else ''}")
        else:
            messagebox.showinfo("Info", "No waypoints to undo")
    
    def apply_rotation_to_selected(self):
        """Apply custom rotation value from entry field to selected rack"""
        if self.selected_rack:
            try:
                new_rotation = float(self.rotation_var.get())
                self.selected_rack.rotation = new_rotation % 360
                self.draw_rack(self.selected_rack, selected=True)
                messagebox.showinfo("Success", f"Rotation set to {self.selected_rack.rotation}°")
            except ValueError:
                messagebox.showerror("Error", "Invalid rotation value")
        else:
            messagebox.showwarning("Warning", "No rack selected")
    
    def redraw_path(self):
        """Redraw the path with waypoints"""
        # Clear existing path elements
        for line_id in self.path_lines:
            self.canvas.delete(line_id)
        for marker_id in self.waypoint_markers:
            self.canvas.delete(marker_id)
        
        self.path_lines.clear()
        self.waypoint_markers.clear()
        
        if not self.waypoints:
            return
        
        # Draw lines between waypoints
        for i in range(len(self.waypoints) - 1):
            x1, y1 = self.waypoints[i]
            x2, y2 = self.waypoints[i + 1]
            line_id = self.canvas.create_line(x1, y1, x2, y2, 
                                             fill='green', width=3, 
                                             arrow=tk.LAST, arrowshape=(10, 12, 5))
            self.path_lines.append(line_id)
        
        # Draw waypoint markers
        for idx, (x, y) in enumerate(self.waypoints):
            # Circle marker
            r = 8
            circle_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                               fill='yellow', outline='green', width=2)
            # Number label
            text_id = self.canvas.create_text(x, y, text=str(idx+1), 
                                             fill='black', font=('Arial', 10, 'bold'))
            self.waypoint_markers.append(circle_id)
            self.waypoint_markers.append(text_id)
    
    def place_rack(self, x, y):
        """Place a single rack"""
        try:
            width = float(self.width_var.get())
            depth = float(self.depth_var.get())
            rotation = float(self.rotation_var.get())
            rack_type = self.preset_var.get()
            
            rack = Rack(x, y, width, depth, rotation, rack_type)
            self.racks.append(rack)
            self.draw_rack(rack)
            self.update_stats()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid dimensions")
    
    def place_row(self, x1, y1, x2, y2):
        """Place a row of racks"""
        try:
            width = float(self.width_var.get())
            depth = float(self.depth_var.get())
            count = int(self.count_var.get())
            spacing = float(self.spacing_var.get())
            rotation = float(self.rotation_var.get())
            rack_type = self.preset_var.get()
            
            # Calculate direction and spacing
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx**2 + dy**2)
            
            if length < 1:
                return
            
            # Unit vector
            ux = dx / length
            uy = dy / length
            
            # Place racks along the line
            spacing_px = spacing * self.scale
            for i in range(count):
                rx = x1 + ux * spacing_px * i
                ry = y1 + uy * spacing_px * i
                
                # Check bounds
                if 0 <= rx <= self.warehouse_width_m * self.scale and \
                   0 <= ry <= self.warehouse_height_m * self.scale:
                    rack = Rack(rx, ry, width, depth, rotation, rack_type)
                    self.racks.append(rack)
                    self.draw_rack(rack)
            
            self.update_stats()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid parameters")
    
    def place_grid(self, x, y):
        """Place a grid of racks"""
        try:
            width = float(self.width_var.get())
            depth = float(self.depth_var.get())
            count = int(self.count_var.get())
            rows = int(self.rows_var.get())
            spacing = float(self.spacing_var.get())
            row_spacing = float(self.row_spacing_var.get())
            rotation = float(self.rotation_var.get())
            rack_type = self.preset_var.get()
            
            spacing_px = spacing * self.scale
            row_spacing_px = row_spacing * self.scale
            
            for row in range(rows):
                for col in range(count):
                    rx = x + col * spacing_px
                    ry = y + row * row_spacing_px
                    
                    # Check bounds
                    if 0 <= rx <= self.warehouse_width_m * self.scale and \
                       0 <= ry <= self.warehouse_height_m * self.scale:
                        rack = Rack(rx, ry, width, depth, rotation, rack_type)
                        self.racks.append(rack)
                        self.draw_rack(rack)
            
            self.update_stats()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid parameters")
    
    def draw_rack(self, rack, selected=False):
        """Draw a rack on canvas"""
        if rack.canvas_id:
            self.canvas.delete(rack.canvas_id)
        
        # Calculate rack corners based on rotation
        w_px = rack.width_m * self.scale
        h_px = rack.depth_m * self.scale
        
        angle_rad = math.radians(rack.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Corner points (rotated)
        corners = [
            (-w_px/2, -h_px/2),
            (w_px/2, -h_px/2),
            (w_px/2, h_px/2),
            (-w_px/2, h_px/2)
        ]
        
        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + rack.x
            ry = cx * sin_a + cy * cos_a + rack.y
            rotated.extend([rx, ry])
        
        color = 'red' if selected else 'gray'
        rack.canvas_id = self.canvas.create_polygon(rotated, fill=color, 
                                                    outline='darkgray', width=2)
    
    def redraw_all_racks(self):
        """Redraw all racks"""
        for idx, rack in enumerate(self.racks):
            selected = (idx == self.selected_rack_idx)
            self.draw_rack(rack, selected)
    
    def select_rack(self, x, y):
        """Select a rack at position"""
        self.selected_rack = None
        self.selected_rack_idx = None
        
        for idx, rack in enumerate(self.racks):
            # Simple distance check
            dist = math.sqrt((rack.x - x)**2 + (rack.y - y)**2)
            if dist < self.scale:  # Within 1 meter
                self.selected_rack = rack
                self.selected_rack_idx = idx
                
                # Update dimension fields
                self.width_var.set(str(rack.width_m))
                self.depth_var.set(str(rack.depth_m))
                self.rotation_var.set(str(rack.rotation))
                break
        
        self.redraw_all_racks()
    
    def delete_selected(self):
        """Delete selected rack"""
        if self.selected_rack and self.selected_rack_idx is not None:
            self.canvas.delete(self.selected_rack.canvas_id)
            self.racks.pop(self.selected_rack_idx)
            self.selected_rack = None
            self.selected_rack_idx = None
            self.update_stats()
    
    def duplicate_selected(self):
        """Duplicate selected rack"""
        if self.selected_rack:
            new_rack = Rack(self.selected_rack.x + 20, 
                          self.selected_rack.y + 20,
                          self.selected_rack.width_m,
                          self.selected_rack.depth_m,
                          self.selected_rack.rotation,
                          self.selected_rack.rack_type)
            self.racks.append(new_rack)
            self.draw_rack(new_rack)
            self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        stats_text = f"Total Racks: {len(self.racks)}\n"
        stats_text += f"Area: {self.warehouse_width_m}m x {self.warehouse_height_m}m\n"
        stats_text += f"Waypoints: {len(self.waypoints)}"
        self.stats_label.config(text=stats_text)
    
    def clear_all(self):
        """Clear all racks and path"""
        if messagebox.askyesno("Confirm", "Delete all racks and path?"):
            self.canvas.delete('all')
            self.racks.clear()
            self.waypoints.clear()
            self.path_lines.clear()
            self.waypoint_markers.clear()
            self.selected_rack = None
            self.selected_rack_idx = None
            self.update_warehouse_size()
            self.update_stats()
    
    def waypoints_to_dict(self):
        """Convert waypoints to world coordinates"""
        waypoints_world = []
        for x_px, y_px in self.waypoints:
            # Convert to meters
            x_m = x_px / self.scale
            y_m = y_px / self.scale
            
            # Relative to origin
            world_x = x_m - self.origin_x_m
            world_y = y_m - self.origin_y_m
            
            # Swap x and y
            waypoints_world.append({
                'x': round(world_y, 3),
                'y': round(world_x, 3)
            })
        
        return waypoints_world
    
    def waypoints_from_dict(self, waypoints_data):
        """Load waypoints from world coordinates"""
        self.waypoints.clear()
        
        for wp in waypoints_data:
            # Swap back
            world_x = wp['y']
            world_y = wp['x']
            
            # Convert to canvas
            x_m = world_x + self.origin_x_m
            y_m = world_y + self.origin_y_m
            
            x_px = x_m * self.scale
            y_px = y_m * self.scale
            
            self.waypoints.append((x_px, y_px))
    
    def export_path_txt(self):
        """Export path waypoints to a TXT file"""
        if not self.waypoints:
            messagebox.showwarning("Warning", "No waypoints to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                waypoints_world = self.waypoints_to_dict()
                
                with open(filename, 'w') as f:
                    f.write("Character Idle 10\n")

                    for idx, wp in enumerate(waypoints_world):
                        f.write(f"Character GoTo {wp['x']} {wp['y']} 0.0 _\n")
                
                messagebox.showinfo("Success", 
                                  f"Path exported to {filename}\n"
                                  f"Total waypoints: {len(waypoints_world)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export path: {e}")
    
    def load_path_txt(self):
        """Load path waypoints from a TXT file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                waypoints_data = []
                
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse: waypoint_number, x, y
                        parts = line.split(',')
                        if len(parts) >= 3:
                            try:
                                x = float(parts[1].strip())
                                y = float(parts[2].strip())
                                waypoints_data.append({'x': x, 'y': y})
                            except ValueError:
                                continue
                
                if not waypoints_data:
                    messagebox.showwarning("Warning", "No valid waypoints found in file!")
                    return
                
                # Clear existing waypoints
                self.waypoints.clear()
                self.path_lines.clear()
                self.waypoint_markers.clear()
                
                # Load new waypoints
                self.waypoints_from_dict(waypoints_data)
                self.redraw_path()
                self.update_stats()
                
                messagebox.showinfo("Success", 
                                  f"Path loaded from {filename}\n"
                                  f"Total waypoints: {len(waypoints_data)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load path: {e}")
    
    def save_layout(self):
        """Save layout to JSON file with world coordinates"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # Save JSON data
            data = {
                'warehouse_type': self.warehouse_var.get(),
                'scale': self.scale,
                'warehouse_width_m': self.warehouse_width_m,
                'warehouse_height_m': self.warehouse_height_m,
                'world_origin': {
                    'x': self.origin_x_m,
                    'y': self.origin_y_m
                },
                'racks': [rack.to_dict(self.origin_x_m, self.origin_y_m, self.scale) 
                         for rack in self.racks],
                'path': {
                    'waypoints': self.waypoints_to_dict()
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Automatically save PNG and TXT with same name
            png_filename = filename.rsplit('.', 1)[0] + '.png'
            txt_filename = filename.rsplit('.', 1)[0] + '.txt'

            saved_files = [filename]
            errors = []

            try:
                self.export_png_to_file(png_filename)
                saved_files.append(png_filename)
            except Exception as e:
                errors.append(f"PNG: {e}")

            # Save TXT file if waypoints exist
            if self.waypoints:
                try:
                    waypoints_world = self.waypoints_to_dict()
                    with open(txt_filename, 'w') as f:
                        f.write("Character Idle 10\n")
                        for idx, wp in enumerate(waypoints_world):
                            f.write(f"Character GoTo {wp['x']} {wp['y']} 0.0 _\n")
                    saved_files.append(txt_filename)
                except Exception as e:
                    errors.append(f"TXT: {e}")

            # Show result message
            if not errors:
                files_list = "\n".join(saved_files)
                messagebox.showinfo("Success", 
                                f"Files saved:\n{files_list}\n\n"
                                f"Warehouse Type: {self.warehouse_var.get()}\n"
                                f"Racks: {len(self.racks)}\n"
                                f"Waypoints: {len(self.waypoints)}\n"
                                f"Positions are relative to origin at ({self.origin_x_m}, {self.origin_y_m})")
            else:
                error_msg = "\n".join(errors)
                messagebox.showwarning("Partial Success", 
                                    f"JSON saved successfully to {filename}\n"
                                    f"But encountered errors:\n{error_msg}")
    
    def load_layout(self):
        """Load layout from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Clear existing
                self.canvas.delete('all')
                self.racks.clear()
                self.waypoints.clear()
                self.path_lines.clear()
                self.waypoint_markers.clear()
                
                # Load settings
                self.scale = data.get('scale', 50)
                self.scale_var.set(str(self.scale))
                
                self.warehouse_width_m = data.get('warehouse_width_m', 40)
                self.warehouse_height_m = data.get('warehouse_height_m', 30)
                self.wh_width_var.set(str(self.warehouse_width_m))
                self.wh_height_var.set(str(self.warehouse_height_m))
                
                # Load warehouse type
                warehouse_type = data.get('warehouse_type', 'Custom')
                self.warehouse_var.set(warehouse_type)
                
                # Load origin
                origin = data.get('world_origin', {'x': self.warehouse_width_m/2, 
                                                   'y': self.warehouse_height_m/2})
                self.origin_x_m = origin['x']
                self.origin_y_m = origin['y']
                self.origin_x_var.set(str(self.origin_x_m))
                self.origin_y_var.set(str(self.origin_y_m))
                
                # Load racks
                for rack_data in data['racks']:
                    rack = Rack.from_dict(rack_data, self.origin_x_m, 
                                         self.origin_y_m, self.scale)
                    self.racks.append(rack)
                
                # Load path
                if 'path' in data and 'waypoints' in data['path']:
                    self.waypoints_from_dict(data['path']['waypoints'])
                
                self.update_warehouse_size()
                messagebox.showinfo("Success", f"Layout loaded\n"
                                  f"Racks: {len(self.racks)}\n"
                                  f"Waypoints: {len(self.waypoints)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout: {e}")
    
    def export_png(self):
        """Export canvas as PNG image"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.export_png_to_file(filename)
                messagebox.showinfo("Success", f"Image exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export image: {e}")
    
    def export_png_to_file(self, filename):
        """Export canvas as PNG image to specified filename"""
        # Get canvas dimensions
        width = int(self.warehouse_width_m * self.scale)
        height = int(self.warehouse_height_m * self.scale)
        
        # Create image
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Draw grid
        for i in range(0, int(self.warehouse_width_m) + 1):
            x = i * self.scale
            draw.line([(x, 0), (x, height)], fill='lightgray', width=1)
        
        for i in range(0, int(self.warehouse_height_m) + 1):
            y = i * self.scale
            draw.line([(0, y), (width, y)], fill='lightgray', width=1)
        
        # Draw boundary
        draw.rectangle([0, 0, width-1, height-1], outline='black', width=3)
        
        # Draw origin
        ox = int(self.origin_x_m * self.scale)
        oy = int(self.origin_y_m * self.scale)
        size = 20
        draw.line([(ox - size, oy), (ox + size, oy)], fill='blue', width=2)
        draw.line([(ox, oy - size), (ox, oy + size)], fill='blue', width=2)
        draw.ellipse([ox-5, oy-5, ox+5, oy+5], fill='blue', outline='darkblue')
        
        # Draw racks
        for rack in self.racks:
            w_px = rack.width_m * self.scale
            h_px = rack.depth_m * self.scale
            
            angle_rad = math.radians(rack.rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            corners = [
                (-w_px/2, -h_px/2),
                (w_px/2, -h_px/2),
                (w_px/2, h_px/2),
                (-w_px/2, h_px/2)
            ]
            
            rotated = []
            for cx, cy in corners:
                rx = cx * cos_a - cy * sin_a + rack.x
                ry = cx * sin_a + cy * cos_a + rack.y
                rotated.append((rx, ry))
            
            draw.polygon(rotated, fill='gray', outline='darkgray')
        
        # Draw path
        if len(self.waypoints) > 1:
            # Draw lines between waypoints
            for i in range(len(self.waypoints) - 1):
                x1, y1 = self.waypoints[i]
                x2, y2 = self.waypoints[i + 1]
                draw.line([(x1, y1), (x2, y2)], fill='green', width=3)
        
        # Draw waypoint markers
        for idx, (x, y) in enumerate(self.waypoints):
            r = 8
            draw.ellipse([x-r, y-r, x+r, y+r], fill='yellow', outline='green', width=2)
            # Draw number (simplified, as PIL text requires font setup)
            draw.text((x-3, y-6), str(idx+1), fill='black')
        
        image.save(filename)


def main():
    root = tk.Tk()
    app = WarehouseDesigner(root)
    root.mainloop()


if __name__ == "__main__":
    main()