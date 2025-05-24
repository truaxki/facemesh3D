#!/usr/bin/env python3
"""matrix_to_pointcloud_example.py

Simple examples showing how to convert Nx3 matrices to Open3D point clouds.
This demonstrates the core concepts without the complexity of a full UI.

Run: python source/matrix_to_pointcloud_example.py
"""

import numpy as np
import open3d as o3d


def example_1_basic_conversion():
    """Basic example: Nx3 matrix → Open3D PointCloud."""
    print("=== Example 1: Basic Matrix → PointCloud ===")
    
    # Create sample data (your Nx3 matrix)
    points = np.array([
        [0.0, 0.0, 0.0],  # origin
        [1.0, 0.0, 0.0],  # x-axis
        [0.0, 1.0, 0.0],  # y-axis  
        [0.0, 0.0, 1.0],  # z-axis
        [1.0, 1.0, 1.0],  # corner
    ], dtype=np.float64)
    
    print(f"Input matrix shape: {points.shape}")
    print("Points:\n", points)
    
    # Convert to Open3D PointCloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Add normals
    pcd.estimate_normals()
    
    print(f"PointCloud has {len(pcd.points)} points")
    print(f"PointCloud has {len(pcd.normals)} normals")
    
    # Save to file
    o3d.io.write_point_cloud("example1_basic.ply", pcd)
    print("Saved: example1_basic.ply")
    
    return pcd


def example_2_with_colors():
    """Example with colors: Nx3 points + Nx3 colors."""
    print("\n=== Example 2: Points + Colors ===")
    
    # Generate random sphere
    n_points = 1000
    
    # Uniform sphere distribution  
    phi = np.random.uniform(0, 2*np.pi, n_points)
    costheta = np.random.uniform(-1, 1, n_points)
    u = np.random.uniform(0, 1, n_points)
    
    theta = np.arccos(costheta)
    r = u ** (1/3)  # Uniform in volume
    
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi) 
    z = r * np.cos(theta)
    points = np.column_stack([x, y, z])
    
    # Create colors based on position
    colors = np.column_stack([
        (x + 1) / 2,      # Red: X coordinate
        (y + 1) / 2,      # Green: Y coordinate  
        (z + 1) / 2       # Blue: Z coordinate
    ])
    
    print(f"Points shape: {points.shape}")
    print(f"Colors shape: {colors.shape}")
    print(f"Color range: [{colors.min():.3f}, {colors.max():.3f}]")
    
    # Convert to Open3D
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    pcd.estimate_normals()
    
    # Save
    o3d.io.write_point_cloud("example2_colored.ply", pcd)
    print("Saved: example2_colored.ply")
    
    return pcd


def example_3_from_csv():
    """Example: Load Nx3 matrix from CSV file."""
    print("\n=== Example 3: Load from CSV ===")
    
    # Create sample CSV data
    csv_data = """0.0,0.0,0.0
1.0,0.0,0.0
0.5,0.866,0.0
-0.5,0.866,0.0
-1.0,0.0,0.0
-0.5,-0.866,0.0
0.5,-0.866,0.0"""
    
    # Save to file
    with open("sample_points.csv", "w") as f:
        f.write(csv_data)
    
    # Load matrix from CSV
    points = np.loadtxt("sample_points.csv", delimiter=",")
    print(f"Loaded {points.shape[0]} points from CSV")
    print("Points:\n", points)
    
    # Convert to PointCloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.estimate_normals()
    
    # Paint uniform color
    pcd.paint_uniform_color([0.7, 0.3, 0.9])  # Purple
    
    o3d.io.write_point_cloud("example3_from_csv.ply", pcd)
    print("Saved: example3_from_csv.ply")
    
    return pcd


def example_4_streamlit_compatible():
    """Example: Streamlit-compatible workflow (no GUI)."""
    print("\n=== Example 4: Streamlit-Compatible ===")
    
    # Generate data
    points = np.random.randn(500, 3)  # Random Gaussian cloud
    
    # Create PointCloud  
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.estimate_normals()
    
    # Process without visualization
    print(f"Point cloud created with {len(pcd.points)} points")
    
    # Operations that work in Streamlit:
    
    # 1. Get bounding box
    bbox = pcd.get_axis_aligned_bounding_box()
    print(f"Bounding box: min={bbox.min_bound}, max={bbox.max_bound}")
    
    # 2. Statistical analysis
    points_array = np.asarray(pcd.points)
    print(f"Centroid: {points_array.mean(axis=0)}")
    print(f"Std dev: {points_array.std(axis=0)}")
    
    # 3. Downsampling
    pcd_downsampled = pcd.voxel_down_sample(voxel_size=0.1)
    print(f"Downsampled to {len(pcd_downsampled.points)} points")
    
    # 4. Export for web download
    o3d.io.write_point_cloud("example4_processed.ply", pcd_downsampled)
    
    # 5. Convert back to numpy for further processing
    final_points = np.asarray(pcd_downsampled.points)
    final_normals = np.asarray(pcd_downsampled.normals)
    
    print(f"Final matrices: points{final_points.shape}, normals{final_normals.shape}")
    
    return pcd_downsampled, final_points, final_normals


def main():
    """Run all examples."""
    print("🔺 Open3D Matrix Examples")
    print("=" * 50)
    
    # Run examples
    pcd1 = example_1_basic_conversion()
    pcd2 = example_2_with_colors()  
    pcd3 = example_3_from_csv()
    pcd4, points, normals = example_4_streamlit_compatible()
    
    print("\n✅ All examples completed!")
    print("\nFiles created:")
    print("- example1_basic.ply")
    print("- example2_colored.ply") 
    print("- example3_from_csv.ply")
    print("- example4_processed.ply")
    print("- sample_points.csv")
    
    print("\n📝 Key Takeaways:")
    print("1. Open3D needs Nx3 numpy arrays (float64 recommended)")
    print("2. Colors must be in [0,1] range, same shape as points")
    print("3. Use pcd.estimate_normals() for shading")
    print("4. Most Open3D operations work in Streamlit")
    print("5. Use matplotlib for web visualization, PLY export for desktop")
    
    # Optionally visualize (only works in desktop environment)
    try:
        response = input("\nVisualize point clouds? (y/n): ").lower()
        if response == 'y':
            print("Opening visualizations...")
            o3d.visualization.draw_geometries([pcd1], window_name="Example 1: Basic")
            o3d.visualization.draw_geometries([pcd2], window_name="Example 2: Colored")
            o3d.visualization.draw_geometries([pcd3], window_name="Example 3: CSV")
            o3d.visualization.draw_geometries([pcd4], window_name="Example 4: Processed")
    except:
        print("Skipping visualization (not available in this environment)")


if __name__ == "__main__":
    main() 