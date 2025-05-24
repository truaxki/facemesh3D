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
        ax.set_title(f'Preview ({len(points)} points)\nThis is the LIMITED matplotlib view')
        
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
        """Create animated preview using matplotlib - controls moved to sidebar."""
        if not frames_data:
            return
        
        # This method is no longer used since controls moved to sidebar
        # Keeping for compatibility but functionality moved to main animation section
        pass
    
    def export_animation_video(self, frames_data, fps=5):
        """Export animation as MP4 video with prominent progress tracking."""
        try:
            # Initialize status
            st.session_state.video_export_complete = False
            st.session_state.video_export_status = "Initializing export..."
            
            # Create temp directory for frames
            temp_dir = tempfile.mkdtemp(prefix="animation_")
            
            # Update status
            st.session_state.video_export_status = f"Preparing to render {len(frames_data)} frames..."
            
            # Generate frame images with progress tracking
            frame_paths = []
            
            for i, frame_data in enumerate(frames_data):
                try:
                    points = frame_data['points']
                    colors = frame_data['colors']
                    
                    # Update progress with clean status
                    progress = (i + 1) / len(frames_data)
                    st.session_state.video_export_status = f"Rendering frame {i+1}/{len(frames_data)} ({progress*100:.0f}%)"
                    
                    # Create matplotlib figure - completely emoji-free
                    fig = plt.figure(figsize=(12, 9), facecolor='black', dpi=100)
                    ax = fig.add_subplot(111, projection='3d', facecolor='black')
                    
                    if colors is not None:
                        ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                                  c=colors, s=3, alpha=0.8, edgecolors='none')
                    else:
                        ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                                  c=points[:, 2], cmap='viridis', s=3, alpha=0.8, edgecolors='none')
                    
                    # Clean styling - NO emoji characters anywhere
                    ax.set_xlabel('X', color='white', fontsize=12)
                    ax.set_ylabel('Y', color='white', fontsize=12)
                    ax.set_zlabel('Z', color='white', fontsize=12)
                    ax.tick_params(colors='white', labelsize=10)
                    ax.set_title(f'Frame {i+1}/{len(frames_data)} | {len(points)} points', 
                               color='white', fontsize=14, pad=20)
                    
                    # Equal aspect ratio (compute once for efficiency)
                    if i == 0:
                        all_points = np.vstack([f['points'] for f in frames_data])
                        max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
                        mid = np.mean(all_points, axis=0)
                        xlim = [mid[0] - max_range, mid[0] + max_range]
                        ylim = [mid[1] - max_range, mid[1] + max_range] 
                        zlim = [mid[2] - max_range, mid[2] + max_range]
                    
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
                    ax.set_zlim(zlim)
                    
                    # Save frame
                    frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                    plt.savefig(frame_path, dpi=100, bbox_inches='tight', 
                              facecolor='black', edgecolor='none', 
                              format='png')
                    plt.close()
                    
                    # Verify frame was created
                    if not os.path.exists(frame_path) or os.path.getsize(frame_path) < 1000:
                        raise ValueError(f"Frame {i+1} failed to render properly")
                    
                    frame_paths.append(frame_path)
                    
                except Exception as frame_error:
                    plt.close('all')  # Ensure matplotlib cleanup
                    st.session_state.video_export_status = f"Error on frame {i+1}: {frame_error}"
                    return
            
            # Update status for video encoding
            st.session_state.video_export_status = "Encoding video..."
            
            # Video creation process
            first_frame = cv2.imread(frame_paths[0])
            if first_frame is None:
                raise ValueError("Could not read first frame image")
            
            height, width, layers = first_frame.shape
            
            # Try multiple codecs
            codecs_to_try = [
                ('mp4v', '.mp4', 'MP4V Standard'),
                ('XVID', '.avi', 'XVID AVI'),
                ('MJPG', '.avi', 'Motion JPEG'),
            ]
            
            video_created = False
            final_video_path = None
            
            for codec, ext, description in codecs_to_try:
                st.session_state.video_export_status = f"Trying {description}..."
                
                try:
                    test_path = os.path.join(temp_dir, f"animation{ext}")
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    video = cv2.VideoWriter(test_path, fourcc, fps, (width, height))
                    
                    if not video.isOpened():
                        video.release()
                        continue
                    
                    # Write all frames
                    for j, frame_path in enumerate(frame_paths):
                        frame = cv2.imread(frame_path)
                        if frame is not None:
                            video.write(frame)
                        else:
                            video.release()
                            raise ValueError(f"Could not read frame {j+1}")
                    
                    video.release()
                    
                    # Verify the video file
                    if os.path.exists(test_path):
                        file_size = os.path.getsize(test_path)
                        if file_size > 5000:
                            final_video_path = test_path
                            video_created = True
                            st.session_state.video_export_status = f"Video ready! ({file_size / (1024*1024):.1f} MB)"
                            break
                        
                except Exception as e:
                    continue
            
            if not video_created:
                st.session_state.video_export_status = "All video codecs failed!"
                raise RuntimeError("All video codecs failed.")
            
            # Success! Prepare download
            st.session_state.video_export_complete = True
            
            with open(final_video_path, "rb") as f:
                video_data = f.read()
                
                if len(video_data) == 0:
                    raise ValueError("Video file is empty")
                
                # Determine file type
                file_ext = os.path.splitext(final_video_path)[1]
                mime_type = "video/mp4" if file_ext == '.mp4' else "video/avi"
                filename = f"pointcloud_animation_{len(frames_data)}frames_{fps}fps{file_ext}"
                
                # Display download in main area
                st.markdown("### Video Export Complete!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Frames", f"{len(frames_data)}")
                with col2:
                    st.metric("Size", f"{len(video_data) / (1024*1024):.1f} MB")
                with col3:
                    st.metric("Duration", f"{len(frames_data) / fps:.1f} sec")
                
                # Download button
                if st.download_button(
                    f"Download {file_ext.upper()} Video",
                    video_data,
                    file_name=filename,
                    mime=mime_type,
                    use_container_width=True,
                    type="primary"
                ):
                    st.balloons()
                    st.success(f"Download started! File: {filename}")
                
        except Exception as e:
            st.session_state.video_export_status = f"Export failed: {str(e)}"
            st.error(f"Error creating video: {str(e)}")
            st.info("Try using the Desktop Viewer for better animation performance.")
    
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
        st.title("Open3D Desktop Launcher")
        st.markdown("""
        **Control Panel for Interactive Point Cloud Visualization**
        
        Configure your point cloud here, then launch the **full interactive** Open3D desktop viewer!
        """)
        
        # Sidebar configuration
        with st.sidebar:
            st.header("Configuration")
            
            # Data source
            data_source = st.selectbox(
                "Data Source",
                ["Generate", "Upload File", "Animation Folder"]
            )
            
            if data_source == "Generate":
                st.subheader("Generation Settings")
                
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
                if st.button("Generate Point Cloud", type="primary"):
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
                st.subheader("File Upload")
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
                st.subheader("Animation Folder")
                st.markdown("""
                **Load a folder of PLY files for animation!**
                
                **Requirements:**
                - All files must be `.ply` format
                - Files will be loaded in alphabetical order
                - Each PLY file = one animation frame
                """)
                
                # Default to animations folder
                default_animations_dir = os.path.join(os.getcwd(), "animations")
                
                # Show available animation folders if default exists
                if os.path.exists(default_animations_dir):
                    st.markdown("**Available Animations:**")
                    try:
                        subfolders = [f for f in os.listdir(default_animations_dir) 
                                    if os.path.isdir(os.path.join(default_animations_dir, f))]
                        if subfolders:
                            selected_subfolder = st.selectbox(
                                "Quick Select Animation",
                                [""] + subfolders,
                                help="Choose from available animation folders"
                            )
                            if selected_subfolder:
                                default_path = os.path.join(default_animations_dir, selected_subfolder)
                            else:
                                default_path = default_animations_dir
                        else:
                            st.info("No animation folders found. Create some using the animation tools!")
                            default_path = default_animations_dir
                    except Exception as e:
                        st.warning(f"Could not scan animations folder: {e}")
                        default_path = default_animations_dir
                else:
                    default_path = default_animations_dir
                    st.info("Default animations folder doesn't exist yet. It will be created when you make animations.")
                
                folder_path = st.text_input(
                    "Folder Path",
                    value=default_path,
                    help="Path to folder containing PLY animation frames",
                    placeholder="animations/torus_y_24"
                )
                
                if st.button("Load Animation Frames", type="primary"):
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
        
        # Main content
        if 'points' in st.session_state:
            points = st.session_state.points
            colors = st.session_state.colors
            config = st.session_state.config
            
            # Two columns: preview and launch
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Web Preview (Limited)")
                st.caption("Basic matplotlib preview - the desktop viewer will be MUCH better!")
                self.preview_plot(points, colors)
            
            with col2:
                st.subheader("Launch Desktop Viewer")
                
                # Info about the data
                st.metric("Points", len(points))
                st.metric("Has Colors", "Yes" if colors is not None else "No")
                
                # Big launch button
                if st.button("Launch Interactive Desktop Viewer", type="primary", use_container_width=True):
                    with st.spinner("Preparing desktop viewer..."):
                        # Save data temporarily
                        ply_path, config_path, temp_dir = self.save_config_and_data(points, colors, config)
                        
                        # Launch viewer
                        success = self.launch_desktop_viewer(ply_path, config)
                        
                        if success:
                            st.success("Desktop viewer launched!")
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
                st.subheader("Manual Download")
                if st.button("Download PLY File"):
                    ply_path, _, _ = self.save_config_and_data(points, colors, config)
                    with open(ply_path, "rb") as f:
                        st.download_button(
                            "Download Point Cloud",
                            f.read(),
                            file_name="pointcloud.ply",
                            mime="application/octet-stream"
                        )
                
                # Instructions
                st.subheader("Manual Launch")
                st.code("""
# If auto-launch fails, run manually:
python source/open3d_desktop_viewer.py --file pointcloud.ply
                """)
        
        elif 'frames_data' in st.session_state:
            # Animation mode - Controls in left sidebar, visuals in main area
            frames_data = st.session_state.frames_data
            config = st.session_state.config
            fps = st.session_state.get('animation_fps', 10)
            
            # Simplified sidebar with only essential controls
            with st.sidebar:
                st.markdown("---")
                st.subheader("Animation Controls")
                
                # Essential info only
                st.metric("Frames", len(frames_data))
                st.metric("FPS", fps)
                
                # Simplified FPS setting
                new_fps = st.slider("Playback Speed (FPS)", 1, 30, fps, key="animation_fps_slider")
                if new_fps != fps:
                    st.session_state.animation_fps = new_fps
                    st.rerun()
                
                st.markdown("---")
                
                # Frame control
                st.markdown("**Frame Control:**")
                frame_idx = st.slider("Frame", 0, len(frames_data)-1, 0, key="frame_slider")
                auto_play = st.checkbox("Auto Play")
                
                st.markdown("---")
                
                # Main export action - make it prominent
                st.markdown("**Export Video:**")
                if st.button("Export MP4", type="primary", use_container_width=True):
                    st.session_state.export_video_requested = True
                    st.session_state.video_export_frames = frames_data
                    st.session_state.video_export_fps = fps
                
                # Secondary actions - simplified
                if st.button("Desktop Viewer", use_container_width=True):
                    try:
                        temp_dir, config_path, ply_paths = self.save_animation_data(frames_data)
                        script_path = Path(__file__).parent / "open3d_desktop_viewer.py"
                        cmd = ["python", str(script_path), "--animation", config_path, "--fps", str(fps)]
                        
                        if os.name == 'nt':
                            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                        else:
                            subprocess.Popen(cmd)
                        
                        st.success("Desktop viewer launched!")
                    except Exception as e:
                        st.error(f"Failed to launch: {e}")
            
            # Main area - ONLY the plot visualization
            st.subheader("Animation Viewer")
            
            # Show prominent loading bar if export is in progress
            if st.session_state.get('export_video_requested', False):
                st.markdown("---")
                st.markdown("## Exporting Video...")
                
                # Very prominent progress bar
                export_progress = st.progress(0)
                export_status = st.empty()
                
                # Large status message
                current_status = st.session_state.get('video_export_status', 'Starting export...')
                export_status.markdown(f"### {current_status}")
                
                # Update progress based on status
                if "Rendering frame" in current_status:
                    try:
                        # Extract frame progress from status message
                        parts = current_status.split()
                        if "frame" in current_status and "/" in current_status:
                            frame_info = [p for p in parts if "/" in p][0]
                            current_frame, total_frames = map(int, frame_info.split("/"))
                            progress = current_frame / total_frames
                            export_progress.progress(progress)
                    except:
                        export_progress.progress(0.5)
                elif "Encoding" in current_status:
                    export_progress.progress(0.8)
                elif "ready" in current_status or "complete" in current_status:
                    export_progress.progress(1.0)
                    st.session_state.export_video_requested = False  # Clear the request
                    st.balloons()
                
                st.markdown("---")
            
            # Create the plot using the frame_idx from sidebar
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
            # Remove emoji from title to fix matplotlib glyph warnings
            ax.set_title(f'Frame {frame_idx+1}/{len(frames_data)}: {filename}\nAnimation Preview ({len(points)} points)')
            
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
        
        # Handle video export requests at the main level (outside any columns)
        if st.session_state.get('export_video_requested', False):
            st.session_state.export_video_requested = False  # Reset flag
            frames_to_export = st.session_state.get('video_export_frames', [])
            fps_to_use = st.session_state.get('video_export_fps', 10)
            if frames_to_export:
                self.export_animation_video(frames_to_export, fps_to_use)


def main():
    """Entry point."""
    app = Open3DLauncher()
    app.run()


if __name__ == "__main__":
    main() 