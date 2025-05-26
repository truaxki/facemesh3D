"""Streamlit Interface

Clean, modular Streamlit interface for Open3D point cloud visualization.
Uses separate modules for each concern, keeping this file focused on UI only.
Enhanced with persistent user preferences and configurable settings.
"""

import streamlit as st
import time
import json
import numpy as np
from pathlib import Path
from point_cloud_generator import PointCloudGenerator, get_shape_parameters
from file_manager import FileManager
from video_exporter import VideoExporter
from desktop_launcher import DesktopLauncher
from visualization import PointCloudVisualizer
import matplotlib.pyplot as plt


class StreamlitInterface:
    """Main Streamlit application interface with user preferences."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Open3D Desktop Launcher",
            page_icon="🚀",
            layout="wide"
        )
        self.load_user_preferences()
        self.setup_session_state()
    
    def load_user_preferences(self):
        """Load user preferences from file or set defaults."""
        self.preferences_file = Path("user_preferences.json")
        
        # Default preferences
        self.default_prefs = {
            'animation': {
                'default_fps': 15,
                'default_view_mode': 'Thumbnail Grid',
                'default_max_thumbnails': 16,
                'default_grid_columns': 4,
                'default_max_strip_frames': 12,
                'auto_launch_desktop': False
            },
            'generation': {
                'default_shape': 'Sphere',
                'default_points': 3000,
                'default_sphere_radius': 1.0,
                'default_torus_radius': 1.0,
                'default_helix_turns': 3.0
            },
            'export': {
                'default_video_quality': 'High',
                'include_timestamp': True,
                'auto_download': True
            },
            'interface': {
                'show_advanced_controls': False,
                'auto_preview': True,
                'show_tooltips': True
            }
        }
        
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    saved_prefs = json.load(f)
                # Merge with defaults (in case new preferences were added)
                self.preferences = {**self.default_prefs, **saved_prefs}
            else:
                self.preferences = self.default_prefs
        except Exception:
            self.preferences = self.default_prefs
    
    def save_user_preferences(self):
        """Save current preferences to file."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            st.error(f"Could not save preferences: {e}")
    
    def setup_session_state(self):
        """Initialize session state variables with user preferences."""
        if 'export_status' not in st.session_state:
            st.session_state.export_status = "Ready"
        if 'animation_fps' not in st.session_state:
            st.session_state.animation_fps = self.preferences['animation']['default_fps']
        if 'view_mode' not in st.session_state:
            st.session_state.view_mode = self.preferences['animation']['default_view_mode']
        if 'max_thumbnails' not in st.session_state:
            st.session_state.max_thumbnails = self.preferences['animation']['default_max_thumbnails']
        if 'grid_columns' not in st.session_state:
            st.session_state.grid_columns = self.preferences['animation']['default_grid_columns']
    
    def render_sidebar(self):
        """Render sidebar with all controls."""
        with st.sidebar:
            # Settings button at top of sidebar
            if st.button("⚙️ Settings & Preferences", use_container_width=True, help="Configure your default settings"):
                st.session_state.show_settings = not st.session_state.get('show_settings', False)
            
            # Show settings panel in sidebar if toggled
            if st.session_state.get('show_settings', False):
                self.render_sidebar_settings()
                st.markdown("---")
            
            st.header("Configuration")
            
            # Data source selection
            data_source = st.selectbox(
                "Data Source",
                ["Generate", "Upload File", "Animation Folder", "Facial Landmark CSV"]
            )
            
            if data_source == "Generate":
                self.render_generation_controls()
            elif data_source == "Upload File":
                self.render_upload_controls()
            elif data_source == "Animation Folder":
                self.render_animation_controls()
            else:  # Facial Landmark CSV
                self.render_facial_csv_controls()
    
    def render_sidebar_settings(self):
        """Render organized settings panel in sidebar by functional area."""
        st.subheader("⚙️ User Preferences")
        
        # 📁 LOAD SETTINGS
        with st.expander("📁 Load Settings", expanded=True):
            new_auto_launch = st.checkbox(
                "Auto-launch Desktop Viewer",
                value=self.preferences['animation']['auto_launch_desktop'],
                help="Automatically open 3D viewer when loading animations"
            )
            
            auto_preview = st.checkbox(
                "Auto-generate Preview",
                value=self.preferences['interface']['auto_preview'],
                help="Automatically show preview when loading data"
            )
        
        # 🎲 GENERATE SETTINGS  
        with st.expander("🎲 Generate Settings", expanded=False):
            new_shape = st.selectbox(
                "Default Shape",
                ["Sphere", "Torus", "Helix", "Cube", "Random"],
                index=["Sphere", "Torus", "Helix", "Cube", "Random"].index(
                    self.preferences['generation']['default_shape']
                )
            )
            
            new_points = st.slider(
                "Default Points",
                10, 100,
                self.preferences['generation']['default_points']
            )
        
        # 🎬 ANIMATE SETTINGS
        with st.expander("🎬 Animate Settings", expanded=True):
            new_fps = st.slider(
                "Default FPS", 
                1, 30, 
                self.preferences['animation']['default_fps'],
                help="Animation playback and export speed"
            )
            
            new_view_mode = st.selectbox(
                "Default View Mode",
                ["Thumbnail Grid", "Timeline Strip", "Single Frame"],
                index=["Thumbnail Grid", "Timeline Strip", "Single Frame"].index(
                    self.preferences['animation']['default_view_mode']
                ),
                help="Default way to display animations"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                new_max_thumbnails = st.slider(
                    "Max Thumbnails",
                    8, 32,
                    self.preferences['animation']['default_max_thumbnails'],
                    help="Grid thumbnail count"
                )
            
            with col2:
                new_grid_columns = st.selectbox(
                    "Grid Columns",
                    [3, 4, 5, 6],
                    index=[3, 4, 5, 6].index(self.preferences['animation']['default_grid_columns']),
                    help="Thumbnail grid columns"
                )
            
            new_video_quality = st.selectbox(
                "Export Quality",
                ["Low", "Medium", "High", "Ultra"],
                index=["Low", "Medium", "High", "Ultra"].index(
                    self.preferences['export']['default_video_quality']
                ),
                help="Default video export quality"
            )
            
            new_auto_download = st.checkbox(
                "Auto-download Exports",
                value=self.preferences['export']['auto_download'],
                help="Automatically download when export completes"
            )
        
        # Save/Reset buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save All", type="primary", use_container_width=True):
                # Update all preferences
                self.preferences['animation'].update({
                    'default_fps': new_fps,
                    'default_view_mode': new_view_mode,
                    'default_max_thumbnails': new_max_thumbnails,
                    'default_grid_columns': new_grid_columns,
                    'auto_launch_desktop': new_auto_launch
                })
                
                self.preferences['generation'].update({
                    'default_shape': new_shape,
                    'default_points': new_points
                })
                
                self.preferences['export'].update({
                    'default_video_quality': new_video_quality,
                    'auto_download': new_auto_download
                })
                
                self.preferences['interface'].update({
                    'auto_preview': auto_preview
                })
                
                # Save to file
                self.save_user_preferences()
                
                # Update session state
                st.session_state.animation_fps = new_fps
                st.session_state.view_mode = new_view_mode
                st.session_state.max_thumbnails = new_max_thumbnails
                st.session_state.grid_columns = new_grid_columns
                
                st.success("✅ All settings saved!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                self.preferences = self.default_prefs
                self.save_user_preferences()
                st.success("✅ Reset to defaults!")
                time.sleep(1)
                st.rerun()
    
    def render_generation_controls(self):
        """Render point cloud generation controls with user preferences."""
        st.subheader("Generation Settings")
        
        # Use user preferences as defaults
        default_shape = self.preferences['generation']['default_shape']
        default_points = self.preferences['generation']['default_points']
        
        shape_type = st.selectbox(
            "Shape Type", 
            ["Sphere", "Torus", "Helix", "Cube", "Random"],
            index=["Sphere", "Torus", "Helix", "Cube", "Random"].index(default_shape)
        )
        num_points = st.slider("Number of Points", 100, 10000, default_points)
        
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
                
                # Auto-launch desktop viewer if enabled
                if self.preferences['animation']['auto_launch_desktop']:
                    fps = st.session_state.animation_fps
                    success, message = DesktopLauncher.launch_animation_viewer(frames_data, fps)
                    if success:
                        st.info("🚀 Auto-launched desktop viewer!")
                    
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
        """Render interface for animation with clean, non-redundant controls."""
        frames_data = st.session_state.frames_data
        
        # Initialize frame index if not set
        if 'current_frame_idx' not in st.session_state:
            st.session_state.current_frame_idx = 0
        
        # Clean animation info in sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("Animation Info")
            st.metric("Frames", len(frames_data))
            
            # Single action buttons
            st.subheader("Actions")
            
            # Single export button (no redundant controls)
            if st.button("🎥 Export Video", type="primary", use_container_width=True):
                st.session_state.export_requested = True
            
            # Desktop viewer options - two choices
            st.subheader("Desktop Viewers")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🖥️ File Viewer", use_container_width=True, help="Traditional file-based animation viewer"):
                    # Use FPS from settings
                    fps = st.session_state.animation_fps
                    success, message = DesktopLauncher.launch_animation_viewer(frames_data, fps)
                    if success:
                        st.success("Animation viewer launched!")
                    else:
                        st.error(message)
            
            with col2:
                if st.button("🎬 Interactive Player", use_container_width=True, help="Enhanced interactive animation player", type="secondary"):
                    # Use FPS from settings
                    fps = st.session_state.animation_fps
                    with st.spinner("Starting interactive animation player..."):
                        success, message = DesktopLauncher.launch_interactive_animation_player(frames_data, fps)
                    if success:
                        st.success("🎬 Interactive animation player completed!")
                        st.info("💡 The interactive player provides smooth real-time controls like play/pause, speed control, frame stepping, and more!")
                    else:
                        st.error(message)
            
            # Help info for desktop viewers
            with st.expander("ℹ️ Viewer Comparison", expanded=False):
                st.markdown("**🖥️ File Viewer:**")
                st.markdown("- Traditional viewer")
                st.markdown("- Loads frames from files")
                st.markdown("- Simple and reliable")
                st.markdown("")
                st.markdown("**🎬 Interactive Player:**")
                st.markdown("- Enhanced with Open3D callbacks")
                st.markdown("- Smooth real-time playback")
                st.markdown("- **In-window controls** (SPACEBAR, N/P, etc.)")
                st.markdown("- Variable speed, reverse, frame stepping")
                st.markdown("- No file I/O overhead")
                st.markdown("- Better for exploration and analysis")
        
        # Main area - visualization based on settings (no redundant controls)
        st.subheader("Animation Viewer")
        
        # Handle video export
        if st.session_state.get('export_requested', False):
            # Use FPS from settings
            fps = st.session_state.animation_fps
            self.handle_video_export(frames_data, fps)
        
        # Show visualization based on saved view mode preference
        view_mode = st.session_state.view_mode
        max_thumbnails = st.session_state.max_thumbnails
        grid_cols = st.session_state.grid_columns
        
        if view_mode == "Thumbnail Grid":
            st.markdown(f"**Grid Overview** - {max_thumbnails} frames in {grid_cols} columns")
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
            max_strip_frames = self.preferences['animation']['default_max_strip_frames']
            st.markdown(f"**Timeline View** - {max_strip_frames} frames in sequence")
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
            
            # Frame navigation controls
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
            
            # Frame slider for single frame mode
            frame_idx = st.slider(
                "Select Frame", 
                0, len(frames_data)-1, 
                st.session_state.current_frame_idx,
                help="Navigate through animation frames"
            )
            if frame_idx != st.session_state.current_frame_idx:
                st.session_state.current_frame_idx = frame_idx
                st.rerun()
            
            # Show single frame
            bounds = PointCloudVisualizer.calculate_animation_bounds(frames_data)
            fig = PointCloudVisualizer.create_animation_frame_plot(
                frames_data[current_frame], current_frame, len(frames_data), bounds
            )
            st.pyplot(fig)
            plt.close(fig)
    
    def handle_video_export(self, frames_data, fps):
        """Handle video export with progress tracking and user preferences."""
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
                
                # Auto-download if enabled in preferences
                download_button = st.download_button(
                    "Download Video",
                    video_data,
                    file_name=f"animation_{len(frames_data)}frames_{fps}fps.mp4",
                    mime="video/mp4",
                    type="primary"
                )
                
                if self.preferences['export']['auto_download'] and download_button:
                    st.balloons()
                else:
                    st.balloons()
            
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
        
        finally:
            st.session_state.export_requested = False
    
    def render_facial_csv_controls(self):
        """Render facial landmark CSV import controls."""
        st.subheader("🎭 Facial Landmark CSV Import")
        st.markdown("Import time series facial landmark data (feat_N_x, feat_N_y, feat_N_z format)")
        
        uploaded_file = st.file_uploader(
            "Choose facial landmark CSV file",
            type=['csv'],
            help="CSV with feat_0_x, feat_0_y, feat_0_z... columns and Time (s) column"
        )
        
        if uploaded_file is not None:
            try:
                # Preview the file structure
                content = uploaded_file.getvalue().decode('utf-8')
                lines = content.split('\n')
                
                st.markdown("**📋 File Preview:**")
                st.code(f"Filename: {uploaded_file.name}")
                st.code(f"Size: {len(uploaded_file.getvalue())} bytes")
                st.code(f"Lines: {len(lines)}")
                
                # Check if it's a valid facial landmark CSV
                from io import StringIO
                import pandas as pd
                df = pd.read_csv(StringIO(content))
                
                if FileManager._is_facial_landmark_csv(df):
                    # Extract info
                    feat_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_x')]
                    num_landmarks = len(feat_cols)
                    num_frames = len(df)
                    
                    # Show file info
                    st.success(f"✅ Valid facial landmark CSV detected!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Landmarks", num_landmarks)
                    with col2:
                        st.metric("Frames", num_frames)
                    with col3:
                        duration = df.iloc[-1].get('Time (s)', num_frames) if 'Time (s)' in df.columns else num_frames
                        st.metric("Duration", f"{duration:.1f}s")
                    
                    # Import options
                    st.markdown("**🎨 Import Options:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        color_mode = st.selectbox(
                            "Color Mode",
                            ["movement", "post_filter_movement", "depth", "regions", "single"],
                            index=0,
                            help="movement = Color by raw motion intensity from CSV\n"
                                 "post_filter_movement = Color by frame-to-frame displacement AFTER filtering (recommended with filters)\n"
                                 "depth = Color by Z distance\n"
                                 "regions = Color by facial regions\n"
                                 "single = Single color for all points"
                        )
                        
                        # Show info about post-filter movement
                        if color_mode == "post_filter_movement":
                            st.info("🎯 **Post-Filter Movement**: Measures displacement between consecutive frames AFTER filters are applied. Perfect for isolating local facial movements after removing head motion with Kabsch alignment!")
                    
                    with col2:
                        max_frames = st.number_input(
                            "Max Frames (0 = all)",
                            min_value=0,
                            max_value=num_frames,
                            value=min(200, num_frames),
                            help="Limit frames for faster processing (0 = use all frames)"
                        )
                    
                    # Z-axis scaling control
                    st.markdown("**📏 3D Proportions:**")
                    z_scale = st.slider(
                        "Z-Axis Scale Factor",
                        min_value=0.1,
                        max_value=10000.0,
                        value=25.0,
                        step=0.1,
                        help="Scale Z-depth for better 3D visualization\n"
                             "1.0 = original proportions (usually too flat)\n"
                             "25.0 = optimal for facial data (user-tested)\n"
                             "50-100+ = higher depth for analysis\n"
                             "Facial data often needs significant scaling!"
                    )
                    
                    # Data Filtering Section
                    st.markdown("**🔧 Data Filtering (Optional):**")
                    
                    # Import the DataFilters class
                    from data_filters import DataFilters
                    
                    # Get available filters
                    available_filters = DataFilters.get_available_filters()
                    
                    # Filter selection
                    enable_filtering = st.checkbox("Enable Data Filtering", value=False, 
                                                  help="Apply mathematical transformations to the data before creating animation")
                    
                    filters_to_apply = []
                    
                    if enable_filtering:
                        st.markdown("**Select Filters to Apply:**")
                        
                        # Kabsch Alignment Filter
                        if st.checkbox("🎯 Kabsch Alignment", value=False, 
                                      help="Align all frames to a baseline frame using optimal rotation (removes rigid body motion)"):
                            baseline_frame = st.number_input(
                                "Baseline Frame Index",
                                min_value=0,
                                max_value=num_frames-1,
                                value=0,
                                help="Frame to use as reference for alignment (0 = first frame)"
                            )
                            filters_to_apply.append({
                                'filter': 'kabsch_alignment',
                                'params': {'baseline_frame_idx': baseline_frame}
                            })
                            
                            st.info("🎯 **Kabsch Algorithm**: Removes rigid body motion by optimally aligning all frames to the baseline. Perfect for focusing on facial expressions while removing head movement.")
                        
                        # Center Frames Filter
                        if st.checkbox("📍 Center Frames", value=False,
                                      help="Center all frames at origin (removes translation)"):
                            filters_to_apply.append({
                                'filter': 'center_frames',
                                'params': {}
                            })
                        
                        # Scale Frames Filter
                        if st.checkbox("📏 Scale Frames", value=False,
                                      help="Scale all frames by a constant factor"):
                            scale_factor = st.number_input(
                                "Scale Factor",
                                min_value=0.1,
                                max_value=10.0,
                                value=1.0,
                                step=0.1,
                                help="Scaling factor (1.0 = no change, >1.0 = larger, <1.0 = smaller)"
                            )
                            filters_to_apply.append({
                                'filter': 'scale_frames',
                                'params': {'scale_factor': scale_factor}
                            })
                        
                        # Remove Outliers Filter
                        if st.checkbox("🧹 Remove Outliers", value=False,
                                      help="Remove points that are far from the centroid"):
                            std_threshold = st.number_input(
                                "Standard Deviation Threshold",
                                min_value=1.0,
                                max_value=5.0,
                                value=2.0,
                                step=0.1,
                                help="Points beyond this many standard deviations from mean distance will be removed"
                            )
                            filters_to_apply.append({
                                'filter': 'remove_outliers',
                                'params': {'std_threshold': std_threshold}
                            })
                        
                        # Custom Matrix Transform
                        if st.checkbox("🔢 Custom Matrix Transform", value=False,
                                      help="Apply a custom transformation matrix (advanced)"):
                            st.markdown("**Enter 3x3 Rotation Matrix (comma-separated rows):**")
                            
                            # Default identity matrix
                            default_matrix = "1,0,0\n0,1,0\n0,0,1"
                            matrix_text = st.text_area(
                                "Transformation Matrix",
                                value=default_matrix,
                                height=100,
                                help="Enter a 3x3 matrix as comma-separated values, one row per line"
                            )
                            
                            try:
                                # Parse matrix
                                rows = matrix_text.strip().split('\n')
                                matrix_data = []
                                for row in rows:
                                    matrix_data.append([float(x.strip()) for x in row.split(',')])
                                
                                custom_matrix = np.array(matrix_data)
                                
                                if custom_matrix.shape == (3, 3):
                                    st.success(f"✅ Valid 3x3 matrix")
                                    filters_to_apply.append({
                                        'filter': 'custom_matrix',
                                        'params': {'matrix': custom_matrix}
                                    })
                                else:
                                    st.error(f"❌ Matrix must be 3x3, got {custom_matrix.shape}")
                            except Exception as e:
                                st.error(f"❌ Invalid matrix format: {str(e)}")
                        
                        # Show filter summary
                        if filters_to_apply:
                            st.markdown("**🔧 Filters to Apply:**")
                            for i, filter_config in enumerate(filters_to_apply):
                                filter_info = available_filters[filter_config['filter']]
                                st.write(f"{i+1}. **{filter_info['name']}**: {filter_info['description']}")
                    
                    # Folder naming
                    subject = df.iloc[0].get('Subject Name', 'unknown') if 'Subject Name' in df.columns else 'unknown'
                    test = df.iloc[0].get('Test Name', 'baseline') if 'Test Name' in df.columns else 'baseline'
                    actual_frames = max_frames if max_frames > 0 else num_frames
                    
                    # Add filter suffix to default name
                    filter_suffix = ""
                    if filters_to_apply:
                        filter_names = [f['filter'] for f in filters_to_apply]
                        if 'kabsch_alignment' in filter_names:
                            filter_suffix += "_aligned"
                        if 'center_frames' in filter_names:
                            filter_suffix += "_centered"
                        if 'remove_outliers' in filter_names:
                            filter_suffix += "_filtered"
                    
                    default_name = f"facemesh_{subject}_{test}_{actual_frames}frames{filter_suffix}"
                    
                    folder_name = st.text_input(
                        "Animation Folder Name",
                        value=default_name,
                        help="Name for the new animation folder in /animations/"
                    )
                    
                    # Create animation button
                    if st.button("🎬 Create Facial Animation", type="primary", use_container_width=True):
                        with st.spinner("Converting facial landmarks to animation..."):
                            try:
                                folder_path, saved_frames, metadata = FileManager.create_facial_animation_folder(
                                    uploaded_file, 
                                    folder_name=folder_name,
                                    color_mode=color_mode,
                                    max_frames=max_frames if max_frames > 0 else None,
                                    z_scale=z_scale,
                                    filters=filters_to_apply if enable_filtering else None
                                )
                                
                                st.success(f"🎉 Animation created successfully!")
                                st.info(f"📁 Folder: {folder_path}")
                                st.info(f"📊 Frames saved: {saved_frames}")
                                
                                # Show metadata
                                with st.expander("📋 Animation Details", expanded=True):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Subject:** {metadata['subject']}")
                                        st.write(f"**Test:** {metadata['test']}")
                                        st.write(f"**Landmarks:** {metadata['landmarks_count']}")
                                    with col2:
                                        st.write(f"**Color Mode:** {metadata['color_mode']}")
                                        st.write(f"**Z-Scale:** {metadata['z_scale']}x")
                                        st.write(f"**Duration:** {metadata['duration_seconds']:.1f}s")
                                        st.write(f"**Source:** {metadata['source_file']}")
                                
                                # Auto-load the animation
                                frames_data = FileManager.load_animation_folder(folder_path)
                                st.session_state.frames_data = frames_data
                                st.session_state.config = {
                                    'source': 'facial_landmark_csv',
                                    'folder_path': folder_path,
                                    'metadata': metadata
                                }
                                
                                st.balloons()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error creating animation: {str(e)}")
                    
                    # Preview first frame
                    if st.checkbox("👁️ Preview First Frame", value=False):
                        with st.spinner("Loading preview..."):
                            try:
                                frames_data = FileManager._parse_facial_landmark_csv(df, color_mode, z_scale)
                                
                                # Apply filters to preview if enabled
                                if enable_filtering and filters_to_apply:
                                    st.info(f"🔧 Applying {len(filters_to_apply)} filter(s) to preview...")
                                    frames_data = DataFilters.apply_filter_chain(frames_data, filters_to_apply)
                                
                                if frames_data:
                                    points = frames_data[0]['points']
                                    colors = frames_data[0]['colors']
                                    
                                    st.session_state.points = points
                                    st.session_state.colors = colors
                                    st.session_state.config = {
                                        'source': 'facial_preview',
                                        'num_points': len(points),
                                        'color_mode': color_mode,
                                        'z_scale': z_scale,
                                        'applied_filters': filters_to_apply if enable_filtering else []
                                    }
                                    
                                    filter_info = f" (with {len(filters_to_apply)} filters)" if enable_filtering and filters_to_apply else ""
                                    st.success(f"✅ Preview loaded: {len(points)} facial landmarks (Z-scale: {z_scale}x){filter_info}")
                                    
                            except Exception as e:
                                st.error(f"❌ Preview error: {str(e)}")
                
                else:
                    st.warning("⚠️ This doesn't appear to be a facial landmark CSV file.")
                    st.info("Expected format: feat_0_x, feat_0_y, feat_0_z, feat_1_x, feat_1_y, feat_1_z, ...")
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV: {str(e)}")
    
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
        
        # Settings hint
        st.markdown("💡 **New!** Click **⚙️ Settings & Preferences** in the sidebar to configure defaults for Load, Generate, and Animate operations.")
        
        # Facial landmark highlight
        st.markdown("🎭 **NEW!** Facial Landmark CSV Import - Convert time series facial data into stunning 3D animations with movement intensity coloring!")
        
        # Interactive animation highlight
        st.markdown("🎬 **Enhanced!** New Interactive Animation Player with real-time controls, variable speed, frame stepping, and smooth Open3D callbacks!")
        
        # Quick overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("🌐 Web Interface")
            st.markdown("✅ Easy configuration\n✅ File uploads\n✅ Settings management\n❌ Limited interactivity")
        
        with col2:
            st.subheader("🎭 Facial Data")
            st.markdown("✅ **CSV time series import**\n✅ **Movement intensity colors**\n✅ **478 landmark support**\n✅ **Auto-animation creation**")
        
        with col3:
            st.subheader("🖥️ Desktop Viewer")
            st.markdown("✅ **Smooth rotation**\n✅ **Professional lighting**\n✅ **Screenshot capture**\n✅ **File-based animation**")
        
        with col4:
            st.subheader("🎬 Interactive Player")
            st.markdown("✅ **Real-time animation**\n✅ **Variable speed control**\n✅ **Frame stepping**\n✅ **Reverse playback**\n✅ **Live interaction**")


def main():
    """Entry point for the application."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 