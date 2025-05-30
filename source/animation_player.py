"""Animation Player Module

Enhanced Open3D animation player using callback-based animation system.
Provides smooth real-time playback with interactive controls in the 3D window.
"""

import open3d as o3d
import numpy as np
import time
import threading
import sys
import ctypes
from typing import List, Dict, Any


class InteractiveAnimationPlayer:
    """Enhanced animation player using Open3D's key callback system."""
    
    def __init__(self, frames_data: List[Dict[str, Any]], fps: int = 15):
        """Initialize animation player.
        
        Args:
            frames_data: List of frame dictionaries with 'points' and 'colors'
            fps: Frames per second for playback
        """
        self.frames_data = frames_data
        self.fps = fps
        self.frame_delay = 1.0 / fps
        
        # Animation state
        self.current_frame = 0
        self.is_playing = False
        self.loop_animation = True
        self.reverse_direction = False
        
        # Viewer objects
        self.vis = None
        self.point_cloud = None
        
        # Control state
        self.running = True
        self.speed_multiplier = 1.0
        self.last_frame_time = 0
        
        # Colors for background cycling
        self.bg_colors = [
            ([0.05, 0.05, 0.2], "Deep Blue"),
            ([0, 0, 0], "Black"), 
            ([0.1, 0.1, 0.1], "Dark Gray"),
            ([0.2, 0.15, 0.1], "Warm Dark"),
        ]
        self.bg_index = 0
    
    def setup_visualizer(self):
        """Setup Open3D visualizer with key callbacks."""
        # Use VisualizerWithKeyCallback for in-window controls
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        window_title = f"🎬 Interactive Animation Player - {len(self.frames_data)} frames"
        self.vis.create_window(window_name=window_title, width=1400, height=900)
        
        # Configure rendering for high-quality animation
        render_opt = self.vis.get_render_option()
        render_opt.background_color = np.array(self.bg_colors[0][0])
        render_opt.point_size = 2.5
        render_opt.show_coordinate_frame = True
        render_opt.light_on = True
        
        # Create initial point cloud from first frame
        if self.frames_data:
            frame_data = self.frames_data[0]
            self.point_cloud = o3d.geometry.PointCloud()
            self.point_cloud.points = o3d.utility.Vector3dVector(frame_data['points'])
            if frame_data['colors'] is not None:
                self.point_cloud.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            
            # Estimate normals for better lighting
            self.point_cloud.estimate_normals()
            
            # Add to visualizer
            self.vis.add_geometry(self.point_cloud)
        
        # Register key callbacks for in-window controls
        self.register_key_callbacks()
        
        return window_title
    
    def register_key_callbacks(self):
        """Register key callbacks for in-window controls."""
        # Playback controls
        self.vis.register_key_callback(ord(" "), self.on_key_space)  # Space - play/pause
        self.vis.register_key_callback(ord("N"), self.on_key_next)   # N - next frame
        self.vis.register_key_callback(ord("P"), self.on_key_prev)   # P - previous frame
        self.vis.register_key_callback(ord("R"), self.on_key_reverse) # R - reverse direction
        self.vis.register_key_callback(ord("L"), self.on_key_loop)   # L - toggle loop
        
        # Navigation controls
        self.vis.register_key_callback(ord("0"), self.on_key_first)  # 0 - first frame
        self.vis.register_key_callback(ord("9"), self.on_key_last)   # 9 - last frame
        
        # Speed controls
        self.vis.register_key_callback(ord("="), self.on_key_faster) # = - faster
        self.vis.register_key_callback(ord("-"), self.on_key_slower) # - - slower
        self.vis.register_key_callback(ord("1"), self.on_key_normal) # 1 - normal speed
        
        # Other controls
        self.vis.register_key_callback(ord("B"), self.on_key_background) # B - background
        self.vis.register_key_callback(ord("S"), self.on_key_screenshot) # S - screenshot
        self.vis.register_key_callback(ord("H"), self.on_key_help)       # H - help
        self.vis.register_key_callback(ord("Q"), self.on_key_quit)       # Q - quit
        
        print("🎮 Key controls registered in 3D window!")
        self.print_controls()
    
    def animation_callback(self, vis):
        """Main animation callback - called by Open3D's animation loop."""
        current_time = time.time()
        
        if self.is_playing and self.frames_data:
            # Check if enough time has passed for next frame
            time_since_last_frame = current_time - self.last_frame_time
            target_delay = self.frame_delay / self.speed_multiplier
            
            if time_since_last_frame >= target_delay:
                # Calculate next frame based on direction
                if self.reverse_direction:
                    next_frame = self.current_frame - 1
                    if next_frame < 0:
                        next_frame = len(self.frames_data) - 1 if self.loop_animation else 0
                        if not self.loop_animation:
                            self.is_playing = False
                            print("⏹️ Reached beginning - stopped")
                else:
                    next_frame = self.current_frame + 1
                    if next_frame >= len(self.frames_data):
                        next_frame = 0 if self.loop_animation else len(self.frames_data) - 1
                        if not self.loop_animation:
                            self.is_playing = False
                            print("⏹️ Reached end - stopped")
                
                # Update to next frame
                self.update_to_frame(next_frame)
                self.last_frame_time = current_time
                
                # Debug output every 10 frames
                if self.current_frame % 10 == 0:
                    print(f"🎬 Frame {self.current_frame + 1}/{len(self.frames_data)} ({self.fps * self.speed_multiplier:.1f} FPS)")
        
        return False  # Continue animation loop
    
    def update_to_frame(self, frame_index: int):
        """Update visualization to specific frame."""
        if 0 <= frame_index < len(self.frames_data):
            self.current_frame = frame_index
            frame_data = self.frames_data[frame_index]
            
            # Update point cloud data
            self.point_cloud.points = o3d.utility.Vector3dVector(frame_data['points'])
            if frame_data['colors'] is not None:
                self.point_cloud.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            
            # Re-estimate normals for updated geometry
            self.point_cloud.estimate_normals()
            
            # Update visualization - try multiple approaches for compatibility
            try:
                # Method 1: Update existing geometry (preferred)
                self.vis.update_geometry(self.point_cloud)
                self.vis.update_renderer()
            except:
                # Method 2: Clear and re-add geometry (fallback)
                self.vis.clear_geometries()
                self.vis.add_geometry(self.point_cloud)
                self.vis.update_renderer()
    
    # Key callback functions - these run in the 3D window
    def on_key_space(self, vis):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing
        self.last_frame_time = time.time()  # Reset timing
        status = "▶️ Playing" if self.is_playing else "⏸️ Paused"
        speed_info = f" ({self.fps * self.speed_multiplier:.1f} FPS)" if self.is_playing else ""
        print(f"{status}{speed_info}")
        return False
    
    def on_key_next(self, vis):
        """Next frame."""
        next_frame = (self.current_frame + 1) % len(self.frames_data)
        self.update_to_frame(next_frame)
        print(f"➡️ Frame {self.current_frame + 1}/{len(self.frames_data)}")
        return False
    
    def on_key_prev(self, vis):
        """Previous frame."""
        prev_frame = (self.current_frame - 1) % len(self.frames_data)
        self.update_to_frame(prev_frame)
        print(f"⬅️ Frame {self.current_frame + 1}/{len(self.frames_data)}")
        return False
    
    def on_key_reverse(self, vis):
        """Toggle reverse direction."""
        self.reverse_direction = not self.reverse_direction
        direction = "⏪ Backward" if self.reverse_direction else "⏩ Forward"
        print(f"🔄 Direction: {direction}")
        return False
    
    def on_key_loop(self, vis):
        """Toggle loop mode."""
        self.loop_animation = not self.loop_animation
        status = "🔁 Loop ON" if self.loop_animation else "➡️ Loop OFF"
        print(status)
        return False
    
    def on_key_first(self, vis):
        """Go to first frame."""
        self.update_to_frame(0)
        print(f"⏮️ First frame: {self.current_frame + 1}")
        return False
    
    def on_key_last(self, vis):
        """Go to last frame."""
        self.update_to_frame(len(self.frames_data) - 1)
        print(f"⏭️ Last frame: {self.current_frame + 1}")
        return False
    
    def on_key_faster(self, vis):
        """Increase speed."""
        self.speed_multiplier *= 1.5
        self.speed_multiplier = min(5.0, self.speed_multiplier)  # Cap at 5x
        print(f"⚡ Speed: {self.fps * self.speed_multiplier:.1f} FPS (faster)")
        return False
    
    def on_key_slower(self, vis):
        """Decrease speed."""
        self.speed_multiplier *= 0.75
        self.speed_multiplier = max(0.1, self.speed_multiplier)  # Cap at 0.1x
        print(f"🐌 Speed: {self.fps * self.speed_multiplier:.1f} FPS (slower)")
        return False
    
    def on_key_normal(self, vis):
        """Reset to normal speed."""
        self.speed_multiplier = 1.0
        print(f"🎯 Speed: {self.fps * self.speed_multiplier:.1f} FPS (normal)")
        return False
    
    def on_key_background(self, vis):
        """Cycle background colors."""
        self.bg_index = (self.bg_index + 1) % len(self.bg_colors)
        color, name = self.bg_colors[self.bg_index]
        render_opt = self.vis.get_render_option()
        render_opt.background_color = np.array(color)
        print(f"🎨 Background: {name}")
        return False
    
    def on_key_screenshot(self, vis):
        """Save screenshot."""
        filename = f"animation_frame_{self.current_frame:04d}.png"
        self.vis.capture_screen_image(filename, do_render=True)
        print(f"📸 Screenshot: {filename}")
        return False
    
    def on_key_help(self, vis):
        """Show help."""
        self.print_controls()
        return False
    
    def on_key_quit(self, vis):
        """Quit player."""
        print("👋 Closing animation player...")
        self.vis.close()
        return False
    
    def bring_window_to_front(self, window_title: str):
        """Bring Open3D window to front (Windows only)."""
        if sys.platform != "win32":
            return
        
        def focus_window():
            try:
                time.sleep(1.0)
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, window_title)
                if hwnd:
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    user32.SetActiveWindow(hwnd)
            except Exception:
                pass  # Ignore errors, not critical
        
        threading.Timer(0.5, focus_window).start()
    
    def print_controls(self):
        """Print control instructions."""
        print("\n" + "="*70)
        print("🎬 INTERACTIVE ANIMATION PLAYER - IN-WINDOW CONTROLS")
        print("="*70)
        print("🖱️ Mouse Controls (in 3D window):")
        print("   Left drag      : Rotate view")
        print("   Right drag     : Pan view") 
        print("   Scroll         : Zoom in/out")
        print("   Middle click   : Reset view")
        print()
        print("⌨️ Keyboard Controls (in 3D window):")
        print("   SPACEBAR       : ▶️⏸️ Play/pause animation")
        print("   N              : ➡️ Next frame")
        print("   P              : ⬅️ Previous frame")
        print("   R              : 🔄 Reverse direction")
        print("   L              : 🔁 Toggle loop mode")
        print("   0              : ⏮️ First frame")
        print("   9              : ⏭️ Last frame")
        print("   =              : ⚡ Faster (1.5x)")
        print("   -              : 🐌 Slower (0.75x)")
        print("   1              : 🎯 Normal speed")
        print("   B              : 🎨 Change background")
        print("   S              : 📸 Save screenshot")
        print("   H              : ❓ Show this help")
        print("   Q              : 👋 Quit")
        print("="*70)
        print(f"📊 Animation: {len(self.frames_data)} frames at {self.fps} FPS")
        print(f"⏱️ Duration: {len(self.frames_data)/self.fps:.1f} seconds")
        print(f"🎮 All controls work directly in the 3D window!")
        print("💡 Press SPACEBAR in the 3D window to start playing!")
        print("="*70)
    
    def play_animation(self):
        """Start the interactive animation player."""
        print("🎬 Starting Interactive Animation Player...")
        
        # Setup visualizer with key callbacks
        window_title = self.setup_visualizer()
        
        # Register animation callback with Open3D
        self.vis.register_animation_callback(self.animation_callback)
        
        # Initialize timing
        self.last_frame_time = time.time()
        
        # Bring window to front
        self.bring_window_to_front(window_title)
        
        print(f"✅ Animation player ready!")
        print(f"🎮 Window: {window_title}")
        print("💡 Press SPACEBAR in the 3D window to start playing!")
        print("💡 Press H in the 3D window for help with all controls!")
        
        # Run the visualizer (this will block until window is closed)
        self.vis.run()
        self.vis.destroy_window()
        
        print("✅ Animation player closed")
        return True


