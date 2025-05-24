#!/usr/bin/env python3
"""streamlit_open3d_launcher.py

Streamlit Control Panel for Open3D Desktop Viewer
==================================================

This app lets you:
1. Configure point cloud settings in a web interface
2. Preview with matplotlib (basic)
3. Launch the FULL Open3D desktop viewer with your settings
4. Upload files and pass them to the desktop viewer
5. CREATE ANIMATIONS from folders of PLY files! 🎬

Best of both worlds: Web UI + Desktop interactivity + Animation!

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
import time
import glob
import cv2


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
        # Create temp directory with timestamp to avoid conflicts
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        temp_dir = tempfile.mkdtemp(prefix=f"open3d_{timestamp}_")
        
        try:
            # Save point cloud
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
            if colors is not None:
                pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
            pcd.estimate_normals()
            
            ply_path = os.path.join(temp_dir, f"pointcloud_{timestamp}.ply")
            success = o3d.io.write_point_cloud(ply_path, pcd)
            
            if not success:
                raise RuntimeError("Failed to write PLY file")
            
            # Save config
            config_path = os.path.join(temp_dir, f"config_{timestamp}.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            return ply_path, config_path, temp_dir
            
        except Exception as e:
            # Clean up on error
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
            raise e
    
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
                # Create temp file with proper Windows handling
                temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(uploaded_file.name)[1])
                try:
                    # Write data to temp file
                    with os.fdopen(temp_fd, 'wb') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file.flush()
                        os.fsync(tmp_file.fileno())  # Force write to disk
                    
                    # Now read with Open3D (file is properly closed)
                    pcd = o3d.io.read_point_cloud(temp_path)
                    
                    # Extract data
                    points = np.asarray(pcd.points)
                    colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
                    
                    return points, colors
                    
                finally:
                    # Clean up temp file
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except (OSError, PermissionError) as e:
                        # Log warning but don't fail - temp files will be cleaned up by OS
                        st.warning(f"Could not clean up temporary file: {e}")
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None, None
    
    def load_ply_folder(self, folder_path):
        """Load all PLY files from a folder in alphabetical order."""
        try:
            ply_files = sorted(glob.glob(os.path.join(folder_path, "*.ply")))
            
            if not ply_files:
                st.error(f"No PLY files found in {folder_path}")
                return None
            
            frames_data = []
            
            # Progress bar for loading
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ply_file in enumerate(ply_files):
                status_text.text(f"Loading frame {i+1}/{len(ply_files)}: {os.path.basename(ply_file)}")
                
                try:
                    pcd = o3d.io.read_point_cloud(ply_file)
                    points = np.asarray(pcd.points)
                    colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
                    
                    frames_data.append({
                        'points': points,
                        'colors': colors,
                        'filename': os.path.basename(ply_file)
                    })
                    
                except Exception as e:
                    st.warning(f"Could not load {ply_file}: {e}")
                    continue
                
                progress_bar.progress((i + 1) / len(ply_files))
            
            progress_bar.empty()
            status_text.empty()
            
            if frames_data:
                st.success(f"✅ Loaded {len(frames_data)} frames from {len(ply_files)} PLY files")
                return frames_data
            else:
                st.error("No valid PLY files could be loaded")
                return None
                
        except Exception as e:
            st.error(f"Error loading folder: {e}")
            return None
    
    def create_animation_preview(self, frames_data, fps=5):
        """Create animated preview using matplotlib."""
        if not frames_data:
            return
        
        st.subheader("🎬 Animation Preview")
        
        # Animation controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            frame_idx = st.slider("Frame", 0, len(frames_data)-1, 0)
        with col2:
            auto_play = st.checkbox("Auto Play")
        with col3:
            if st.button("🎥 Export Video"):
                self.export_animation_video(frames_data, fps)
        
        # Display current frame
        current_frame = frames_data[frame_idx]
        points = current_frame['points']
        colors = current_frame['colors']
        filename = current_frame['filename']
        
        fig = plt.figure(figsize=(12, 8))
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
        ax.set_title(f'Frame {frame_idx+1}/{len(frames_data)}: {filename}\n🎬 Animation Preview ({len(points)} points)')
        
        # Equal aspect ratio
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2
        mid = np.mean(all_points, axis=0)
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        st.pyplot(fig)
        plt.close()
        
        # Auto-play functionality
        if auto_play:
            if 'animation_frame' not in st.session_state:
                st.session_state.animation_frame = 0
            
            st.session_state.animation_frame = (st.session_state.animation_frame + 1) % len(frames_data)
            time.sleep(1.0 / fps)
            st.rerun()
    
    def export_animation_video(self, frames_data, fps=5):
        """Export animation as MP4 video."""
        try:
            with st.spinner("Creating animation video..."):
                # Create temp directory for frames
                temp_dir = tempfile.mkdtemp(prefix="animation_")
                
                # Generate frame images
                frame_paths = []
                for i, frame_data in enumerate(frames_data):
                    points = frame_data['points']
                    colors = frame_data['colors']
                    
                    fig = plt.figure(figsize=(10, 8), facecolor='black')
                    ax = fig.add_subplot(111, projection='3d', facecolor='black')
                    
                    if colors is not None:
                        ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                                  c=colors, s=2, alpha=0.8)
                    else:
                        ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                                  c=points[:, 2], cmap='viridis', s=2, alpha=0.8)
                    
                    ax.set_xlabel('X', color='white')
                    ax.set_ylabel('Y', color='white')
                    ax.set_zlabel('Z', color='white')
                    ax.tick_params(colors='white')
                    
                    # Equal aspect ratio
                    all_points = np.vstack([f['points'] for f in frames_data])
                    max_range = np.max(np.ptp(all_points, axis=0)) / 2
                    mid = np.mean(all_points, axis=0)
                    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
                    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
                    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
                    
                    frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                    plt.savefig(frame_path, dpi=100, bbox_inches='tight', facecolor='black')
                    plt.close()
                    
                    frame_paths.append(frame_path)
                
                # Create video using OpenCV
                video_path = os.path.join(temp_dir, "animation.mp4")
                frame = cv2.imread(frame_paths[0])
                height, width, layers = frame.shape
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
                
                for frame_path in frame_paths:
                    frame = cv2.imread(frame_path)
                    video.write(frame)
                
                video.release()
                
                # Offer download
                with open(video_path, "rb") as f:
                    st.download_button(
                        "📥 Download Animation Video",
                        f.read(),
                        file_name="pointcloud_animation.mp4",
                        mime="video/mp4"
                    )
                
                st.success(f"✅ Video created with {len(frames_data)} frames at {fps} FPS!")
                
        except Exception as e:
            st.error(f"Error creating video: {e}")
    
    def save_animation_data(self, frames_data):
        """Save all frames for animated desktop viewer."""
        timestamp = int(time.time() * 1000)
        temp_dir = tempfile.mkdtemp(prefix=f"animation_{timestamp}_")
        
        try:
            ply_paths = []
            
            for i, frame_data in enumerate(frames_data):
                points = frame_data['points']
                colors = frame_data['colors']
                
                # Create point cloud
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
                if colors is not None:
                    pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
                pcd.estimate_normals()
                
                # Save frame
                ply_path = os.path.join(temp_dir, f"frame_{i:04d}.ply")
                o3d.io.write_point_cloud(ply_path, pcd)
                ply_paths.append(ply_path)
            
            # Save animation config
            config = {
                'type': 'animation',
                'num_frames': len(frames_data),
                'frame_paths': ply_paths,
                'fps': 10
            }
            
            config_path = os.path.join(temp_dir, "animation_config.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            return temp_dir, config_path, ply_paths
            
        except Exception as e:
            # Clean up on error
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
            raise e
    
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
                ["Generate", "Upload File", "🎬 Animation Folder"]
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
            
            elif data_source == "Upload File":
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
            
            else:  # Animation Folder
                st.subheader("🎬 Animation Folder")
                st.markdown("""
                **Load a folder of PLY files for animation!**
                
                🔍 **Requirements:**
                - All files must be `.ply` format
                - Files will be loaded in alphabetical order
                - Each PLY file = one animation frame
                """)
                
                folder_path = st.text_input(
                    "Folder Path",
                    value="",
                    help="Enter the full path to your folder containing PLY files",
                    placeholder="C:/path/to/your/ply/files/"
                )
                
                if st.button("🎬 Load Animation Frames", type="primary"):
                    if folder_path and os.path.exists(folder_path):
                        frames_data = self.load_ply_folder(folder_path)
                        if frames_data:
                            st.session_state.frames_data = frames_data
                            st.session_state.config = {
                                'source': 'animation',
                                'folder_path': folder_path,
                                'num_frames': len(frames_data)
                            }
                    else:
                        st.error("Please enter a valid folder path")
                
                # Animation settings
                if 'frames_data' in st.session_state:
                    st.subheader("⚙️ Animation Settings")
                    fps = st.slider("FPS (Frames Per Second)", 1, 30, 10)
                    st.session_state.animation_fps = fps
        
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
        
        elif 'frames_data' in st.session_state:
            # Animation mode
            frames_data = st.session_state.frames_data
            config = st.session_state.config
            fps = st.session_state.get('animation_fps', 10)
            
            # Animation preview and controls
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self.create_animation_preview(frames_data, fps)
            
            with col2:
                st.subheader("🎬 Animation Controls")
                
                # Info about the animation
                st.metric("Total Frames", len(frames_data))
                st.metric("FPS", fps)
                
                # Animation actions
                if st.button("🎮 Launch Animated Desktop Viewer", type="primary", use_container_width=True):
                    with st.spinner("Preparing animated viewer..."):
                        try:
                            temp_dir, config_path, ply_paths = self.save_animation_data(frames_data)
                            
                            # Launch animated viewer (enhanced desktop viewer)
                            script_path = Path(__file__).parent / "open3d_desktop_viewer.py"
                            cmd = [
                                "python", str(script_path),
                                "--animation", config_path,
                                "--fps", str(fps)
                            ]
                            
                            if os.name == 'nt':  # Windows
                                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                            else:  # Unix/Linux/Mac
                                subprocess.Popen(cmd)
                            
                            st.success("🎉 Animated desktop viewer launched!")
                            st.info(f"""
                            **Animated viewer is now running!**
                            
                            🎬 **Animation Controls:**
                            - **Spacebar**: Play/Pause animation
                            - **Arrow Keys**: Next/Previous frame
                            - **R**: Reset to first frame
                            - **Mouse**: Rotate view while animating
                            
                            **{len(frames_data)} frames** loaded at **{fps} FPS**
                            """)
                            
                        except Exception as e:
                            st.error(f"Failed to launch animated viewer: {e}")
                
                # Video export
                st.subheader("🎥 Export Video")
                if st.button("📹 Create MP4 Video", use_container_width=True):
                    self.export_animation_video(frames_data, fps)
                
                # Frame download
                st.subheader("💾 Download Frames")
                if st.button("📥 Download All PLY Frames"):
                    with st.spinner("Preparing frame archive..."):
                        try:
                            temp_dir, _, ply_paths = self.save_animation_data(frames_data)
                            
                            # Create ZIP archive
                            import zipfile
                            zip_path = os.path.join(temp_dir, "animation_frames.zip")
                            
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for i, ply_path in enumerate(ply_paths):
                                    arcname = f"frame_{i:04d}.ply"
                                    zipf.write(ply_path, arcname)
                            
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    "Download Frame Archive",
                                    f.read(),
                                    file_name="animation_frames.zip",
                                    mime="application/zip"
                                )
                            
                        except Exception as e:
                            st.error(f"Failed to create archive: {e}")
                
                # Instructions
                st.subheader("📋 Manual Launch")
                st.code(f"""
