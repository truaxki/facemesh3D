"""Viewer Core Module

Core functionality for the Open3D desktop viewer.
Extracted from the main viewer to keep it under 200 lines.
"""

import numpy as np
import open3d as o3d
import threading
import time
import sys
import ctypes


class ViewerCore:
    """Core viewer functionality."""
    
    @staticmethod
    def create_point_cloud(points, colors=None):
        """Convert numpy arrays to Open3D point cloud."""
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
        
        if colors is not None:
            colors = np.clip(colors, 0, 1)
            pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
        
        pcd.estimate_normals()
        return pcd
    
    @staticmethod
    def setup_visualizer(window_name="Open3D Viewer", width=1200, height=800):
        """Create and configure visualizer."""
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=window_name, width=width, height=height)
        
        # Configure rendering
        render_opt = vis.get_render_option()
        render_opt.background_color = np.array([0.1, 0.1, 0.4])
        render_opt.point_size = 3.0
        render_opt.show_coordinate_frame = True
        render_opt.light_on = True
        
        return vis
    
    @staticmethod
    def bring_window_to_front(window_title, delay=1.0):
        """Bring Open3D window to front on Windows."""
        if sys.platform != "win32":
            return
        
        def focus_window():
            try:
                time.sleep(delay)
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, window_title)
                if hwnd:
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    user32.SetActiveWindow(hwnd)
                    print(f"✅ Window brought to front: {window_title}")
                else:
                    print(f"⚠️ Could not find window: {window_title}")
            except Exception as e:
                print(f"⚠️ Focus error: {e}")
        
        threading.Timer(delay, focus_window).start()


class InteractiveControls:
    """Handle interactive terminal controls."""
    
    BG_COLORS = [
        ([0.1, 0.1, 0.4], "Dark Blue"),
        ([0, 0, 0], "Black"),
        ([1, 1, 1], "White"),
        ([0.2, 0.2, 0.2], "Dark Gray")
    ]
    
    def __init__(self, vis):
        self.vis = vis
        self.bg_index = 0
        self.running = True
    
    def start_control_thread(self):
        """Start control thread."""
        control_thread = threading.Thread(target=self.control_loop, daemon=True)
        control_thread.start()
        return control_thread
    
    def control_loop(self):
        """Main control loop."""
        self.print_help()
        
        while self.running:
            try:
                cmd = input("\n> ").strip().lower()
                self.handle_command(cmd)
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Closing viewer...")
                self.vis.close()
                break
    
    def handle_command(self, cmd):
        """Handle individual commands."""
        if cmd in ['q', 'quit']:
            print("Closing viewer...")
            self.vis.close()
            self.running = False
        
        elif cmd in ['s', 'screenshot']:
            print("Saving screenshot...")
            self.vis.capture_screen_image("open3d_screenshot.png", do_render=True)
            print("   ✅ Saved: open3d_screenshot.png")
        
        elif cmd in ['', 'bg']:  # ENTER key
            self.cycle_background()
        
        else:
            print("❓ Unknown command. Use ENTER, 's', or 'q'")
    
    def cycle_background(self):
        """Cycle through background colors."""
        self.bg_index = (self.bg_index + 1) % len(self.BG_COLORS)
        color, name = self.BG_COLORS[self.bg_index]
        render_opt = self.vis.get_render_option()
        render_opt.background_color = np.array(color)
        print(f"🎨 Background: {name}")
    
    def print_help(self):
        """Print help message."""
        print("\n" + "="*50)
        print("🎮 INTERACTIVE CONTROLS")
        print("="*50)
        print("Mouse (in 3D window):")
        print("  Left drag    : Rotate view")
        print("  Right drag   : Pan view")
        print("  Scroll       : Zoom in/out")
        print("  Middle click : Reset view")
        print("\nTerminal Commands:")
        print("  ENTER        : Change background")
        print("  's'          : Save screenshot")
        print("  'q'          : Quit")
        print("="*50)
        print("💡 Try dragging in the 3D window - much smoother than web!")


