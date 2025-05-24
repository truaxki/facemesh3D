#!/usr/bin/env python3
"""open3d_streamlit_demo.py

Comprehensive demo showing how to:
1. Convert Nx3 matrices to Open3D point clouds
2. Integrate Open3D with Streamlit for web visualization
3. Load different data formats (numpy, CSV, PLY)
4. Add colors, normals, and other properties

Run with: streamlit run source/open3d_streamlit_demo.py
"""

import streamlit as st
import numpy as np
import open3d as o3d
import pandas as pd
import tempfile
import os
from io import StringIO
from typing import Optional, Tuple, Union


class Open3DStreamlitDemo:
    """Demo app for Open3D + Streamlit integration."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Open3D + Streamlit Demo",
            page_icon="🔺",
            layout="wide"
        )
    
    def create_point_cloud_from_matrix(
        self, 
        points: np.ndarray, 
        colors: Optional[np.ndarray] = None,
        normals: Optional[np.ndarray] = None
    ) -> o3d.geometry.PointCloud:
        """
        Convert Nx3 matrix to Open3D PointCloud.
        
        Parameters:
        -----------
        points : np.ndarray, shape (N, 3)
            XYZ coordinates
        colors : np.ndarray, shape (N, 3), optional
            RGB colors (0-1 range)
        normals : np.ndarray, shape (N, 3), optional
            Normal vectors
        """
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("Points must be Nx3 array")
        
        # Create Open3D point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
        
        # Add colors if provided
        if colors is not None:
            if colors.shape != points.shape:
                raise ValueError("Colors must have same shape as points")
            # Ensure colors are in 0-1 range
            colors = np.clip(colors, 0, 1)
            pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
        
        # Add normals if provided
        if normals is not None:
            if normals.shape != points.shape:
                raise ValueError("Normals must have same shape as points")
            pcd.normals = o3d.utility.Vector3dVector(normals.astype(np.float64))
        else:
            # Estimate normals automatically
            pcd.estimate_normals()
        
        return pcd
    
    def generate_sample_data(self, data_type: str, num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate different types of sample point clouds."""
        
        if data_type == "Random Sphere":
            # Uniform distribution in sphere
            phi = np.random.uniform(0, 2*np.pi, num_points)
            costheta = np.random.uniform(-1, 1, num_points)
            u = np.random.uniform(0, 1, num_points)
            
            theta = np.arccos(costheta)
            r = u ** (1/3)  # Uniform in volume
            
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            points = np.column_stack([x, y, z])
            
            # Color by Z coordinate
            colors = np.column_stack([
                (z + 1) / 2,  # Red: Z coordinate normalized
                np.zeros_like(z),  # Green: 0
                1 - (z + 1) / 2   # Blue: inverse Z
            ])
            
        elif data_type == "Torus":
            # Torus (donut shape)
            R = 1.0  # Major radius
            r = 0.3  # Minor radius
            
            u = np.random.uniform(0, 2*np.pi, num_points)
            v = np.random.uniform(0, 2*np.pi, num_points)
            
            x = (R + r * np.cos(v)) * np.cos(u)
            y = (R + r * np.cos(v)) * np.sin(u)
            z = r * np.sin(v)
            points = np.column_stack([x, y, z])
            
            # Rainbow colors based on angle
            colors = np.column_stack([
                (np.sin(u) + 1) / 2,
                (np.cos(u) + 1) / 2,
                (np.sin(v) + 1) / 2
            ])
            
        elif data_type == "Helix":
            # Spiral helix
            t = np.linspace(0, 4*np.pi, num_points)
            x = np.cos(t)
            y = np.sin(t)
            z = t / (2*np.pi)
            points = np.column_stack([x, y, z])
            
            # Color by height
            colors = np.column_stack([
                t / (4*np.pi),  # Red increases with height
                np.ones_like(t) * 0.5,  # Green constant
                1 - t / (4*np.pi)  # Blue decreases with height
            ])
            
        elif data_type == "Bunny Surface":
            # Simple bunny-like surface (simplified)
            u = np.random.uniform(-np.pi, np.pi, num_points)
            v = np.random.uniform(-np.pi/2, np.pi/2, num_points)
            
            x = np.cos(v) * np.cos(u)
            y = np.cos(v) * np.sin(u) 
            z = np.sin(v) + 0.3 * np.sin(3*u) * np.cos(v)  # Add some features
            points = np.column_stack([x, y, z])
            
            # Pastel colors
            colors = np.column_stack([
                0.8 + 0.2 * np.random.random(num_points),
                0.6 + 0.2 * np.random.random(num_points),
                0.9 + 0.1 * np.random.random(num_points)
            ])
        
        else:  # Cube
            points = np.random.uniform(-1, 1, (num_points, 3))
            # Color by distance from center
            dist = np.linalg.norm(points, axis=1)
            colors = np.column_stack([
                dist / np.max(dist),
                0.5 * np.ones_like(dist),
                1 - dist / np.max(dist)
            ])
        
        return points, colors
    
    def save_point_cloud_temp(self, pcd: o3d.geometry.PointCloud, format: str = "ply") -> str:
        """Save point cloud to temporary file for download."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
            if format == "ply":
                o3d.io.write_point_cloud(tmp.name, pcd)
            elif format == "xyz":
                # Save as simple XYZ text file
                points = np.asarray(pcd.points)
                np.savetxt(tmp.name, points, delimiter=" ", fmt="%.6f")
            return tmp.name
    
    def load_from_uploaded_file(self, uploaded_file) -> Optional[o3d.geometry.PointCloud]:
        """Load point cloud from uploaded file."""
        try:
            if uploaded_file.name.endswith('.csv'):
                # Read CSV
                content = StringIO(uploaded_file.getvalue().decode('utf-8'))
                df = pd.read_csv(content)
                
                # Expect at least X, Y, Z columns
                if len(df.columns) < 3:
                    st.error("CSV must have at least 3 columns (X, Y, Z)")
                    return None
                
                points = df.iloc[:, :3].values
                colors = None
                if len(df.columns) >= 6:  # Has RGB columns
                    colors = df.iloc[:, 3:6].values
                    # Normalize if values > 1 (assuming 0-255 range)
                    if np.max(colors) > 1:
                        colors = colors / 255.0
                
                return self.create_point_cloud_from_matrix(points, colors)
            
            elif uploaded_file.name.endswith(('.ply', '.pcd', '.xyz')):
                # Save to temp file and load with Open3D
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp.flush()
                    pcd = o3d.io.read_point_cloud(tmp.name)
                    os.unlink(tmp.name)
                    return pcd
            
            else:
                st.error("Unsupported file format. Use CSV, PLY, PCD, or XYZ.")
                return None
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    
    def render_3d_plot(self, pcd: o3d.geometry.PointCloud):
        """Render 3D plot using matplotlib (Streamlit compatible)."""
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if colors is not None:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=1, alpha=0.6)
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=points[:, 2], cmap='viridis', s=1, alpha=0.6)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Point Cloud ({len(points)} points)')
        
        # Equal aspect ratio
        max_range = np.max(np.ptp(points, axis=0)) / 2
        mid = np.mean(points, axis=0)
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        st.pyplot(fig)
        plt.close()
    
    def run(self):
        """Main app logic."""
        st.title("🔺 Open3D + Streamlit Integration Demo")
        st.markdown("Learn how to work with Nx3 matrices and Open3D in Streamlit!")
        
        # Sidebar options
        st.sidebar.header("Options")
        
        # Data source selection
        data_source = st.sidebar.selectbox(
            "Data Source",
            ["Generate Sample", "Upload File", "Manual Input"]
        )
        
        pcd = None
        
        if data_source == "Generate Sample":
            # Sample data generation
            st.sidebar.subheader("Sample Data")
            sample_type = st.sidebar.selectbox(
                "Sample Type",
                ["Random Sphere", "Torus", "Helix", "Bunny Surface", "Cube"]
            )
            num_points = st.sidebar.slider("Number of Points", 100, 5000, 1000)
            
            if st.sidebar.button("Generate"):
                with st.spinner("Generating point cloud..."):
                    points, colors = self.generate_sample_data(sample_type, num_points)
                    pcd = self.create_point_cloud_from_matrix(points, colors)
                    st.session_state.pcd = pcd
                    st.session_state.points_matrix = points
                    st.session_state.colors_matrix = colors
        
        elif data_source == "Upload File":
            # File upload
            st.sidebar.subheader("Upload File")
            uploaded_file = st.sidebar.file_uploader(
                "Choose file",
                type=['csv', 'ply', 'pcd', 'xyz'],
                help="CSV: X,Y,Z columns (optionally R,G,B). PLY/PCD/XYZ: Standard formats"
            )
            
            if uploaded_file is not None:
                pcd = self.load_from_uploaded_file(uploaded_file)
                if pcd is not None:
                    st.session_state.pcd = pcd
                    st.session_state.points_matrix = np.asarray(pcd.points)
                    st.session_state.colors_matrix = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
        
        elif data_source == "Manual Input":
            # Manual matrix input
            st.sidebar.subheader("Manual Input")
            st.sidebar.markdown("Enter points as: x1,y1,z1\\nx2,y2,z2\\n...")
            
            points_text = st.sidebar.text_area(
                "Points (CSV format)",
                value="0,0,0\n1,0,0\n0,1,0\n0,0,1",
                height=100
            )
            
            if st.sidebar.button("Parse Points"):
                try:
                    lines = [line.strip() for line in points_text.split('\n') if line.strip()]
                    points = []
                    for line in lines:
                        coords = [float(x.strip()) for x in line.split(',')]
                        if len(coords) >= 3:
                            points.append(coords[:3])
                    
                    if points:
                        points = np.array(points)
                        pcd = self.create_point_cloud_from_matrix(points)
                        st.session_state.pcd = pcd
                        st.session_state.points_matrix = points
                        st.session_state.colors_matrix = None
                    else:
                        st.error("No valid points found")
                except Exception as e:
                    st.error(f"Error parsing points: {str(e)}")
        
        # Display results
        if 'pcd' in st.session_state:
            pcd = st.session_state.pcd
            points = st.session_state.points_matrix
            colors = st.session_state.colors_matrix
            
            # Main content tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Info", "🎨 3D Plot", "📋 Matrix View", "💾 Export"])
            
            with tab1:
                st.subheader("Point Cloud Information")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Number of Points", len(points))
                with col2:
                    st.metric("Has Colors", "Yes" if colors is not None else "No")
                with col3:
                    st.metric("Has Normals", "Yes" if len(pcd.normals) > 0 else "No")
                
                # Statistics
                st.subheader("Statistics")
                stats_df = pd.DataFrame({
                    'Axis': ['X', 'Y', 'Z'],
                    'Min': [points[:, i].min() for i in range(3)],
                    'Max': [points[:, i].max() for i in range(3)],
                    'Mean': [points[:, i].mean() for i in range(3)],
                    'Std': [points[:, i].std() for i in range(3)]
                })
                st.dataframe(stats_df, use_container_width=True)
            
            with tab2:
                st.subheader("3D Visualization")
                self.render_3d_plot(pcd)
                
                # Show matrix -> Open3D conversion code
                st.subheader("Code Example")
                st.code("""