# Manual animation playback:
python source/open3d_desktop_viewer.py --animation [config_path] --fps {fps}
                """)
        
        else:
            # Instructions when no data loaded
            st.info("👈 Configure your point cloud in the sidebar to get started!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🌐 Web Interface")
                st.markdown("""
                ✅ Easy configuration  
                ✅ File uploads  
                ✅ Parameter tweaking  
                ❌ Limited interactivity  
                """)
            
            with col2:
                st.subheader("🖥️ Desktop Viewer")
                st.markdown("""
                ✅ **Smooth rotation**  
                ✅ **Professional lighting**  
                ✅ **High-quality rendering**  
                ✅ **Screenshot capture**  
                """)
            
            with col3:
                st.subheader("🎬 Animation")
                st.markdown("""
                ✅ **Folder loading**  
                ✅ **Frame sequencing**  
                ✅ **Video export**  
                ✅ **Animated playback**  
                """)
            
            st.markdown("---")
            st.subheader("🎯 Workflow Options")
            
            # Create tabs for different workflows
            tab1, tab2, tab3 = st.tabs(["Single Point Cloud", "Animation", "Advanced"])
            
            with tab1:
                st.markdown("""
                **Single Point Cloud Workflow:**
                1. **Generate** or **Upload** a point cloud
                2. **Preview** with matplotlib in browser
                3. **Launch** desktop viewer for full interactivity
                4. **Export** or **screenshot** your visualization
                """)
            
            with tab2:
                st.markdown("""
                **Animation Workflow:**
                1. **Prepare** a folder of PLY files (frame_001.ply, frame_002.ply, etc.)
                2. **Load Animation Folder** in sidebar
                3. **Preview** animation with frame slider
                4. **Export MP4 video** or **Launch animated viewer**
                5. **Control playback** with spacebar and arrow keys
                """)
            
            with tab3:
                st.markdown("""
                **Advanced Features:**
                - **Custom FPS**: Adjust animation speed
                - **Batch Processing**: Load hundreds of frames
                - **Video Export**: High-quality MP4 output
                - **Interactive Animation**: Real-time playback with Open3D
                - **Frame Navigation**: Manual frame-by-frame control
                """)


def main():
    """Entry point."""
    app = Open3DLauncher()
    app.run()


if __name__ == "__main__":
    main() 