def create_animation_player(frames_data: List[Dict[str, Any]], fps: int = 15) -> InteractiveAnimationPlayer:
    """Create and return an interactive animation player."""
    return InteractiveAnimationPlayer(frames_data, fps)


def play_animation_interactive(frames_data: List[Dict[str, Any]], fps: int = 15) -> bool:
    """Launch interactive animation player and return success status."""
    try:
        player = create_animation_player(frames_data, fps)
        player.play_animation()
        return True
    except Exception as e:
        print(f"❌ Animation player error: {e}")
        return False


class ComparisonAnimationPlayer(InteractiveAnimationPlayer):
    """Side-by-side comparison animation player for original vs transformed point clouds."""
    
    def __init__(self, original_frames: List[Dict[str, Any]], transformed_frames: List[Dict[str, Any]], 
                 fps: int = 15, comparison_label: str = "Original vs Transformed"):
        """Initialize comparison animation player.
        
        Args:
            original_frames: List of original frame dictionaries
            transformed_frames: List of transformed frame dictionaries
            fps: Frames per second for playback
            comparison_label: Label for the comparison (e.g., "Original vs Kabsch-aligned")
        """
        # Store both sets of frames
        self.original_frames = original_frames
        self.transformed_frames = transformed_frames
        self.comparison_label = comparison_label
        
        # Initialize parent with transformed frames (for compatibility)
        super().__init__(transformed_frames, fps)
        
        # Additional state for comparison
        self.point_cloud_original = None
        self.point_cloud_transformed = None
        self.separation_distance = 0.0  # Will be calculated based on bounding box
        
        # Text labels
        self.text_original = None
        self.text_transformed = None
    
    def calculate_separation_distance(self):
        """Calculate appropriate separation distance based on point cloud size."""
        if self.original_frames:
            # Get bounding box of first frame
            points = self.original_frames[0]['points']
            min_bounds = np.min(points, axis=0)
            max_bounds = np.max(points, axis=0)
            bbox_diagonal = np.linalg.norm(max_bounds - min_bounds)
            
            # Set separation to 0.75x the bounding box diagonal (reduced from 1.5x)
            self.separation_distance = bbox_diagonal * 0.75
            
            print(f"📏 Separation distance: {self.separation_distance:.2f}")
    
    def setup_visualizer(self):
        """Setup Open3D visualizer with side-by-side point clouds."""
        # Use VisualizerWithKeyCallback for in-window controls
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        window_title = f"🎬 Comparison: {self.comparison_label} - {len(self.original_frames)} frames"
        self.vis.create_window(window_name=window_title, width=1600, height=900)
        
        # Configure rendering
        render_opt = self.vis.get_render_option()
        render_opt.background_color = np.array([0.05, 0.05, 0.2])
        render_opt.point_size = 2.5
        render_opt.show_coordinate_frame = False  # Hide coordinate frame for cleaner view
        render_opt.light_on = True
        
        # Calculate separation distance
        self.calculate_separation_distance()
        
        # Create point clouds for both original and transformed
        if self.original_frames and self.transformed_frames:
            # Original point cloud (left side)
            frame_data = self.original_frames[0]
            self.point_cloud_original = o3d.geometry.PointCloud()
            
            # Shift original to the left
            shifted_points = frame_data['points'] - np.array([self.separation_distance/2, 0, 0])
            self.point_cloud_original.points = o3d.utility.Vector3dVector(shifted_points)
            
            if frame_data['colors'] is not None:
                self.point_cloud_original.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            else:
                # Default color for original (light blue)
                colors = np.ones((len(frame_data['points']), 3)) * [0.5, 0.7, 1.0]
                self.point_cloud_original.colors = o3d.utility.Vector3dVector(colors)
            
            self.point_cloud_original.estimate_normals()
            
            # Transformed point cloud (right side)
            frame_data = self.transformed_frames[0]
            self.point_cloud_transformed = o3d.geometry.PointCloud()
            
            # Shift transformed to the right
            shifted_points = frame_data['points'] + np.array([self.separation_distance/2, 0, 0])
            self.point_cloud_transformed.points = o3d.utility.Vector3dVector(shifted_points)
            
            if frame_data['colors'] is not None:
                self.point_cloud_transformed.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            
            self.point_cloud_transformed.estimate_normals()
            
            # Add both to visualizer
            self.vis.add_geometry(self.point_cloud_original)
            self.vis.add_geometry(self.point_cloud_transformed)
            
            # Add text labels (if Open3D version supports it)
            try:
                # Create coordinate frames as labels
                coord_frame_original = o3d.geometry.TriangleMesh.create_coordinate_frame(
                    size=self.separation_distance * 0.1, 
                    origin=[-self.separation_distance/2, -self.separation_distance*0.4, 0]
                )
                coord_frame_transformed = o3d.geometry.TriangleMesh.create_coordinate_frame(
                    size=self.separation_distance * 0.1,
                    origin=[self.separation_distance/2, -self.separation_distance*0.4, 0]
                )
                self.vis.add_geometry(coord_frame_original)
                self.vis.add_geometry(coord_frame_transformed)
            except:
                pass  # Ignore if coordinate frames fail
        
        # Register key callbacks
        self.register_key_callbacks()
        
        # Add comparison-specific controls
        self.vis.register_key_callback(ord("C"), self.on_key_center_view)  # C - center view
        
        # Reset view to show both
        self.vis.reset_view_point(True)
        
        return window_title
    
    def update_to_frame(self, frame_index: int):
        """Update both point clouds to specific frame."""
        if 0 <= frame_index < len(self.original_frames):
            self.current_frame = frame_index
            
            # Update original point cloud
            frame_data = self.original_frames[frame_index]
            shifted_points = frame_data['points'] - np.array([self.separation_distance/2, 0, 0])
            self.point_cloud_original.points = o3d.utility.Vector3dVector(shifted_points)
            
            if frame_data['colors'] is not None:
                self.point_cloud_original.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            else:
                # Keep default color
                colors = np.ones((len(frame_data['points']), 3)) * [0.5, 0.7, 1.0]
                self.point_cloud_original.colors = o3d.utility.Vector3dVector(colors)
            
            self.point_cloud_original.estimate_normals()
            
            # Update transformed point cloud
            frame_data = self.transformed_frames[frame_index]
            shifted_points = frame_data['points'] + np.array([self.separation_distance/2, 0, 0])
            self.point_cloud_transformed.points = o3d.utility.Vector3dVector(shifted_points)
            
            if frame_data['colors'] is not None:
                self.point_cloud_transformed.colors = o3d.utility.Vector3dVector(frame_data['colors'])
            
            self.point_cloud_transformed.estimate_normals()
            
            # Update visualization
            try:
                self.vis.update_geometry(self.point_cloud_original)
                self.vis.update_geometry(self.point_cloud_transformed)
                self.vis.update_renderer()
            except:
                # Fallback method
                self.vis.clear_geometries()
                self.vis.add_geometry(self.point_cloud_original)
                self.vis.add_geometry(self.point_cloud_transformed)
                self.vis.update_renderer()
    
    def on_key_center_view(self, vis):
        """Center the view to show both point clouds."""
        self.vis.reset_view_point(True)
        print("🎯 View centered on both point clouds")
        return False
    
    def print_controls(self):
        """Print control instructions with comparison-specific additions."""
        super().print_controls()
        print("\n⚡ Comparison-Specific Controls:")
        print("   C              : 🎯 Center view on both")
        print(f"\n📊 Comparison: {self.comparison_label}")
        print(f"   Left side: Original")
        print(f"   Right side: Transformed")


def play_comparison_animation(original_frames: List[Dict[str, Any]], 
                            transformed_frames: List[Dict[str, Any]], 
                            fps: int = 15,
                            comparison_label: str = "Original vs Transformed") -> bool:
    """Launch side-by-side comparison animation player."""
    try:
        player = ComparisonAnimationPlayer(original_frames, transformed_frames, fps, comparison_label)
        player.play_animation()
        return True
    except Exception as e:
        print(f"❌ Comparison animation player error: {e}")
        return False 