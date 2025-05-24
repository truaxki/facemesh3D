#!/usr/bin/env python3
"""streamlit_open3d_launcher.py

Streamlit Control Panel for Open3D Desktop Viewer
==================================================

This app lets you:
1. Configure point cloud settings in a web interface
2. Preview with matplotlib (basic)
3. Launch the FULL Open3D desktop viewer with your settings
4. Upload files and pass them to the desktop viewer

Best of both worlds: Web UI + Desktop interactivity!

Run: streamlit run source/streamlit_open3d_launcher.py
"""

import streamlit as st
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import subprocess
import tempfile
import os
import json
from pathlib import Path
import pandas as pd
from io import StringIO


class Open3DLauncher:
    """Streamlit app that launches desktop Open3D viewers."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Open3D Desktop Launcher",
            page_icon="🚀",
            layout="wide"
        )
    
    def generate_point_cloud(self, shape_type, num_points, **kwargs):
        """Generate point cloud data based on parameters."""
        
        if shape_type == "Sphere":
            radius = kwargs.get('radius', 1.0)
            phi = np.random.uniform(0, 2*np.pi, num_points)
            costheta = np.random.uniform(-1, 1, num_points)
            u = np.random.uniform(0, 1, num_points)
            
            theta = np.arccos(costheta)
            r = radius * (u ** (1/3))
            
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            points = np.column_stack([x, y, z])
            
            # Color by height
            colors = np.column_stack([
                (z + radius) / (2*radius),
                np.zeros_like(z),
                1 - (z + radius) / (2*radius)
            ])
            
        elif shape_type == "Torus":
            major_r = kwargs.get('major_radius', 1.0)
            minor_r = kwargs.get('minor_radius', 0.3)
            
            u = np.random.uniform(0, 2*np.pi, num_points)
            v = np.random.uniform(0, 2*np.pi, num_points)
            
            x = (major_r + minor_r * np.cos(v)) * np.cos(u)
            y = (major_r + minor_r * np.cos(v)) * np.sin(u)
            z = minor_r * np.sin(v)
            points = np.column_stack([x, y, z])
            
            colors = np.column_stack([
                (np.sin(u) + 1) / 2,
                (np.cos(u) + 1) / 2,
                (np.sin(v) + 1) / 2
            ])
            
        elif shape_type == "Helix":
            turns = kwargs.get('turns', 3)
            height = kwargs.get('height', 2.0)
            radius = kwargs.get('radius', 1.0)
            
            t = np.linspace(0, turns * 2*np.pi, num_points)
            x = radius * np.cos(t)
            y = radius * np.sin(t)
            z = height * t / (turns * 2*np.pi)
            points = np.column_stack([x, y, z])
            
            colors = np.column_stack([
                t / (turns * 2*np.pi),
                0.5 * np.ones_like(t),
                1 - t / (turns * 2*np.pi)
            ])
            
        elif shape_type == "Cube":
            side = kwargs.get('side_length', 2.0)
            points = np.random.uniform(-side/2, side/2, (num_points, 3))
            
            # Color by distance from center
            dist = np.linalg.norm(points, axis=1)
            max_dist = np.max(dist)
            colors = np.column_stack([
                dist / max_dist,
                0.5 * np.ones_like(dist),
                1 - dist / max_dist
            ])
        
        else:  # Random
            points = np.random.randn(num_points, 3)
            colors = np.random.rand(num_points, 3)
        
        return points, colors
    
    def save_config_and_data(self, points, colors, config):
        """Save point cloud data and config for desktop viewer."""
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="open3d_")
        
        # Save point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
        if colors is not None:
            pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
        pcd.estimate_normals()
        
        ply_path = os.path.join(temp_dir, "pointcloud.ply")
        o3d.io.write_point_cloud(ply_path, pcd)
        
        # Save config
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        return ply_path, config_path, temp_dir
    
    def launch_desktop_viewer(self, ply_path, config):
        """Launch the desktop Open3D viewer with specified parameters."""
        try:
            # Get current working directory for the script
            script_path = Path(__file__).parent / "open3d_desktop_viewer.py"
            
            # Build command
            cmd = [
                "python", str(script_path),
                "--file", ply_path,
                "--points", str(config.get('num_points', 1000))
            ]
            
            # Launch in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux/Mac
                subprocess.Popen(cmd)
            
            return True
        except Exception as e:
            st.error(f"Failed to launch desktop viewer: {str(e)}")
            return False
    
    def preview_plot(self, points, colors=None):
        """Create matplotlib preview plot."""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if colors is not None:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=1, alpha=0.7)
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Preview ({len(points)} points)\n👆 This is the LIMITED matplotlib view')
        
        # Equal aspect ratio
        max_range = np.max(np.ptp(points, axis=0)) / 2
        mid = np.mean(points, axis=0)
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        st.pyplot(fig)
        plt.close()
    
    def load_uploaded_file(self, uploaded_file):
        """Load point cloud from uploaded file."""
        try:
            if uploaded_file.name.endswith('.csv'):
                content = StringIO(uploaded_file.getvalue().decode('utf-8'))
                df = pd.read_csv(content)
                
                if len(df.columns) < 3:
                    st.error("CSV must have at least 3 columns (X, Y, Z)")
                    return None, None
                
                points = df.iloc[:, :3].values
                colors = None
                if len(df.columns) >= 6:
                    colors = df.iloc[:, 3:6].values
                    if np.max(colors) > 1:
                        colors = colors / 255.0
                
                return points, colors
            
            elif uploaded_file.name.endswith(('.ply', '.pcd', '.xyz')):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp.flush()
                    pcd = o3d.io.read_point_cloud(tmp.name)
                    os.unlink(tmp.name)
                    
                    points = np.asarray(pcd.points)
                    colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
                    return points, colors
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None, None
    
    def run(self):
        """Main Streamlit app."""
        st.title("🚀 Open3D Desktop Launcher")
        st.markdown("""
        **Control Panel for Interactive Point Cloud Visualization**
        
        Configure your point cloud here, then launch the **full interactive** Open3D desktop viewer!
        """)
        
        # Sidebar configuration
        with st.sidebar:
            st.header("🎛️ Configuration")
            
            # Data source
            data_source = st.selectbox(
                "Data Source",
                ["Generate", "Upload File"]
            )
            
            if data_source == "Generate":
                st.subheader("📊 Generation Settings")
                
                shape_type = st.selectbox(
                    "Shape Type",
                    ["Sphere", "Torus", "Helix", "Cube", "Random"]
                )
                
                num_points = st.slider("Number of Points", 100, 10000, 2000)
                
                # Shape-specific parameters
                shape_params = {}
                if shape_type == "Sphere":
                    shape_params['radius'] = st.slider("Radius", 0.5, 3.0, 1.0)
                elif shape_type == "Torus":
                    shape_params['major_radius'] = st.slider("Major Radius", 0.5, 2.0, 1.0)
                    shape_params['minor_radius'] = st.slider("Minor Radius", 0.1, 0.8, 0.3)
                elif shape_type == "Helix":
                    shape_params['turns'] = st.slider("Number of Turns", 1, 8, 3)
                    shape_params['height'] = st.slider("Height", 1.0, 5.0, 2.0)
                    shape_params['radius'] = st.slider("Radius", 0.5, 2.0, 1.0)
                elif shape_type == "Cube":
                    shape_params['side_length'] = st.slider("Side Length", 1.0, 4.0, 2.0)
                
                # Generate button
                if st.button("🎲 Generate Point Cloud", type="primary"):
                    points, colors = self.generate_point_cloud(shape_type, num_points, **shape_params)
                    st.session_state.points = points
                    st.session_state.colors = colors
                    st.session_state.config = {
                        'shape_type': shape_type,
                        'num_points': num_points,
                        **shape_params
                    }
                    st.success(f"Generated {len(points)} points!")
            
            else:  # Upload File
                st.subheader("📁 File Upload")
                uploaded_file = st.file_uploader(
                    "Choose file",
                    type=['csv', 'ply', 'pcd', 'xyz'],
                    help="CSV: X,Y,Z,R,G,B columns. PLY/PCD/XYZ: Standard formats"
                )
                
                if uploaded_file is not None:
                    points, colors = self.load_uploaded_file(uploaded_file)
                    if points is not None:
                        st.session_state.points = points
                        st.session_state.colors = colors
                        st.session_state.config = {
                            'source': 'uploaded',
                            'filename': uploaded_file.name,
                            'num_points': len(points)
                        }
                        st.success(f"Loaded {len(points)} points from {uploaded_file.name}")
        
        # Main content
        if 'points' in st.session_state:
            points = st.session_state.points
            colors = st.session_state.colors
            config = st.session_state.config
            
            # Two columns: preview and launch
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("👁️ Web Preview (Limited)")
                st.caption("Basic matplotlib preview - the desktop viewer will be MUCH better!")
                self.preview_plot(points, colors)
            
            with col2:
                st.subheader("🚀 Launch Desktop Viewer")
                
                # Info about the data
                st.metric("Points", len(points))
                st.metric("Has Colors", "Yes" if colors is not None else "No")
                
                # Big launch button
                if st.button("🎮 Launch Interactive Desktop Viewer", type="primary", use_container_width=True):
                    with st.spinner("Preparing desktop viewer..."):
                        # Save data temporarily
                        ply_path, config_path, temp_dir = self.save_config_and_data(points, colors, config)
                        
                        # Launch viewer
                        success = self.launch_desktop_viewer(ply_path, config)
                        
                        if success:
                            st.success("🎉 Desktop viewer launched!")
                            st.info(f"""
                            **Desktop viewer is now running!**
                            
                            Try these in the Open3D window:
                            - **Mouse drag**: Smooth rotation
                            - **Right drag**: Pan view
                            - **Scroll**: Zoom in/out
                            - **Terminal commands**: Background, screenshots
                            
                            Data saved to: `{ply_path}`
                            """)
                        else:
                            st.error("Failed to launch desktop viewer")
                
                # Alternative: Download for manual viewing
                st.subheader("💾 Manual Download")
                if st.button("📥 Download PLY File"):
                    ply_path, _, _ = self.save_config_and_data(points, colors, config)
                    with open(ply_path, "rb") as f:
                        st.download_button(
                            "Download Point Cloud",
                            f.read(),
                            file_name="pointcloud.ply",
                            mime="application/octet-stream"
                        )
                
                # Instructions
                st.subheader("📋 Manual Launch")
                st.code("""
# If auto-launch fails, run manually:
python source/open3d_desktop_viewer.py --file pointcloud.ply
                """)
        
        else:
            # Instructions when no data loaded
            st.info("👈 Configure your point cloud in the sidebar to get started!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🌐 Web Interface (This)")
                st.markdown("""
                ✅ Easy configuration  
                ✅ File uploads  
                ✅ Parameter tweaking  
                ❌ Limited interactivity  
                ❌ Slow matplotlib 3D  
                """)
            
            with col2:
                st.subheader("🖥️ Desktop Viewer")
                st.markdown("""
                ✅ **Smooth real-time rotation**  
                ✅ **Professional lighting**  
                ✅ **High-quality rendering**  
                ✅ **Screenshot capture**  
                ✅ **Multiple viewing modes**  
                """)
            
            st.markdown("---")
            st.subheader("🎯 Workflow")
            st.markdown("""
            1. **Configure** your point cloud using this web interface
            2. **Preview** with basic matplotlib (optional)
            3. **Launch** the desktop viewer for full interactivity
            4. **Explore** your data with professional 3D tools!
            """)


def main():
    """Entry point."""
    app = Open3DLauncher()
    app.run()


if __name__ == "__main__":
    main() 