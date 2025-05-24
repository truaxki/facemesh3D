#!/usr/bin/env python3
"""open3d_desktop_viewer.py

Full-featured Open3D desktop viewer showing REAL interactivity.
This demonstrates what Streamlit CANNOT provide.

Mouse Controls:
- Left drag: Rotate
- Right drag: Pan  
- Scroll: Zoom
- Middle click: Reset view

Keyboard (in terminal):
- Press ENTER to cycle through backgrounds
- Press 's' + ENTER to save screenshot
- Press 'q' + ENTER to quit

Run: python source/open3d_desktop_viewer.py
"""

import numpy as np
import open3d as o3d
import argparse
import threading
import time


def create_sample_data(data_type="sphere", num_points=2000):
    """Generate sample point clouds."""
    
    if data_type == "sphere":
        # Colorful sphere
        phi = np.random.uniform(0, 2*np.pi, num_points)
        costheta = np.random.uniform(-1, 1, num_points)
        u = np.random.uniform(0, 1, num_points)
        
        theta = np.arccos(costheta)
        r = u ** (1/3)
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        points = np.column_stack([x, y, z])
        
        # Rainbow colors by angle
        colors = np.column_stack([
            (phi / (2*np.pi)),
            (theta / np.pi), 
            np.ones_like(phi) * 0.8
        ])
        
    elif data_type == "torus":
        # Donut shape
        R, r = 1.0, 0.3
        u = np.random.uniform(0, 2*np.pi, num_points)
        v = np.random.uniform(0, 2*np.pi, num_points)
        
        x = (R + r * np.cos(v)) * np.cos(u)
        y = (R + r * np.cos(v)) * np.sin(u)
        z = r * np.sin(v)
        points = np.column_stack([x, y, z])
        
        colors = np.column_stack([
            (np.sin(u) + 1) / 2,
            (np.cos(u) + 1) / 2,
            (np.sin(v) + 1) / 2
        ])
        
    elif data_type == "bunny":
        # Generate bunny-like shape
        u = np.random.uniform(-np.pi, np.pi, num_points)
        v = np.random.uniform(-np.pi/2, np.pi/2, num_points)
        
        x = np.cos(v) * np.cos(u)
        y = np.cos(v) * np.sin(u) 
        z = np.sin(v) + 0.3 * np.sin(3*u) * np.cos(v)
        points = np.column_stack([x, y, z])
        
        # Pastel colors
        colors = np.column_stack([
            0.8 + 0.2 * np.random.random(num_points),
            0.6 + 0.2 * np.random.random(num_points), 
            0.9 + 0.1 * np.random.random(num_points)
        ])
    
    else:  # "dragon" or complex shape
        # Multiple intertwined spirals
        t = np.linspace(0, 8*np.pi, num_points)
        noise = np.random.normal(0, 0.02, (num_points, 3))
        
        # Triple helix
        x1 = np.cos(t) + 0.3*np.cos(3*t)
        y1 = np.sin(t) + 0.3*np.sin(3*t)
        z1 = t / (4*np.pi)
        
        points = np.column_stack([x1, y1, z1]) + noise
        
        # Color by height and twist
        colors = np.column_stack([
            (z1 - z1.min()) / (z1.max() - z1.min()),
            np.abs(np.sin(3*t)),
            np.abs(np.cos(5*t))
        ])
    
    return points, colors


def create_point_cloud(points, colors=None):
    """Convert to Open3D point cloud."""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
    
    if colors is not None:
        colors = np.clip(colors, 0, 1)
        pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
    
    pcd.estimate_normals()
    return pcd


