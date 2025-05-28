"""Streamlit Interface - Refactored for Microexpression Analysis

Streamlined interface focused on facial landmark visualization and analysis.
Three tabs: Import, Animation, Analysis (future)
"""

import streamlit as st
import time
import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from file_manager import FileManager
from video_exporter import VideoExporter
from desktop_launcher import DesktopLauncher
from visualization import PointCloudVisualizer
from data_filters import DataFilters
import matplotlib.pyplot as plt


class StreamlitInterface:
    """Streamlined Streamlit interface for facial microexpression analysis."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Facial Microexpression Analysis",
            page_icon="🎭",
            layout="wide"
        )
        self.setup_session_state()
        self.setup_directories()
    
    def setup_directories(self):
        """Ensure data directories exist."""
        self.data_read_dir = Path("data/read")
        self.data_write_dir = Path("data/write")
        self.data_read_dir.mkdir(parents=True, exist_ok=True)
        self.data_write_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_session_state(self):
        """Initialize session state variables."""
        defaults = {
            'current_tab': 'Import',
            'csv_file_path': None,
            'csv_data': None,
            'frames_data': None,
            'animation_created': False,
            'z_scale': 25.0,
            'color_mode': 'local_movement',  # renamed from post_filter_movement
            'animation_fps': 15,
            'export_requested': False,
            'current_frame_idx': 0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def run(self):
        """Main application entry point."""
        st.title("🎭 Facial Microexpression Analysis")
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Import", "Animation", "Analysis"])
        
        with tab1:
            self.render_import_tab()
        
        with tab2:
            self.render_animation_tab()
        
        with tab3:
            self.render_analysis_tab()
    
    def render_import_tab(self):
        """Render the Import tab for CSV file selection and preview."""
        st.header("Import Facial Landmark Data")
        
        # File picker
        csv_files = list(self.data_read_dir.glob("*.csv"))
        if csv_files:
            file_names = ["Select a file..."] + [f.name for f in csv_files]
            selected_file = st.selectbox(
                "Select CSV file from data/read/",
                file_names,
                help="Place your facial landmark CSV files in the data/read/ directory"
            )
            
            if selected_file != "Select a file...":
                file_path = self.data_read_dir / selected_file
                if file_path != st.session_state.csv_file_path:
                    st.session_state.csv_file_path = file_path
                    st.session_state.csv_data = None
                    st.session_state.frames_data = None
                    st.session_state.animation_created = False
                
                # Load and preview
                self.load_and_preview_csv(file_path)
        else:
            st.warning("No CSV files found in data/read/ directory. Please add your facial landmark CSV files there.")
            st.info("Expected format: feat_0_x, feat_0_y, feat_0_z, ... for 478 facial landmarks")
    
    def load_and_preview_csv(self, file_path):
        """Load and preview the selected CSV file."""
        try:
            with st.spinner("Loading CSV file..."):
                df = pd.read_csv(file_path)
                st.session_state.csv_data = df
            
            # File info
            st.success(f"✅ Loaded: {file_path.name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows (Frames)", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                # Detect number of landmarks
                coord_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith(('_x', '_y', '_z'))]
                num_landmarks = len(coord_cols) // 3
                st.metric("Facial Landmarks", num_landmarks)
            
            # Preview data
            with st.expander("Preview Data", expanded=True):
                # Show first few rows
                st.subheader("First 5 frames")
                st.dataframe(df.head(), use_container_width=True)
                
                # Show landmark statistics
                if num_landmarks > 0:
                    st.subheader("Landmark Statistics")
                    
                    # Get coordinate columns
                    x_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_x')]
                    y_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_y')]
                    z_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_z')]
                    
                    if x_cols and y_cols and z_cols:
                        stats_data = {
                            'Axis': ['X', 'Y', 'Z'],
                            'Min': [
                                df[x_cols].min().min(),
                                df[y_cols].min().min(),
                                df[z_cols].min().min()
                            ],
                            'Max': [
                                df[x_cols].max().max(),
                                df[y_cols].max().max(),
                                df[z_cols].max().max()
                            ],
                            'Mean': [
                                df[x_cols].mean().mean(),
                                df[y_cols].mean().mean(),
                                df[z_cols].mean().mean()
                            ]
                        }
                        stats_df = pd.DataFrame(stats_data)
                        st.dataframe(stats_df, use_container_width=True)
            
            # Auto-progress to Animation tab
            st.info("✨ Data loaded successfully! Go to the **Animation** tab to create visualization.")
            
        except Exception as e:
            st.error(f"Error loading CSV: {str(e)}")
    
    def render_animation_tab(self):
        """Render the Animation tab for creating and viewing animations."""
        st.header("Create Animation")
        
        if st.session_state.csv_data is None:
            st.warning("Please import a CSV file in the Import tab first.")
            return
        
        # Animation controls in sidebar
        with st.sidebar:
            st.subheader("Animation Settings")
            
            # Color mode selection with better name
            color_mode = st.selectbox(
                "Color Mode",
                ["local_movement", "single"],
                format_func=lambda x: {
                    "local_movement": "Local Movement (Microexpressions)",
                    "single": "Single Color"
                }[x],
                help="Local Movement highlights facial movements after head motion removal"
            )
            st.session_state.color_mode = color_mode
            
            # Hidden but set defaults
            st.session_state.z_scale = 25.0  # Always use 25x
            
            # Create animation button
            if st.button("🎬 Create Facial Animation", type="primary", use_container_width=True):
                self.create_animation()
        
        # Main area - animation display
        if st.session_state.animation_created and st.session_state.frames_data:
            self.render_animation_viewer()
        else:
            st.info("Click '🎬 Create Facial Animation' in the sidebar to generate the animation.")
    
    def create_animation(self):
        """Create animation from loaded CSV data."""
        try:
            with st.spinner("Creating animation..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Parse facial landmarks
                status_text.text("Parsing facial landmarks...")
                df = st.session_state.csv_data
                
                # Get coordinate columns
                x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
                y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
                z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
                
                num_frames = len(df)
                num_landmarks = len(x_cols)
                
                frames_data = []
                
                # First pass: collect all frames
                status_text.text("Loading frames...")
                for i in range(num_frames):
                    progress_bar.progress((i + 1) / (num_frames * 2))  # First half of progress
                    
                    # Extract points for this frame
                    points = np.zeros((num_landmarks, 3))
                    for j in range(num_landmarks):
                        points[j] = [
                            df[x_cols[j]].iloc[i],
                            df[y_cols[j]].iloc[i],
                            df[z_cols[j]].iloc[i] * st.session_state.z_scale
                        ]
                    
                    frames_data.append({
                        'points': points,
                        'colors': None  # Will be set based on color mode
                    })
                
                # Apply Kabsch alignment
                status_text.text("Applying Kabsch alignment to remove head motion...")
                frames_data = DataFilters.align_frames_to_baseline(
                    frames_data, 
                    baseline_frame_idx=0
                )
                
                # Apply coloring based on mode
                if st.session_state.color_mode == 'local_movement':
                    status_text.text("Calculating local movement colors...")
                    frames_data = self.apply_local_movement_coloring(frames_data)
                else:
                    # Single color mode
                    for frame in frames_data:
                        frame['colors'] = np.tile([0.5, 0.7, 1.0], (len(frame['points']), 1))
                
                progress_bar.progress(1.0)
                
                # Generate animation name based on source file
                source_name = st.session_state.csv_file_path.stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                animation_name = f"{source_name}_{num_frames}frames_{timestamp}"
                
                # Save animation
                save_path = self.data_write_dir / animation_name
                save_path.mkdir(exist_ok=True)
                
                status_text.text("Saving animation frames...")
                FileManager.save_animation_frames(frames_data, str(save_path))
                
                # Store in session state
                st.session_state.frames_data = frames_data
                st.session_state.animation_created = True
                st.session_state.animation_name = animation_name
                
                status_text.empty()
                progress_bar.empty()
                
                st.success(f"✅ Animation created: {animation_name}")
                
                # Auto-launch interactive player
                with st.spinner("Launching interactive animation player..."):
                    time.sleep(0.5)  # Brief pause for UI update
                    success, message = DesktopLauncher.launch_interactive_animation_player(
                        frames_data, 
                        st.session_state.animation_fps
                    )
                    if success:
                        st.success("🎬 Interactive animation player launched!")
                        st.info("Use keyboard controls in the 3D window: SPACE=play/pause, N/P=next/prev frame")
                    else:
                        st.error(f"Failed to launch player: {message}")
                
        except Exception as e:
            st.error(f"Error creating animation: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    def apply_local_movement_coloring(self, frames_data):
        """Apply coloring based on frame-to-frame movement (microexpressions)."""
        from visualization import PointCloudVisualizer
        
        # Calculate frame-to-frame displacement
        for i in range(len(frames_data)):
            if i == 0:
                # First frame - no movement
                frames_data[i]['colors'] = np.zeros((len(frames_data[i]['points']), 3))
                frames_data[i]['colors'][:] = [0, 0, 1]  # Blue for no movement
            else:
                # Calculate displacement from previous frame
                prev_points = frames_data[i-1]['points']
                curr_points = frames_data[i]['points']
                
                # Compute displacement magnitude for each point
                displacement = np.linalg.norm(curr_points - prev_points, axis=1)
                
                # Store for normalization
                frames_data[i]['displacement_magnitude'] = displacement
        
        # Calculate global statistics for normalization
        all_displacements = []
        for i in range(1, len(frames_data)):
            if 'displacement_magnitude' in frames_data[i]:
                all_displacements.extend(frames_data[i]['displacement_magnitude'])
        
        if all_displacements:
            all_displacements = np.array(all_displacements)
            p95 = np.percentile(all_displacements, 95)
            
            # Apply colors based on normalized displacement
            for i in range(len(frames_data)):
                if i == 0:
                    continue
                
                displacement = frames_data[i]['displacement_magnitude']
                normalized = np.clip(displacement / p95, 0, 1) if p95 > 0 else displacement
                
                # Create color map (blue -> green -> yellow -> red)
                colors = PointCloudVisualizer._create_movement_colormap(normalized)
                frames_data[i]['colors'] = colors
        
        return frames_data
    
    def render_animation_viewer(self):
        """Render the animation viewer interface."""
        frames_data = st.session_state.frames_data
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Animation Preview")
            
            # Frame slider
            frame_idx = st.slider(
                "Frame", 
                0, len(frames_data)-1, 
                st.session_state.current_frame_idx,
                format_func=lambda x: f"Frame {x+1}/{len(frames_data)}"
            )
            st.session_state.current_frame_idx = frame_idx
            
            # Display current frame
            frame_data = frames_data[frame_idx]
            fig = PointCloudVisualizer.create_simple_animation_frame(
                frame_data['points'],
                frame_data['colors'],
                f"Frame {frame_idx + 1}/{len(frames_data)}"
            )
            st.pyplot(fig)
        
        with col2:
            st.subheader("Export")
            
            # Export to MP4
            if st.button("📹 Export to MP4", use_container_width=True):
                st.session_state.export_requested = True
            
            if st.session_state.export_requested:
                self.handle_video_export()
            
            # Animation info
            st.markdown("---")
            st.metric("Total Frames", len(frames_data))
            st.metric("FPS", st.session_state.animation_fps)
            st.metric("Duration", f"{len(frames_data)/st.session_state.animation_fps:.1f}s")
    
    def handle_video_export(self):
        """Handle video export process."""
        frames_data = st.session_state.frames_data
        fps = st.session_state.animation_fps
        
        with st.spinner("Exporting video..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message):
                if message.startswith("Rendering frame"):
                    # Extract frame number
                    parts = message.split()
                    if len(parts) >= 3:
                        try:
                            current = int(parts[2].split('/')[0])
                            total = int(parts[2].split('/')[1])
                            progress = current / total
                            progress_bar.progress(progress)
                            status_text.text(message)
                        except:
                            status_text.text(message)
                else:
                    status_text.text(message)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{st.session_state.animation_name}_export_{timestamp}.mp4"
            output_path = self.data_write_dir / output_filename
            
            # Export video
            exporter = VideoExporter()
            success = exporter.export_frames_to_video(
                frames_data,
                str(output_path),
                fps=fps,
                quality='high',
                progress_callback=progress_callback
            )
            
            progress_bar.empty()
            status_text.empty()
            
            if success:
                st.success(f"✅ Video exported to: data/write/{output_filename}")
                
                # Provide download
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="📥 Download MP4",
                        data=f,
                        file_name=output_filename,
                        mime="video/mp4"
                    )
            else:
                st.error("Failed to export video")
        
        st.session_state.export_requested = False
    
    def render_analysis_tab(self):
        """Render the Analysis tab (placeholder for future features)."""
        st.header("Feature Analysis")
        st.info("🚧 Analysis features coming soon...")
        st.markdown("""
        This tab will include:
        - Feature extraction for model training
        - Movement pattern analysis
        - Statistical summaries
        - Export features to training datasets
        """)


def main():
    """Main entry point."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 