"""Desktop Launcher Module

Handles launching and communication with the desktop Open3D viewer.
Clean interface for both single point clouds and animations.
"""

import os
import subprocess
from pathlib import Path
from source.file_manager import FileManager


class DesktopLauncher:
    """Launches desktop Open3D viewer with point cloud data."""
    
    @staticmethod
    def launch_single_viewer(points, colors, config):
        """Launch desktop viewer for a single point cloud."""
        try:
            # Save data temporarily
            ply_path, config_path, temp_dir = FileManager.save_point_cloud(points, colors, config)
            
            # Get simplified viewer script path
            script_path = Path(__file__).parent / "open3d_desktop_viewer_simple.py"
            
            # Build command
            cmd = [
                "python", str(script_path),
                "--file", ply_path
            ]
            
            # Launch in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux/Mac
                subprocess.Popen(cmd)
            
            return True, f"Desktop viewer launched with {len(points)} points"
            
        except Exception as e:
            return False, f"Failed to launch desktop viewer: {str(e)}"
    
    @staticmethod
    def launch_animation_viewer(frames_data, fps=10):
        """Launch desktop viewer for animation playback."""
        try:
            # Save animation data
            temp_dir, config_path, ply_paths = FileManager.save_animation_frames(frames_data)
            
            # Get simplified viewer script path
            script_path = Path(__file__).parent / "open3d_desktop_viewer_simple.py"
            
            # Build command for animation
            cmd = [
                "python", str(script_path),
                "--animation", config_path,
                "--fps", str(fps)
            ]
            
            # Launch in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux/Mac
                subprocess.Popen(cmd)
            
            return True, f"Animation viewer launched with {len(frames_data)} frames at {fps} FPS"
            
        except Exception as e:
            return False, f"Failed to launch animation viewer: {str(e)}"
    
    @staticmethod
    def get_launch_info():
        """Get information about desktop viewer capabilities."""
        script_path = Path(__file__).parent / "open3d_desktop_viewer_simple.py"
        
        return {
            'viewer_available': script_path.exists(),
            'features': [
                'Smooth mouse rotation',
                'Professional lighting',
                'High-quality rendering',
                'Screenshot capture',
                'Animation playback',
                'Keyboard controls'
            ],
            'controls': {
                'mouse': {
                    'left_drag': 'Rotate view',
                    'right_drag': 'Pan view',
                    'scroll': 'Zoom in/out',
                    'middle_click': 'Reset view'
                },
                'keyboard': {
                    'enter': 'Change background',
                    's': 'Save screenshot',
                    'spacebar': 'Play/pause animation (animation mode)',
                    'n/p': 'Next/previous frame (animation mode)',
                    'q': 'Quit viewer'
                }
            }
        }
    
    @staticmethod
    def get_manual_commands():
        """Get manual command examples for troubleshooting."""
        return {
            'single_pointcloud': 'python source/open3d_desktop_viewer_simple.py --file pointcloud.ply',
            'animation': 'python source/open3d_desktop_viewer_simple.py --animation config.json --fps 10',
            'help': 'python source/open3d_desktop_viewer_simple.py --help'
        } 