"""Streamlit Interface

Clean, modular Streamlit interface for Open3D point cloud visualization.
Uses separate modules for each concern, keeping this file focused on UI only.
"""

import streamlit as st
import time
from source.point_cloud_generator import PointCloudGenerator, get_shape_parameters
from source.file_manager import FileManager
from source.video_exporter import VideoExporter
from source.desktop_launcher import DesktopLauncher
from source.visualization import PointCloudVisualizer
import matplotlib.pyplot as plt


class StreamlitInterface:
    """Main Streamlit application interface."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Open3D Desktop Launcher",
            page_icon="🚀",
            layout="wide"
        )
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables."""
        if 'export_status' not in st.session_state:
            st.session_state.export_status = "Ready"
        if 'animation_fps' not in st.session_state:
            st.session_state.animation_fps = 10
    
    def render_sidebar(self):
        """Render sidebar with all controls."""
        with st.sidebar:
            st.header("Configuration")
            
            # Data source selection
            data_source = st.selectbox(
                "Data Source",
                ["Generate", "Upload File", "Animation Folder"]
            )
            
            if data_source == "Generate":
                self.render_generation_controls()
            elif data_source == "Upload File":
                self.render_upload_controls()
            else:  # Animation Folder
                self.render_animation_controls()
    
    def render_generation_controls(self):
        """Render point cloud generation controls."""
        st.subheader("Generation Settings")
        
        shape_type = st.selectbox("Shape Type", ["Sphere", "Torus", "Helix", "Cube", "Random"])
        num_points = st.slider("Number of Points", 100, 10000, 2000)
        
        # Dynamic shape parameters
        shape_params = {}
        param_definitions = get_shape_parameters()
        
        for param in param_definitions.get(shape_type, []):
            if param.get('type') == 'int':
                shape_params[param['name']] = st.slider(
                    param['name'].replace('_', ' ').title(),
                    param['min'], param['max'], param['default']
                )
            else:
                shape_params[param['name']] = st.slider(
                    param['name'].replace('_', ' ').title(),
                    param['min'], param['max'], param['default']
                )
        
        if st.button("Generate Point Cloud", type="primary"):
            points, colors = PointCloudGenerator.generate(shape_type, num_points, **shape_params)
            st.session_state.points = points
            st.session_state.colors = colors
            st.session_state.config = {
                'shape_type': shape_type,
                'num_points': num_points,
                **shape_params
            }
            st.success(f"Generated {len(points)} points!")
    
    def render_upload_controls(self):
        """Render file upload controls."""
        st.subheader("File Upload")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=['csv', 'ply', 'pcd', 'xyz'],
            help="CSV: X,Y,Z,R,G,B columns. PLY/PCD/XYZ: Standard formats"
        )
        
        if uploaded_file is not None:
            try:
                points, colors = FileManager.load_uploaded_file(uploaded_file)
                st.session_state.points = points
                st.session_state.colors = colors
                st.session_state.config = {
                    'source': 'uploaded',
                    'filename': uploaded_file.name,
                    'num_points': len(points)
                }
                st.success(f"Loaded {len(points)} points from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    def render_animation_controls(self):
        """Render animation folder controls."""
        st.subheader("Animation Folder")
        
        # Quick select from available animations
        available_folders = FileManager.get_animation_folders()
        if available_folders:
            selected_folder = st.selectbox("Available Animations", [""] + available_folders)
            if selected_folder:
                folder_path = f"animations/{selected_folder}"
            else:
                folder_path = st.text_input("Custom Path", placeholder="animations/my_animation")
        else:
            folder_path = st.text_input("Folder Path", placeholder="animations/torus_y_24")
        
        if st.button("Load Animation Frames", type="primary") and folder_path:
            try:
                with st.spinner("Loading animation frames..."):
                    frames_data = FileManager.load_animation_folder(folder_path)
                st.session_state.frames_data = frames_data
                st.session_state.config = {'source': 'animation', 'folder_path': folder_path}
                st.success(f"Loaded {len(frames_data)} frames")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    def render_single_pointcloud_view(self):
        """Render interface for single point cloud."""
        points = st.session_state.points
        colors = st.session_state.colors
        config = st.session_state.config
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Web Preview (Limited)")
            st.caption("Basic matplotlib preview - the desktop viewer will be MUCH better!")
            fig = PointCloudVisualizer.create_preview_plot(points, colors)
            st.pyplot(fig)
        
        with col2:
            st.subheader("Launch Desktop Viewer")
            st.metric("Points", len(points))
            st.metric("Has Colors", "Yes" if colors is not None else "No")
            
            if st.button("Launch Interactive Desktop Viewer", type="primary", use_container_width=True):
                success, message = DesktopLauncher.launch_single_viewer(points, colors, config)
                if success:
                    st.success("Desktop viewer launched!")
                    st.info(message)
                else:
                    st.error(message)
    
    def render_animation_view(self):
        """Render interface for animation."""
        frames_data = st.session_state.frames_data
        
        # Initialize frame index if not set
        if 'current_frame_idx' not in st.session_state:
            st.session_state.current_frame_idx = 0
        
        # Animation controls in sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("Animation Controls")
            st.metric("Frames", len(frames_data))
            
            # Simplified FPS control
            fps = st.slider("FPS", 1, 30, st.session_state.animation_fps)
            st.session_state.animation_fps = fps
            
            st.markdown("---")
            
            # Visualization options
            st.subheader("View Options")
            view_mode = st.selectbox(
                "Display Mode",
                ["Thumbnail Grid", "Timeline Strip", "Single Frame"],
                help="Choose how to display the animation frames"
            )
            
            # View-specific options
            if view_mode == "Thumbnail Grid":
                max_thumbnails = st.slider("Max Thumbnails", 8, 32, 16)
                grid_cols = st.selectbox("Grid Columns", [3, 4, 5, 6], index=1)
            elif view_mode == "Timeline Strip":
                max_strip_frames = st.slider("Max Strip Frames", 6, 20, 12)
            else:  # Single Frame
                frame_idx = st.slider("Frame", 0, len(frames_data)-1, st.session_state.current_frame_idx)
                st.session_state.current_frame_idx = frame_idx
            
            st.markdown("---")
            
            # Export and viewer controls
            st.subheader("Actions")
            
            # Export video - simplified
            if st.button("Export Video", type="primary", use_container_width=True):
                st.session_state.export_requested = True
            
            # Desktop viewer
            if st.button("Desktop Viewer", use_container_width=True):
                success, message = DesktopLauncher.launch_animation_viewer(frames_data, fps)
                if success:
                    st.success("Animation viewer launched!")
                else:
                    st.error(message)
        
        # Main area - visualization based on selected mode
        st.subheader("Animation Viewer")
        
        # Handle video export
        if st.session_state.get('export_requested', False):
            self.handle_video_export(frames_data, fps)
        
        # Show visualization based on selected mode
        if view_mode == "Thumbnail Grid":
            st.markdown(f"**Grid Overview** - Showing up to {max_thumbnails} frames in {grid_cols} columns")
            with st.spinner("Generating thumbnail grid..."):
                fig = PointCloudVisualizer.create_animation_thumbnail_grid(
                    frames_data, max_frames=max_thumbnails, grid_cols=grid_cols
                )
                st.pyplot(fig)
                plt.close(fig)
            
            # Show sampling info if frames were limited
            if len(frames_data) > max_thumbnails:
                st.info(f"📊 Showing {max_thumbnails} representative frames from {len(frames_data)} total frames. "
                       f"Frames are sampled evenly across the animation.")
        
        elif view_mode == "Timeline Strip":
            st.markdown(f"**Timeline View** - Showing up to {max_strip_frames} frames in sequence")
            with st.spinner("Generating timeline strip..."):
                fig = PointCloudVisualizer.create_animation_strip(
                    frames_data, max_frames=max_strip_frames
                )
                st.pyplot(fig)
                plt.close(fig)
            
            if len(frames_data) > max_strip_frames:
                st.info(f"📊 Showing {max_strip_frames} representative frames from {len(frames_data)} total frames.")
        
        else:  # Single Frame mode
            current_frame = st.session_state.current_frame_idx
            st.markdown(f"**Single Frame View** - Frame {current_frame + 1} of {len(frames_data)}")
            
            # Add frame navigation buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("⏮️ First"):
                    st.session_state.current_frame_idx = 0
                    st.rerun()
            with col2:
                if st.button("⏪ Prev"):
                    st.session_state.current_frame_idx = max(0, current_frame - 1)
                    st.rerun()
            with col3:
                st.write(f"Frame {current_frame + 1}")
            with col4:
                if st.button("Next ⏩"):
                    st.session_state.current_frame_idx = min(len(frames_data) - 1, current_frame + 1)
                    st.rerun()
            with col5:
                if st.button("Last ⏭️"):
                    st.session_state.current_frame_idx = len(frames_data) - 1
                    st.rerun()
            
            # Show single frame
            bounds = PointCloudVisualizer.calculate_animation_bounds(frames_data)
            fig = PointCloudVisualizer.create_animation_frame_plot(
                frames_data[current_frame], current_frame, len(frames_data), bounds
            )
            st.pyplot(fig)
            plt.close(fig)
    
    def handle_video_export(self, frames_data, fps):
        """Handle video export with progress tracking."""
        st.markdown("---")
        st.markdown("## Exporting Video...")
        
        export_progress = st.progress(0)
        export_status = st.empty()
        
        def progress_callback(message):
            st.session_state.export_status = message
            export_status.markdown(f"### {message}")
            
            # Update progress bar based on message
            if "Rendering frame" in message:
                try:
                    parts = message.split()
                    if "/" in message:
                        frame_info = [p for p in parts if "/" in p][0]
                        current, total = map(int, frame_info.split("/"))
                        progress = current / total * 0.8  # 80% for rendering
                        export_progress.progress(progress)
                except:
                    pass
            elif "Encoding" in message:
                export_progress.progress(0.9)
            elif "complete" in message:
                export_progress.progress(1.0)
        
        try:
            exporter = VideoExporter(progress_callback)
            video_path = exporter.export_video(frames_data, fps)
            
            if video_path:
                with open(video_path, "rb") as f:
                    video_data = f.read()
                
                st.markdown("### Video Export Complete!")
                st.download_button(
                    "Download Video",
                    video_data,
                    file_name=f"animation_{len(frames_data)}frames_{fps}fps.mp4",
                    mime="video/mp4",
                    type="primary"
                )
                st.balloons()
            
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
        
        finally:
            st.session_state.export_requested = False
    
    def run(self):
        """Main application entry point."""
        st.title("Open3D Desktop Launcher")
        st.markdown("**Control Panel for Interactive Point Cloud Visualization**")
        
        self.render_sidebar()
        
        # Main content based on loaded data
        if 'points' in st.session_state:
            self.render_single_pointcloud_view()
        elif 'frames_data' in st.session_state:
            self.render_animation_view()
        else:
            self.render_welcome_screen()
    
    def render_welcome_screen(self):
        """Render welcome screen when no data is loaded."""
        st.info("👈 Configure your point cloud in the sidebar to get started!")
        
        # Quick overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🌐 Web Interface")
            st.markdown("✅ Easy configuration\n✅ File uploads\n❌ Limited interactivity")
        
        with col2:
            st.subheader("🖥️ Desktop Viewer")
            st.markdown("✅ **Smooth rotation**\n✅ **Professional lighting**\n✅ **Screenshot capture**")
        
        with col3:
            st.subheader("🎬 Animation")
            st.markdown("✅ **Folder loading**\n✅ **Video export**\n✅ **Animated playback**")


def main():
    """Entry point for the application."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 