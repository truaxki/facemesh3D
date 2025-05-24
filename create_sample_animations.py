#!/usr/bin/env python3
"""create_sample_animations.py

Quick script to create sample point cloud animations for testing
==============================================================

This script creates several demo animations that you can immediately
test with the Streamlit animation viewer.
"""

import os
import subprocess
from pathlib import Path

def run_animation_creation(sample_type, output_dir, frames=24, axis='y', points=2000):
    """Run the rotation script to create an animation."""
    ply_filename = f"sample_{sample_type}.ply"
    
    cmd = [
        "python", "rotate_pointcloud.py",
        "--sample", sample_type,
        ply_filename, output_dir,
        "--frames", str(frames),
        "--axis", axis,
        "--points", str(points)
    ]
    
    print(f"Creating {sample_type} animation ({frames} frames, {axis}-axis rotation)...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  {sample_type} animation created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Failed to create {sample_type} animation: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Create multiple sample animations."""
    print("Creating Sample Point Cloud Animations")
    print("=" * 50)
    
    animations = [
        # (sample_type, output_dir, frames, axis, points)
        ("torus", "animations/torus_y_24", 24, "y", 2000),
        ("helix", "animations/helix_z_36", 36, "z", 2000),
        ("sphere", "animations/sphere_x_30", 30, "x", 1500),
        ("torus", "animations/torus_z_48", 48, "z", 3000),  # High-res torus rotating on Z
    ]
    
    successful = 0
    total = len(animations)
    
    for sample_type, output_dir, frames, axis, points in animations:
        success = run_animation_creation(sample_type, output_dir, frames, axis, points)
        if success:
            successful += 1
        print()  # Empty line for spacing
    
    print(f"Summary: {successful}/{total} animations created successfully!")
    
    if successful > 0:
        print("\nReady to test! Here are your animation folders:")
        for sample_type, output_dir, frames, axis, points in animations:
            full_path = os.path.abspath(output_dir)
            print(f"   {output_dir} -> {full_path}")
        
        print(f"\nTo view animations:")
        print(f"   1. Run: python main.py")
        print(f"   2. Select 'Animation Folder' in sidebar")
        print(f"   3. Paste one of the paths above")
        print(f"   4. Watch your rotating point cloud!")
        
        print(f"\nOr launch animated desktop viewer directly:")
        print(f"   python source/open3d_desktop_viewer.py --animation [folder]/animation_config.json")

if __name__ == "__main__":
    main() 