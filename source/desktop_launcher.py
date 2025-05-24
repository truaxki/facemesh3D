"""Desktop Launcher Module

Handles launching and communication with the desktop Open3D viewer.
Clean interface for both single point clouds and animations.
Enhanced with interactive animation player using Open3D callbacks.
"""

import os
import subprocess
from pathlib import Path
from source.file_manager import FileManager
from source.animation_player import play_animation_interactive


class DesktopLauncher:
    """Launches desktop Open3D viewer with point cloud data."""
    
    @staticmethod
    def launch_single_viewer(points, colors, config):
        """Launch desktop viewer for a single point cloud."""
        try:
            # Save data temporarily
            ply_path, config_path, temp_dir = FileManager.save_point_cloud(points, colors, config)
            
            # Get script paths (absolute)
            script_path = Path(__file__).parent.absolute() / "open3d_desktop_viewer_simple.py"
            project_root = Path(__file__).parent.parent.absolute()
            
            # Build command with absolute paths
            cmd = [
                "python", str(script_path),
                "--file", str(ply_path)
            ]
            
            # Launch in background with correct working directory
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=str(project_root))
            else:  # Unix/Linux/Mac
                subprocess.Popen(cmd, cwd=str(project_root))
            
            return True, f"Desktop viewer launched with {len(points)} points"
            
        except Exception as e:
            return False, f"Failed to launch desktop viewer: {str(e)}"
    
    @staticmethod
    def launch_animation_viewer(frames_data, fps=10):
        """Launch desktop viewer for animation playback (file-based)."""
        try:
            # Save animation data
            temp_dir, config_path, ply_paths = FileManager.save_animation_frames(frames_data)
            
            # Get script paths (absolute)
            script_path = Path(__file__).parent.absolute() / "open3d_desktop_viewer_simple.py"
            project_root = Path(__file__).parent.parent.absolute()
            
            # Build command for animation with absolute paths
            cmd = [
                "python", str(script_path),
                "--animation", str(config_path),
                "--fps", str(fps)
            ]
            
            # Launch in background with correct working directory
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=str(project_root))
            else:  # Unix/Linux/Mac
                subprocess.Popen(cmd, cwd=str(project_root))
            
            return True, f"Animation viewer launched with {len(frames_data)} frames at {fps} FPS"
            
        except Exception as e:
            return False, f"Failed to launch animation viewer: {str(e)}"
    
    @staticmethod
    def launch_interactive_animation_player(frames_data, fps=15):
        """Launch enhanced interactive animation player (memory-based).
        
        This uses Open3D's animation callback system for smooth real-time playback
        with interactive controls. No temporary files needed.
        """
        try:
            print(f"🎬 Launching Interactive Animation Player...")
            print(f"   📊 {len(frames_data)} frames at {fps} FPS")
            print(f"   ⏱️ Duration: {len(frames_data)/fps:.1f} seconds")
            
            # Launch the interactive player directly
            success = play_animation_interactive(frames_data, fps)
            
            if success:
                return True, f"Interactive animation player completed with {len(frames_data)} frames"
            else:
                return False, "Interactive animation player failed to start"
                
        except Exception as e:
            return False, f"Failed to launch interactive animation player: {str(e)}"
    
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
                'Interactive animation player',
                'Real-time controls',
                'Variable speed playback',
                'Frame stepping',
                'Keyboard controls'
            ],
            'animation_modes': {
                'file_based': {
                    'name': 'File-based Animation Viewer',
                    'description': 'Traditional viewer that loads frames from files',
                    'pros': ['Simple', 'Reliable'],
                    'cons': ['File I/O overhead', 'Less interactive']
                },
                'interactive': {
                    'name': 'Interactive Animation Player',
                    'description': 'Enhanced player using Open3D animation callbacks',
                    'pros': ['Smooth playback', 'Real-time controls', 'No file overhead', 'Variable speed'],
                    'cons': ['Memory intensive for large animations']
                }
            },
            'controls': {
                'mouse': {
                    'left_drag': 'Rotate view',
                    'right_drag': 'Pan view',
                    'scroll': 'Zoom in/out',
                    'middle_click': 'Reset view'
                },
                'keyboard_in_window': {
                    'spacebar': 'Play/pause animation',
                    'n/p': 'Next/previous frame',
                    'r': 'Reverse direction',
                    'l': 'Toggle loop mode',
                    '=/−': 'Speed up/down',
                    '0/9': 'First/last frame',
                    'b': 'Change background',
                    's': 'Save screenshot',
                    'h': 'Show help',
                    'q': 'Quit viewer'
                }
            }
        }
    
    @staticmethod
    def get_manual_commands():
        """Get manual command examples for troubleshooting."""
        return {
            'single_pointcloud': 'python source/open3d_desktop_viewer_simple.py --file pointcloud.ply',
            'animation_file_based': 'python source/open3d_desktop_viewer_simple.py --animation config.json --fps 10',
            'interactive_player': 'Available only through Streamlit interface',
            'help': 'python source/open3d_desktop_viewer_simple.py --help'
        } 