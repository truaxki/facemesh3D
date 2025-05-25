#!/usr/bin/env python3
"""open3d_desktop_viewer_simple.py

Simplified Open3D desktop viewer - under 200 lines.
Uses modular architecture for better maintainability.

Run: python source/open3d_desktop_viewer_simple.py
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add current directory to path for module imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import open3d as o3d

try:
    from viewer_core import ViewerCore, InteractiveControls, AnimationViewer, generate_sample_data
except ImportError:
    print("Warning: Could not import viewer_core. Some functionality may be limited.")
    ViewerCore = None


def load_point_cloud_from_file(file_path):
    """Load point cloud from file."""
    try:
        pcd = o3d.io.read_point_cloud(file_path)
        if len(pcd.points) == 0:
            raise ValueError("File is empty or invalid")
        return pcd
    except Exception as e:
        raise RuntimeError(f"Could not load {file_path}: {e}")


def run_single_viewer(args):
    """Run single point cloud viewer."""
    print("🖥️ Open3D Interactive Desktop Viewer")
    print("=" * 50)
    
    # Load or generate point cloud
    if args.file:
        print(f"📂 Loading: {args.file}")
        pcd = load_point_cloud_from_file(args.file)
        print(f"✅ Loaded {len(pcd.points)} points")
        window_title = f"Open3D Viewer - {args.file}"
    else:
        print(f"🎲 Generating {args.type} with {args.points} points...")
        points, colors = generate_sample_data(args.type, args.points)
        pcd = ViewerCore.create_point_cloud(points, colors)
        print(f"✅ Generated {len(pcd.points)} points")
        window_title = f"Open3D Viewer - {args.type.title()}"
    
    # Create and setup visualizer
    vis = ViewerCore.setup_visualizer(window_title)
    vis.add_geometry(pcd)
    
    # Start interactive controls
    controls = InteractiveControls(vis)
    controls.start_control_thread()
    
    # Focus window and show instructions
    ViewerCore.bring_window_to_front(window_title)
    
    print(f"\n🎮 3D Window opened!")
    print("   🖱️ Mouse: Drag to rotate, right-drag to pan, scroll to zoom")
    print("   ⌨️ Terminal: Press ENTER to change background, 's' to screenshot")
    print("\n💡 If window isn't visible, check your taskbar!")
    
    # Run viewer
    vis.run()
    vis.destroy_window()
    print("✅ Viewer closed")


def run_animation_viewer(args):
    """Run animation viewer."""
    print("🎬 Open3D Animation Viewer")
    print("=" * 50)
    
    try:
        # Load animation config
        print(f"📂 Loading animation: {args.animation}")
        with open(args.animation, 'r') as f:
            config = json.load(f)
        
        frame_paths = config.get('frame_paths', [])
        if not frame_paths:
            raise ValueError("No frame paths found in animation config")
        
        print(f"📋 Found {len(frame_paths)} animation frames")
        
        # Create and run animation viewer
        anim_viewer = AnimationViewer(frame_paths, args.fps)
        anim_viewer.load_frames()
        anim_viewer.start_viewer()
        
    except Exception as e:
        print(f"❌ Animation error: {e}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive Open3D Point Cloud Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s --type sphere --points 5000
  python %(prog)s --file pointcloud.ply
  python %(prog)s --animation config.json --fps 15

Controls:
  Mouse: Drag=rotate, Right-drag=pan, Scroll=zoom
  Keys: ENTER=background, s=screenshot, q=quit
  Animation: SPACE=play/pause, n/p=next/prev frame
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--file", type=str, 
                           help="Load point cloud from file (PLY/PCD/XYZ)")
    mode_group.add_argument("--animation", type=str, 
                           help="Load animation config JSON file")
    
    # Generation options
    parser.add_argument("--type", choices=["sphere", "torus", "random"], 
                       default="sphere", help="Type of point cloud to generate")
    parser.add_argument("--points", type=int, default=3000, 
                       help="Number of points to generate")
    
    # Animation options
    parser.add_argument("--fps", type=int, default=10, 
                       help="Animation FPS (frames per second)")
    
    return parser.parse_args()


def print_startup_info():
    """Print startup information."""
    print("🚀 Open3D Desktop Viewer (Simplified)")
    print("   Real interactivity vs. Streamlit's limited matplotlib!")
    print("   Smooth rotation, professional lighting, high-quality rendering")


def main():
    """Main entry point."""
    print_startup_info()
    
    try:
        args = parse_arguments()
        
        # Route to appropriate viewer
        if args.animation:
            run_animation_viewer(args)
        else:
            run_single_viewer(args)
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try: python source/open3d_desktop_viewer_simple.py --help")


if __name__ == "__main__":
    main() 