class AnimationViewer:
    """Animation-specific viewer functionality."""
    
    def __init__(self, frame_paths, fps=10):
        self.frame_paths = frame_paths
        self.fps = fps
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 1.0 / fps
        self.vis = None
    
    def load_frames(self):
        """Load all animation frames."""
        print("📂 Loading animation frames...")
        
        for i, path in enumerate(self.frame_paths):
            if i % 5 == 0:
                print(f"   Frame {i+1}/{len(self.frame_paths)}")
            
            try:
                pcd = o3d.io.read_point_cloud(path)
                if len(pcd.points) > 0:
                    self.frames.append(pcd)
                else:
                    print(f"⚠️ Empty frame: {path}")
            except Exception as e:
                print(f"⚠️ Could not load {path}: {e}")
        
        if not self.frames:
            raise ValueError("No valid frames loaded")
        
        print(f"✅ Loaded {len(self.frames)} frames")
    
    def start_viewer(self):
        """Start the animation viewer."""
        self.vis = ViewerCore.setup_visualizer("Open3D Animation Viewer")
        
        # Add first frame
        self.vis.add_geometry(self.frames[self.current_frame])
        
        # Configure for animation
        render_opt = self.vis.get_render_option()
        render_opt.background_color = np.array([0.05, 0.05, 0.2])
        render_opt.point_size = 2.5
        
        # Start control and animation threads
        self.start_control_thread()
        self.start_animation_thread()
        
        # Focus window
        ViewerCore.bring_window_to_front("Open3D Animation Viewer")
        
        # Print instructions
        print(f"\n🎬 Animation Viewer Started!")
        print(f"   📊 {len(self.frames)} frames at {self.fps} FPS")
        print(f"   ⏱️ Duration: {len(self.frames)/self.fps:.1f} seconds")
        print("   ⌨️ Press SPACEBAR to play/pause")
        
        # Run viewer
        self.vis.run()
        self.vis.destroy_window()
        print("✅ Animation viewer closed")
    
    def start_control_thread(self):
        """Start animation control thread."""
        def control_loop():
            print("\n🎮 Animation Controls: SPACE (play/pause), n/p (next/prev), q (quit)")
            
            while True:
                try:
                    cmd = input(f"\n[{self.current_frame+1}/{len(self.frames)}] > ").strip().lower()
                    
                    if cmd in ['q', 'quit']:
                        self.vis.close()
                        break
                    elif cmd in [' ', 'space']:
                        self.is_playing = not self.is_playing
                        status = "▶️ Playing" if self.is_playing else "⏸️ Paused"
                        print(status)
                    elif cmd in ['n', 'next']:
                        self.next_frame()
                    elif cmd in ['p', 'prev']:
                        self.prev_frame()
                    elif cmd in ['r', 'reset']:
                        self.current_frame = 0
                        self.update_frame()
                        print("⏮️ Reset to first frame")
                    elif cmd in ['s', 'screenshot']:
                        filename = f"animation_frame_{self.current_frame:04d}.png"
                        self.vis.capture_screen_image(filename, do_render=True)
                        print(f"📸 Saved: {filename}")
                    
                except (EOFError, KeyboardInterrupt):
                    self.vis.close()
                    break
        
        threading.Thread(target=control_loop, daemon=True).start()
    
    def start_animation_thread(self):
        """Start animation playback thread."""
        def animation_loop():
            last_time = time.time()
            
            while True:
                if self.is_playing:
                    current_time = time.time()
                    if current_time - last_time >= self.frame_delay:
                        self.next_frame()
                        last_time = current_time
                
                time.sleep(0.01)
        
        threading.Thread(target=animation_loop, daemon=True).start()
    
    def next_frame(self):
        """Go to next frame."""
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.update_frame()
    
    def prev_frame(self):
        """Go to previous frame."""
        self.current_frame = (self.current_frame - 1) % len(self.frames)
        self.update_frame()
    
    def update_frame(self):
        """Update displayed frame."""
        self.vis.clear_geometries()
        self.vis.add_geometry(self.frames[self.current_frame])
        self.vis.update_renderer()


def generate_sample_data(data_type="sphere", num_points=2000):
    """Generate sample point cloud data."""
    if data_type == "sphere":
        phi = np.random.uniform(0, 2*np.pi, num_points)
        costheta = np.random.uniform(-1, 1, num_points)
        u = np.random.uniform(0, 1, num_points)
        
        theta = np.arccos(costheta)
        r = u ** (1/3)
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        points = np.column_stack([x, y, z])
        
        colors = np.column_stack([
            (phi / (2*np.pi)),
            (theta / np.pi),
            np.ones_like(phi) * 0.8
        ])
        
    elif data_type == "torus":
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
    
    else:  # Random or other
        points = np.random.randn(num_points, 3)
        colors = np.random.rand(num_points, 3)
    
    return points, colors 