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

Animation Support:
- Press SPACEBAR to play/pause animation
- Press Arrow keys for manual frame control
- Press 'r' + ENTER to reset to first frame

Run: python source/open3d_desktop_viewer.py
"""

import numpy as np
import open3d as o3d
import argparse
import threading
import time
import json
import os
import glob


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
    print("INTERACTIVE CONTROLS")
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
    print("TIP: Try moving the mouse in the 3D window - MUCH smoother than Streamlit!")
    print("   Notice the real-time lighting, shadows, and depth!")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q' or cmd == 'quit':
                print("Closing viewer...")
                vis.close()
                break
                
            elif cmd == 's' or cmd == 'screenshot':
                print("Saving screenshot...")
                vis.capture_screen_image("open3d_screenshot.png", do_render=True)
                print("   SUCCESS: Saved open3d_screenshot.png")
                
            elif cmd == '' or cmd == 'bg':  # ENTER key
                bg_index = (bg_index + 1) % len(bg_colors)
                render_opt = vis.get_render_option()
                render_opt.background_color = np.array(bg_colors[bg_index])
                color_names = ["Dark Blue", "Black", "White", "Dark Gray"]
                print(f"Background: {color_names[bg_index]}")
                
            else:
                print("Unknown command. Use ENTER, 's', or 'q'")
                
        except (EOFError, KeyboardInterrupt):
            print("\nClosing viewer...")
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
    parser.add_argument("--animation", type=str, help="Load animation config JSON file")
    parser.add_argument("--fps", type=int, default=10, help="Animation FPS")
    
    args = parser.parse_args()
    
    print("Open3D Interactive Desktop Viewer")
    print("=" * 50)
    print("This shows REAL interactivity vs. Streamlit's limited matplotlib!")
    
    # Animation mode
    if args.animation:
        print(f"Loading animation: {args.animation}")
        try:
            with open(args.animation, 'r') as f:
                config = json.load(f)
            
            frame_paths = config.get('frame_paths', [])
            if not frame_paths:
                print("ERROR: No frame paths found in animation config")
                return
            
            print(f"SUCCESS: Found {len(frame_paths)} animation frames")
            run_animation_viewer(frame_paths, args.fps)
            return
            
        except Exception as e:
            print(f"ERROR: Failed to load animation: {e}")
            return
    
    # Single point cloud mode
    if args.file:
        print(f"Loading point cloud from: {args.file}")
        pcd = o3d.io.read_point_cloud(args.file)
        if len(pcd.points) == 0:
            print("ERROR: Failed to load point cloud or file is empty")
            return
        print(f"SUCCESS: Loaded {len(pcd.points)} points")
    else:
        print(f"Generating {args.type} with {args.points} points...")
        points, colors = create_sample_data(args.type, args.points)
        pcd = create_point_cloud(points, colors)
        print(f"SUCCESS: Generated {len(pcd.points)} points")
    
    # Create visualizer with enhanced settings
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=f"Open3D Interactive Viewer - {args.type.title()}", 
                     width=1200, height=800)
    
    # Add geometry
    vis.add_geometry(pcd)
    
    # Configure rendering for maximum quality
    render_opt = vis.get_render_option()
    render_opt.background_color = np.array([0.1, 0.1, 0.4])  # Dark blue
    render_opt.point_size = 3.0
    render_opt.show_coordinate_frame = True
    render_opt.light_on = True
    
    # Windows focus fix - bring window to front
    import sys
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            import time
            
            # Give window time to create
            time.sleep(0.5)
            
            # Find and focus the Open3D window
            def bring_to_front():
                user32 = ctypes.windll.user32
                # Get current foreground window - try multiple window title variations
                window_titles = [
                    f"Open3D Interactive Viewer - {args.type.title()}",
                    "Open3D",
                    "Open3D Interactive Viewer"
                ]
                
                hwnd = None
                for title in window_titles:
                    hwnd = user32.FindWindowW(None, title)
                    if hwnd:
                        break
                
                if hwnd:
                    # Force window to front
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    user32.SetActiveWindow(hwnd)
                    print("SUCCESS: Brought Open3D window to front!")
                else:
                    print("WARNING: Could not find Open3D window to bring to front")
            
            # Try to bring window to front after a short delay
            threading.Timer(1.0, bring_to_front).start()
            
        except ImportError:
            print("WARNING: Could not import Windows focus utilities")
    
    # Start control thread
    control_thread = threading.Thread(target=interactive_controls, args=(vis,), daemon=True)
    control_thread.start()
    
    print(f"\n3D Window opened! Try these NOW:")
    print("   Mouse: Drag to rotate (notice the smoothness!)")
    print("   Right-drag: Pan around")
    print("   Scroll: Zoom in/out") 
    print("   Terminal: Press ENTER to change background")
    print("\nIf you don't see the 3D window, check your taskbar!")
    print("   Windows sometimes opens it in the background.")
    
    # Run the main visualization loop
    vis.run()
    vis.destroy_window()
    
    print("Viewer closed.")


def run_animation_viewer(frame_paths, fps=10):
    """Run animation viewer with playback controls."""
    if not frame_paths:
        print("ERROR: No animation frames provided")
        return
    
    print(f"Starting animation viewer ({len(frame_paths)} frames at {fps} FPS)")
    
    # Load all frames
    frames = []
    print("Loading animation frames...")
    for i, path in enumerate(frame_paths):
        if i % 5 == 0:  # Progress update every 5 frames
            print(f"   Loading frame {i+1}/{len(frame_paths)}")
        
        try:
            pcd = o3d.io.read_point_cloud(path)
            if len(pcd.points) > 0:
                frames.append(pcd)
            else:
                print(f"WARNING: Empty frame: {path}")
        except Exception as e:
            print(f"WARNING: Could not load frame {path}: {e}")
    
    if not frames:
        print("ERROR: No valid frames loaded")
        return
    
    print(f"SUCCESS: Loaded {len(frames)} frames successfully")
    
    # Create visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Open3D Animation Viewer", width=1200, height=800)
    
    # Add first frame
    current_frame = 0
    vis.add_geometry(frames[current_frame])
    
    # Configure rendering
    render_opt = vis.get_render_option()
    render_opt.background_color = np.array([0.05, 0.05, 0.2])  # Dark blue
    render_opt.point_size = 2.5
    render_opt.show_coordinate_frame = True
    render_opt.light_on = True
    
    # Animation state
    is_playing = False
    frame_delay = 1.0 / fps
    
    def animation_controls():
        """Handle animation-specific controls."""
        nonlocal current_frame, is_playing
        
        print("\n" + "="*60)
        print("🎬 ANIMATION CONTROLS")
        print("="*60)
        print("Animation Controls:")
        print("  SPACEBAR           : Play/Pause animation")
        print("  'n' + ENTER        : Next frame")
        print("  'p' + ENTER        : Previous frame") 
        print("  'r' + ENTER        : Reset to first frame")
        print("  '0-9' + ENTER      : Jump to frame percentage")
        print("\nGeneral Controls:")
        print("  ENTER              : Change background")
        print("  's' + ENTER        : Save screenshot")
        print("  'q' + ENTER        : Quit")
        print("="*60)
        print(f"📽️ Loaded: {len(frames)} frames at {fps} FPS")
        print(f"⏱️ Duration: {len(frames)/fps:.1f} seconds")
        
        while True:
            try:
                cmd = input(f"\n[Frame {current_frame+1}/{len(frames)}] > ").strip().lower()
                
                if cmd == 'q' or cmd == 'quit':
                    print("👋 Closing animation viewer...")
                    vis.close()
                    break
                
                elif cmd == ' ' or cmd == 'space':
                    is_playing = not is_playing
                    status = "▶️ PLAYING" if is_playing else "⏸️ PAUSED"
                    print(f"{status}")
                
                elif cmd == 'n' or cmd == 'next':
                    current_frame = (current_frame + 1) % len(frames)
                    update_frame()
                
                elif cmd == 'p' or cmd == 'prev':
                    current_frame = (current_frame - 1) % len(frames)
                    update_frame()
                
                elif cmd == 'r' or cmd == 'reset':
                    current_frame = 0
                    update_frame()
                    print("⏮️ Reset to first frame")
                
                elif cmd.isdigit():
                    percent = int(cmd) * 10  # 0-9 -> 0%-90%
                    target_frame = int((percent / 100.0) * len(frames))
                    current_frame = min(target_frame, len(frames) - 1)
                    update_frame()
                    print(f"⏭️ Jumped to {percent}% (frame {current_frame+1})")
                
                elif cmd == 's' or cmd == 'screenshot':
                    filename = f"animation_frame_{current_frame:04d}.png"
                    vis.capture_screen_image(filename, do_render=True)
                    print(f"📸 Saved: {filename}")
                
                elif cmd == '':  # ENTER - background change
                    bg_colors = [[0.05, 0.05, 0.2], [0, 0, 0], [1, 1, 1], [0.2, 0.2, 0.2]]
                    bg_index = (current_frame // 10) % len(bg_colors)
                    render_opt.background_color = np.array(bg_colors[bg_index])
                    print("🎨 Background changed")
                
                else:
                    print("❓ Unknown command. Available: SPACE, n, p, r, 0-9, s, q")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Closing animation viewer...")
                vis.close()
                break
    
    def update_frame():
        """Update the displayed frame."""
        vis.clear_geometries()
        vis.add_geometry(frames[current_frame])
        vis.update_renderer()
    
    def animation_loop():
        """Main animation playback loop."""
        nonlocal current_frame
        last_time = time.time()
        
        while True:
            if is_playing:
                current_time = time.time()
                if current_time - last_time >= frame_delay:
                    current_frame = (current_frame + 1) % len(frames)
                    update_frame()
                    last_time = current_time
            
            time.sleep(0.01)  # Small delay to prevent CPU spinning
    
    # Windows focus fix
    import sys
    if sys.platform == "win32":
        try:
            import ctypes
            time.sleep(0.5)
            
            def bring_to_front():
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, "🎬 Open3D Animation Viewer")
                if hwnd:
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    user32.SetActiveWindow(hwnd)
                    print("🪟 Animation window brought to front!")
            
            threading.Timer(1.0, bring_to_front).start()
        except ImportError:
            pass
    
    # Start control threads
    control_thread = threading.Thread(target=animation_controls, daemon=True)
    control_thread.start()
    
    animation_thread = threading.Thread(target=animation_loop, daemon=True)
    animation_thread.start()
    
    print(f"\n🎬 Animation window opened!")
    print("   🖱️  Mouse: Rotate view while animation plays")
    print("   ⌨️  Terminal: Press SPACEBAR to start animation")
    print("\n🪟 If you don't see the window, check your taskbar!")
    
    # Run the main visualization loop
    vis.run()
    vis.destroy_window()
    
    print("✅ Animation viewer closed.")


if __name__ == "__main__":
    main() 