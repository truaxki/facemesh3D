#!/usr/bin/env python3
"""rotate_pointcloud.py

Create 360-degree rotation animations from a single point cloud
==============================================================

This script takes a single PLY file and creates a rotating animation
by generating multiple frames with the point cloud rotated around an axis.

Usage:
    python rotate_pointcloud.py input.ply output_folder/ --frames 36 --axis y
"""

import numpy as np
import open3d as o3d
import os
import argparse
from pathlib import Path

def create_rotation_matrix(axis, angle_radians):
    """Create a rotation matrix for the specified axis and angle."""
    cos_a = np.cos(angle_radians)
    sin_a = np.sin(angle_radians)
    
    if axis.lower() == 'x':
        return np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ])
    elif axis.lower() == 'y':
        return np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])
    elif axis.lower() == 'z':
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])
    else:
        raise ValueError("Axis must be 'x', 'y', or 'z'")

def rotate_point_cloud_360(input_ply_path, output_dir, num_frames=36, axis='y', center_at_origin=True):
    """
    Create a 360-degree rotation animation from a single point cloud.
    
    Args:
        input_ply_path (str): Path to input PLY file
        output_dir (str): Output directory for animation frames
        num_frames (int): Number of frames in animation (default: 36 = 10° per frame)
        axis (str): Rotation axis - 'x', 'y', or 'z' (default: 'y')
        center_at_origin (bool): Whether to center the point cloud at origin before rotation
    
    Returns:
        list: Paths to generated frame files
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating {num_frames}-frame rotation animation")
    print(f"Input: {input_ply_path}")
    print(f"Output: {output_dir}")
    print(f"Rotation axis: {axis.upper()}")
    
    # Load the original point cloud
    try:
        pcd = o3d.io.read_point_cloud(input_ply_path)
        if len(pcd.points) == 0:
            raise ValueError("Point cloud is empty")
        print(f"Loaded point cloud with {len(pcd.points)} points")
    except Exception as e:
        print(f"Error loading {input_ply_path}: {e}")
        return []
    
    # Get original points and colors
    original_points = np.asarray(pcd.points)
    original_colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
    
    # Center at origin if requested
    if center_at_origin:
        centroid = np.mean(original_points, axis=0)
        original_points = original_points - centroid
        print(f"Centered at origin (moved by {centroid})")
    
    # Generate frames
    frame_paths = []
    angle_step = 2 * np.pi / num_frames  # Radians per frame
    
    for frame in range(num_frames):
        angle = frame * angle_step
        degrees = np.degrees(angle)
        
        # Create rotation matrix
        rotation_matrix = create_rotation_matrix(axis, angle)
        
        # Rotate points
        rotated_points = original_points @ rotation_matrix.T
        
        # Create new point cloud
        rotated_pcd = o3d.geometry.PointCloud()
        rotated_pcd.points = o3d.utility.Vector3dVector(rotated_points)
        
        if original_colors is not None:
            rotated_pcd.colors = o3d.utility.Vector3dVector(original_colors)
        
        # Estimate normals for better visualization
        rotated_pcd.estimate_normals()
        
        # Save frame
        frame_filename = f"frame_{frame:03d}_{degrees:06.1f}deg.ply"
        frame_path = os.path.join(output_dir, frame_filename)
        
        success = o3d.io.write_point_cloud(frame_path, rotated_pcd)
        if success:
            frame_paths.append(frame_path)
            print(f"  Frame {frame+1:2d}/{num_frames}: {degrees:6.1f}° -> {frame_filename}")
        else:
            print(f"  Failed to save frame {frame+1}")
    
    print(f"Animation complete! {len(frame_paths)} frames saved")
    print(f"Folder path for Streamlit: {os.path.abspath(output_dir)}")
    
    return frame_paths

def create_sample_point_cloud(output_path, shape='torus', num_points=2000):
    """Create a sample point cloud for testing."""
    
    print(f"Creating sample {shape} point cloud...")
    
    if shape == 'torus':
        # Create a torus
        u = np.random.uniform(0, 2*np.pi, num_points)
        v = np.random.uniform(0, 2*np.pi, num_points)
        
        major_r = 2.0
        minor_r = 0.8
        
        x = (major_r + minor_r * np.cos(v)) * np.cos(u)
        y = (major_r + minor_r * np.cos(v)) * np.sin(u)
        z = minor_r * np.sin(v)
        
        points = np.column_stack([x, y, z])
        
        # Rainbow colors based on angle
        colors = np.column_stack([
            (np.sin(u) + 1) / 2,
            (np.cos(u) + 1) / 2,
            (np.sin(v) + 1) / 2
        ])
        
    elif shape == 'helix':
        # Create a helix
        t = np.linspace(0, 6*np.pi, num_points)
        radius = 1.5
        
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = t / 3
        
        points = np.column_stack([x, y, z])
        
        # Color gradient along the helix
        colors = np.column_stack([
            t / (6*np.pi),
            0.5 * np.ones_like(t),
            1 - t / (6*np.pi)
        ])
        
    elif shape == 'sphere':
        # Create a sphere
        phi = np.random.uniform(0, 2*np.pi, num_points)
        costheta = np.random.uniform(-1, 1, num_points)
        u = np.random.uniform(0, 1, num_points)
        
        theta = np.arccos(costheta)
        r = 1.5 * (u ** (1/3))
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        
        points = np.column_stack([x, y, z])
        
        # Color by height
        colors = np.column_stack([
            (z + 1.5) / 3.0,
            np.zeros_like(z),
            1 - (z + 1.5) / 3.0
        ])
        
    else:
        raise ValueError(f"Unknown shape: {shape}")
    
    # Create and save point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    pcd.estimate_normals()
    
    success = o3d.io.write_point_cloud(output_path, pcd)
    if success:
        print(f"Sample {shape} saved to {output_path}")
        return output_path
    else:
        print(f"Failed to save sample {shape}")
        return None

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Create 360-degree rotation animations from point clouds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rotate existing PLY file around Y-axis (36 frames)
  python rotate_pointcloud.py my_cloud.ply animation_output/
  
  # Create 60-frame rotation around Z-axis  
  python rotate_pointcloud.py my_cloud.ply output/ --frames 60 --axis z
  
  # Create sample torus and animate it
  python rotate_pointcloud.py --sample torus sample_torus.ply output/
  
  # Create sample helix with custom frame count
  python rotate_pointcloud.py --sample helix sample_helix.ply output/ --frames 72
        """
    )
    
    parser.add_argument('input_ply', nargs='?', help='Input PLY file path')
    parser.add_argument('output_dir', nargs='?', help='Output directory for animation frames')
    parser.add_argument('--frames', type=int, default=36, help='Number of animation frames (default: 36)')
    parser.add_argument('--axis', choices=['x', 'y', 'z'], default='y', help='Rotation axis (default: y)')
    parser.add_argument('--no-center', action='store_true', help='Do not center point cloud at origin')
    parser.add_argument('--sample', choices=['torus', 'helix', 'sphere'], help='Create sample point cloud')
    parser.add_argument('--points', type=int, default=2000, help='Number of points for sample (default: 2000)')
    
    args = parser.parse_args()
    
    # Handle sample creation
    if args.sample:
        if not args.input_ply or not args.output_dir:
            print("For sample creation, provide: --sample <shape> <output_ply> <animation_dir>")
            return
        
        # Create sample point cloud
        sample_path = create_sample_point_cloud(args.input_ply, args.sample, args.points)
        if not sample_path:
            return
            
        input_ply = sample_path
        output_dir = args.output_dir
    else:
        if not args.input_ply or not args.output_dir:
            print("Required arguments: input_ply output_dir")
            print("Use --help for usage information")
            return
            
        input_ply = args.input_ply
        output_dir = args.output_dir
    
    # Check input file exists
    if not os.path.exists(input_ply):
        print(f"Input file not found: {input_ply}")
        return
    
    # Create rotation animation
    frame_paths = rotate_point_cloud_360(
        input_ply, 
        output_dir, 
        num_frames=args.frames,
        axis=args.axis,
        center_at_origin=not args.no_center
    )
    
    if frame_paths:
        print(f"\nSuccess! Created {len(frame_paths)} animation frames")
        print(f"Animation folder: {os.path.abspath(output_dir)}")
        print(f"Ready for Streamlit animation viewer!")
        print(f"\nNext steps:")
        print(f"   1. Run: python main.py")
        print(f"   2. Select 'Animation Folder'")
        print(f"   3. Enter path: {os.path.abspath(output_dir)}")
        print(f"   4. Enjoy your rotating point cloud!")

if __name__ == "__main__":
    main() 