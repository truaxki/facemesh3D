import open3d as o3d
import numpy as np

def create_face_mesh_from_pointcloud(pcd, method="poisson"):
    """
    Create a facial mesh from a point cloud using different methods
    
    Args:
        pcd: Open3D point cloud
        method: "poisson", "ball_pivoting", or "alpha_shapes"
    
    Returns:
        mesh: Open3D triangle mesh
    """
    
    if method == "poisson":
        return create_face_mesh_poisson(pcd)
    elif method == "ball_pivoting":
        return create_face_mesh_ball_pivoting(pcd)
    elif method == "alpha_shapes":
        return create_face_mesh_alpha_shapes(pcd)
    else:
        raise ValueError("Method must be 'poisson', 'ball_pivoting', or 'alpha_shapes'")

def create_face_mesh_poisson(pcd):
    """
    Poisson reconstruction - best for complete facial scans
    Creates smooth, watertight meshes
    """
    print("Creating facial mesh using Poisson reconstruction...")
    
    # Estimate normals - crucial for facial geometry
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    
    # Orient normals consistently (important for faces)
    pcd.orient_normals_consistent_tangent_plane(k=30)
    
    # Poisson reconstruction with parameters tuned for faces
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, 
        depth=10,           # Higher depth for more detail
        width=0,            # Auto-determine width
        scale=1.1,          # Slightly larger bounding box
        linear_fit=False    # Better for organic shapes like faces
    )
    
    # Remove low-density vertices (often artifacts)
    densities = np.asarray(densities)
    density_threshold = np.quantile(densities, 0.02)  # Remove bottom 2%
    mesh.remove_vertices_by_mask(densities < density_threshold)
    
    return mesh

def create_face_mesh_ball_pivoting(pcd):
    """
    Ball pivoting - good for partial facial scans
    Preserves original point cloud structure
    """
    print("Creating facial mesh using Ball Pivoting...")
    
    # Estimate normals
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    
    # Calculate appropriate ball radius for facial features
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    
    # Use multiple radii to capture different scales of facial features
    radii = [avg_dist, avg_dist * 2, avg_dist * 4]
    
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd,
        o3d.utility.DoubleVector(radii)
    )
    
    return mesh

def create_face_mesh_alpha_shapes(pcd):
    """
    Alpha shapes - good for detailed facial features
    Can preserve holes (like nostrils, mouth opening)
    """
    print("Creating facial mesh using Alpha Shapes...")
    
    # Calculate alpha based on point density
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    alpha = 1.5 * avg_dist  # Adjust this value based on your data
    
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
        pcd, alpha
    )
    
    return mesh

def refine_facial_mesh(mesh):
    """
    Post-process the mesh to improve quality for facial analysis
    """
    print("Refining facial mesh...")
    
    # Remove degenerate triangles
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    
    # Smooth the mesh (be careful not to lose facial details)
    mesh = mesh.filter_smooth_simple(number_of_iterations=1)
    
    # Recompute normals
    mesh.compute_vertex_normals()
    
    return mesh

def load_and_process_face_pointcloud(file_path):
    """
    Load a facial point cloud and create a mesh
    
    Args:
        file_path: Path to point cloud file (.ply, .pcd, etc.)
    
    Returns:
        mesh: Processed facial mesh
    """
    
    # Load point cloud
    pcd = o3d.io.read_point_cloud(file_path)
    print(f"Loaded point cloud with {len(pcd.points)} points")
    
    # Optional: downsample if too dense
    if len(pcd.points) > 50000:
        pcd = pcd.voxel_down_sample(voxel_size=0.001)
        print(f"Downsampled to {len(pcd.points)} points")
    
    # Optional: remove outliers
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    print(f"After outlier removal: {len(pcd.points)} points")
    
    # Create mesh using Poisson (usually best for faces)
    mesh = create_face_mesh_from_pointcloud(pcd, method="poisson")
    
    # Refine the mesh
    mesh = refine_facial_mesh(mesh)
    
    print(f"Created mesh with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
    
    return mesh, pcd

def visualize_face_mesh(mesh, pcd=None):
    """
    Visualize the facial mesh and optionally the original point cloud
    """
    geometries = []
    
    # Add mesh
    mesh.paint_uniform_color([0.8, 0.8, 0.8])
    geometries.append(mesh)
    
    # Optionally add original point cloud in different color
    if pcd is not None:
        pcd.paint_uniform_color([1.0, 0.0, 0.0])  # Red points
        geometries.append(pcd)
    
    o3d.visualization.draw_geometries(
        geometries,
        window_name="Facial Mesh",
        mesh_show_wireframe=True,
        mesh_show_back_face=True
    )

def main():
    """
    Example usage for facial mesh creation
    """
    
    # Example 1: Create from a sample point cloud
    print("Creating sample facial-like point cloud...")
    # Create an ellipsoid as a simple face approximation
    mesh_sample = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=20)
    
    # Apply non-uniform scaling to make it face-like
    vertices = np.asarray(mesh_sample.vertices)
    vertices[:, 0] *= 1.0  # X - width
    vertices[:, 1] *= 1.2  # Y - height 
    vertices[:, 2] *= 0.8  # Z - depth
    mesh_sample.vertices = o3d.utility.Vector3dVector(vertices)
    
    pcd_sample = mesh_sample.sample_points_uniformly(number_of_points=5000)
    
    # Create mesh from point cloud
    mesh = create_face_mesh_from_pointcloud(pcd_sample, method="poisson")
    mesh = refine_facial_mesh(mesh)
    
    # Visualize
    visualize_face_mesh(mesh, pcd_sample)
    
    # Save the mesh
    o3d.io.write_triangle_mesh("facial_mesh.ply", mesh)
    print("Saved facial mesh to facial_me