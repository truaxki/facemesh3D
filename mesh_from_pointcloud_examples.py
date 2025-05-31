import open3d as o3d
import numpy as np

def create_sample_point_cloud():
    """Create a sample point cloud for demonstration"""
    # Create a sphere point cloud for testing
    mesh = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=20)
    pcd = mesh.sample_points_uniformly(number_of_points=1000)
    return pcd

def method1_ball_pivoting(pcd):
    """
    Ball Pivoting Algorithm - Good for smooth surfaces
    Works well when you have a relatively uniform point density
    """
    print("Creating mesh using Ball Pivoting Algorithm...")
    
    # Estimate normals
    pcd.estimate_normals()
    
    # Estimate radius for ball pivoting
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 1.5 * avg_dist
    
    # Create mesh using ball pivoting
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd,
        o3d.utility.DoubleVector([radius, radius * 2])
    )
    
    return mesh

def method2_poisson_reconstruction(pcd):
    """
    Poisson Surface Reconstruction - Good for closed surfaces
    Requires oriented normals, produces smooth, watertight meshes
    """
    print("Creating mesh using Poisson Surface Reconstruction...")
    
    # Estimate normals with consistent orientation
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(100)
    
    # Poisson reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=9
    )
    
    # Optional: Remove low density vertices
    densities = np.asarray(densities)
    density_threshold = np.quantile(densities, 0.01)
    mesh.remove_vertices_by_mask(densities < density_threshold)
    
    return mesh

def method3_alpha_shapes(pcd):
    """
    Alpha Shapes - Good for complex geometries with holes
    Creates non-watertight meshes that follow the point cloud shape closely
    """
    print("Creating mesh using Alpha Shapes...")
    
    # Calculate alpha value (you may need to tune this)
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    alpha = 2.0 * avg_dist
    
    # Create alpha shape
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
        pcd, alpha
    )
    
    return mesh

def method4_delaunay_2d(pcd):
    """
    2D Delaunay Triangulation - For relatively flat surfaces
    Projects points to 2D plane and triangulates
    """
    print("Creating mesh using 2D Delaunay Triangulation...")
    
    # This is a simplified example - you'd need to project to appropriate plane
    points = np.asarray(pcd.points)
    
    # Project to XY plane (assuming Z is roughly constant)
    points_2d = points[:, :2]
    
    # Create 2D triangulation (this is a basic example)
    from scipy.spatial import Delaunay
    tri = Delaunay(points_2d)
    
    # Create mesh
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(points)
    mesh.triangles = o3d.utility.Vector3iVector(tri.simplices)
    mesh.compute_vertex_normals()
    
    return mesh

def visualize_results(original_pcd, meshes, titles):
    """Visualize original point cloud and resulting meshes"""
    
    # Visualize original point cloud
    print("Showing original point cloud...")
    o3d.visualization.draw_geometries([original_pcd], window_name="Original Point Cloud")
    
    # Visualize each mesh
    for mesh, title in zip(meshes, titles):
        print(f"Showing {title}...")
        mesh.compute_vertex_normals()
        mesh.paint_uniform_color([0.7, 0.7, 0.7])
        o3d.visualization.draw_geometries([mesh], window_name=title)

def main():
    """Main function to demonstrate different meshing methods"""
    
    # Create or load your point cloud
    pcd = create_sample_point_cloud()
    
    # You can also load your own point cloud like this:
    # pcd = o3d.io.read_point_cloud("your_pointcloud.ply")
    
    print(f"Point cloud has {len(pcd.points)} points")
    
    # Try different methods
    meshes = []
    titles = []
    
    try:
        mesh1 = method1_ball_pivoting(pcd.copy())
        meshes.append(mesh1)
        titles.append("Ball Pivoting")
        print(f"Ball Pivoting: {len(mesh1.vertices)} vertices, {len(mesh1.triangles)} triangles")
    except Exception as e:
        print(f"Ball Pivoting failed: {e}")
    
    try:
        mesh2 = method2_poisson_reconstruction(pcd.copy())
        meshes.append(mesh2)
        titles.append("Poisson Reconstruction")
        print(f"Poisson: {len(mesh2.vertices)} vertices, {len(mesh2.triangles)} triangles")
    except Exception as e:
        print(f"Poisson failed: {e}")
    
    try:
        mesh3 = method3_alpha_shapes(pcd.copy())
        meshes.append(mesh3)
        titles.append("Alpha Shapes")
        print(f"Alpha Shapes: {len(mesh3.vertices)} vertices, {len(mesh3.triangles)} triangles")
    except Exception as e:
        print(f"Alpha Shapes failed: {e}")
    
    # Visualize results
    visualize_results(pcd, meshes, titles)
    
    # Save meshes
    for i, (mesh, title) in enumerate(zip(meshes, titles)):
        filename = f"mesh_{title.lower().replace(' ', '_')}.ply"
        o3d.io.write_triangle_mesh(filename, mesh)
        print(f"Saved {title} mesh to {filename}")

if __name__ == "__main__":
    main() 