# Convert Nx3 matrix to Open3D PointCloud
import open3d as o3d
import numpy as np

# Your data (Nx3 matrix)
points = np.array([[x1,y1,z1], [x2,y2,z2], ...])  # Shape: (N, 3)
colors = np.array([[r1,g1,b1], [r2,g2,b2], ...])  # Shape: (N, 3), optional

# Create Open3D point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))

# Add colors (0-1 range)
if colors is not None:
    pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))

# Estimate normals
pcd.estimate_normals()

# Visualize (desktop only)
o3d.visualization.draw_geometries([pcd])
                """, language='python')
            
            with tab3:
                st.subheader("Raw Data Matrices")
                
                # Points matrix
                st.write("**Points Matrix (Nx3):**")
                st.dataframe(
                    pd.DataFrame(points, columns=['X', 'Y', 'Z']).head(100),
                    use_container_width=True
                )
                
                # Colors matrix
                if colors is not None:
                    st.write("**Colors Matrix (Nx3):**")
                    st.dataframe(
                        pd.DataFrame(colors, columns=['R', 'G', 'B']).head(100),
                        use_container_width=True
                    )
            
            with tab4:
                st.subheader("Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Download as PLY"):
                        temp_file = self.save_point_cloud_temp(pcd, "ply")
                        with open(temp_file, "rb") as f:
                            st.download_button(
                                "Download PLY file",
                                f.read(),
                                file_name="pointcloud.ply",
                                mime="application/octet-stream"
                            )
                        os.unlink(temp_file)
                
                with col2:
                    if st.button("Download as XYZ"):
                        temp_file = self.save_point_cloud_temp(pcd, "xyz")
                        with open(temp_file, "r") as f:
                            st.download_button(
                                "Download XYZ file",
                                f.read(),
                                file_name="pointcloud.xyz",
                                mime="text/plain"
                            )
                        os.unlink(temp_file)
        
        else:
            # Instructions
            st.info("👆 Select a data source from the sidebar to get started!")
            
            st.subheader("Key Points about Nx3 Matrices & Open3D")
            st.markdown("""
            ### Data Format Requirements:
            - **Points**: Nx3 numpy array (float64 recommended)
            - **Colors**: Nx3 numpy array, values in [0,1] range
            - **Normals**: Nx3 numpy array, unit vectors
            
            ### Open3D + Streamlit Compatibility:
            ✅ **Works**: Data processing, file I/O, mesh operations  
            ✅ **Works**: matplotlib visualization (shown above)  
            ❌ **Doesn't work**: `o3d.visualization.draw_geometries()` (requires GUI)  
            
            ### Recommended Workflow:
            1. Process your Nx3 data with Open3D
            2. Use matplotlib for web visualization
            3. Export results for desktop viewing with Open3D
            """)


def main():
    """Entry point."""
    app = Open3DStreamlitDemo()
    app.run()


if __name__ == "__main__":
    main() 