def interactive_controls(vis):
    """Handle interactive controls via terminal input."""
    bg_colors = [
        [0.1, 0.1, 0.4],  # Dark blue
        [0, 0, 0],         # Black
        [1, 1, 1],         # White
        [0.2, 0.2, 0.2],   # Dark gray
    ]
    bg_index = 0
    
    print("\n" + "="*60)
    print("🎮 INTERACTIVE CONTROLS")
    print("="*60)
    print("Mouse Controls (in Open3D window):")
    print("  Left click + drag    : Rotate view")
    print("  Right click + drag   : Pan view")  
    print("  Scroll wheel         : Zoom in/out")
    print("  Middle click         : Reset view")
    print("\nTerminal Controls:")
    print("  ENTER               : Change background color")
    print("  's' + ENTER         : Save screenshot")
    print("  'q' + ENTER         : Quit")
    print("="*60)
    print("💡 Try moving the mouse in the 3D window - MUCH smoother than Streamlit!")
    print("   Notice the real-time lighting, shadows, and depth!")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q' or cmd == 'quit':
                print("👋 Closing viewer...")
                vis.close()
                break
                
            elif cmd == 's' or cmd == 'screenshot':
                print("📸 Saving screenshot...")
                vis.capture_screen_image("open3d_screenshot.png", do_render=True)
                print("   ✅ Saved: open3d_screenshot.png")
                
            elif cmd == '' or cmd == 'bg':  # ENTER key
                bg_index = (bg_index + 1) % len(bg_colors)
                render_opt = vis.get_render_option()
                render_opt.background_color = np.array(bg_colors[bg_index])
                color_names = ["Dark Blue", "Black", "White", "Dark Gray"]
                print(f"🎨 Background: {color_names[bg_index]}")
                
            else:
                print("❓ Unknown command. Use ENTER, 's', or 'q'")
                
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Closing viewer...")
            vis.close()
            break


def main():
    """Main interactive viewer."""
    parser = argparse.ArgumentParser(description="Interactive Open3D Point Cloud Viewer")
    parser.add_argument("--type", choices=["sphere", "torus", "bunny", "dragon"], 
                       default="torus", help="Type of point cloud to generate")
    parser.add_argument("--points", type=int, default=3000, 
                       help="Number of points to generate")
    parser.add_argument("--file", type=str, help="Load point cloud from file (PLY/PCD/XYZ)")
    
    args = parser.parse_args()
    
    print("🔺 Open3D Interactive Desktop Viewer")
    print("=" * 50)
    print("This shows REAL interactivity vs. Streamlit's limited matplotlib!")
    
    if args.file:
        print(f"Loading point cloud from: {args.file}")
        pcd = o3d.io.read_point_cloud(args.file)
        if len(pcd.points) == 0:
            print("❌ Failed to load point cloud or file is empty")
            return
        print(f"✅ Loaded {len(pcd.points)} points")
    else:
        print(f"Generating {args.type} with {args.points} points...")
        points, colors = create_sample_data(args.type, args.points)
        pcd = create_point_cloud(points, colors)
        print(f"✅ Generated {len(pcd.points)} points")
    
    # Create visualizer with enhanced settings
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=f"🔺 Open3D Interactive Viewer - {args.type.title()}", 
                     width=1200, height=800)
    
    # Add geometry
    vis.add_geometry(pcd)
    
    # Configure rendering for maximum quality
    render_opt = vis.get_render_option()
    render_opt.background_color = np.array([0.1, 0.1, 0.4])  # Dark blue
    render_opt.point_size = 3.0
    render_opt.show_coordinate_frame = True
    render_opt.light_on = True
    
    # Start control thread
    control_thread = threading.Thread(target=interactive_controls, args=(vis,), daemon=True)
    control_thread.start()
    
    print(f"\n🎮 3D Window opened! Try these NOW:")
    print("   🖱️  Mouse: Drag to rotate (notice the smoothness!)")
    print("   🖱️  Right-drag: Pan around")
    print("   🖱️  Scroll: Zoom in/out") 
    print("   ⌨️  Terminal: Press ENTER to change background")
    
    # Run the main visualization loop
    vis.run()
    vis.destroy_window()
    
    print("✅ Viewer closed.")


if __name__ == "__main__":
    main() 