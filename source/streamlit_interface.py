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
            'baseline_frames': 30,
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
        
        # Experiment (folder) picker
        experiment_dirs = [d for d in self.data_read_dir.glob("*") if d.is_dir()]
        if experiment_dirs:
            # Sort experiment folders numerically if possible
            folder_names = ["Select an experiment..."] + sorted([f.name for f in experiment_dirs], 
                key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x)
            selected_experiment = st.selectbox(
                "Select experiment from data/read/",
                folder_names,
                help="Place your experiment folders containing facial landmark CSV files in the data/read/ directory"
            )
            
            if selected_experiment != "Select an experiment...":
                experiment_path = self.data_read_dir / selected_experiment
                csv_files = list(experiment_path.glob("*.csv"))
                
                if csv_files:
                    # Sort CSV files and find baseline
                    csv_files = sorted(csv_files, key=lambda x: x.stem)
                    baseline_file = next((f for f in csv_files if f.stem.endswith("-baseline")), None)
                    
                    # Create list of tests with baseline first if it exists
                    test_options = []
                    if baseline_file:
                        test_options.append(baseline_file.stem)
                        other_tests = [f.stem for f in csv_files if f != baseline_file]
                        test_options.extend(sorted(other_tests))
                    else:
                        test_options = [f.stem for f in csv_files]
                    
                    # Test selection dropdown
                    selected_test = st.selectbox(
                        "Test Selection",
                        test_options,
                        index=0 if baseline_file else 0,
                        help="Select the test to analyze. Baseline test is recommended for initial analysis."
                    )
                    
                    # Get the selected file path
                    file_path = next(f for f in csv_files if f.stem == selected_test)
                    
                    if file_path != st.session_state.csv_file_path:
                        st.session_state.csv_file_path = file_path
                        st.session_state.csv_data = None
                        st.session_state.frames_data = None
                        st.session_state.animation_created = False
                        
                        # Show info about the experiment
                        st.info(f"📊 Found {len(csv_files)} tests in experiment. Currently using: {file_path.name}")
                    
                    # Load and preview
                    self.load_and_preview_csv(file_path)
                else:
                    st.warning(f"No CSV files found in experiment folder: {selected_experiment}")
        else:
            st.warning("No experiment folders found in data/read/ directory. Please add your experiment folders containing facial landmark CSV files.")
            st.info("Expected folder structure: data/read/experiment_name/*.csv\nExpected CSV format: feat_0_x, feat_0_y, feat_0_z, ... for 478 facial landmarks")
    
    def load_and_preview_csv(self, file_path):
        """Load and preview the selected CSV file."""
        try:
            with st.spinner("Loading CSV file..."):
                df = pd.read_csv(file_path)
                
                # Check if Time (s) column exists and sort by it
                if 'Time (s)' in df.columns:
                    original_order = df.index.tolist()
                    df = df.sort_values('Time (s)').reset_index(drop=True)
                    
                    # Check if sorting changed the order
                    if df.index.tolist() != original_order:
                        st.info("📊 Data has been automatically sorted by Time (s) column")
                
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
                st.subheader("First 5 frames (sorted by time)")
                preview_df = df.head()
                
                # If Time (s) column exists, highlight it in preview
                if 'Time (s)' in df.columns:
                    # Create a styled dataframe that highlights the Time column
                    st.dataframe(preview_df, use_container_width=True)
                    
                    # Show time range info
                    time_col = df['Time (s)']
                    st.info(f"⏱️ Time range: {time_col.min():.3f}s to {time_col.max():.3f}s (Duration: {time_col.max() - time_col.min():.3f}s)")
                else:
                    st.dataframe(preview_df, use_container_width=True)
                
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
            
            # Baseline frames configuration
            baseline_frames = st.number_input(
                "Baseline Frames for Alignment",
                min_value=1,
                max_value=100,
                value=30,
                help="Number of initial frames to average for stable baseline (more frames = more stable, but slower processing)"
            )
            
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
            st.session_state.baseline_frames = baseline_frames
            
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
                    baseline_frame_count=st.session_state.baseline_frames
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
                temp_dir, config_path, ply_paths = FileManager.save_animation_frames(frames_data, str(save_path))
                
                # Create metadata file
                metadata = {
                    'source_file': st.session_state.csv_file_path.name,
                    'num_frames': len(frames_data),
                    'num_landmarks': len(frames_data[0]['points']),
                    'color_mode': st.session_state.color_mode,
                    'z_scale': st.session_state.z_scale,
                    'baseline_frames': st.session_state.baseline_frames,
                    'fps': st.session_state.animation_fps,
                    'created_at': datetime.now().isoformat(),
                    'kabsch_aligned': True,  # Always true in refactored version
                }
                
                metadata_path = save_path / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
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
                colors = np.zeros((len(displacement), 3))
                for j, intensity in enumerate(normalized):
                    if intensity < 0.25:  # Very low movement - blue to cyan
                        colors[j] = [0, intensity*4, 1.0]
                    elif intensity < 0.5:  # Low movement - cyan to green
                        t = (intensity - 0.25) * 4
                        colors[j] = [0, 1.0, 1.0 - t]
                    elif intensity < 0.75:  # Medium movement - green to yellow
                        t = (intensity - 0.5) * 4
                        colors[j] = [t, 1.0, 0]
                    else:  # High movement - yellow to red
                        t = (intensity - 0.75) * 4
                        colors[j] = [1.0, 1.0 - t, 0]
                
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
                f"Frame (1-{len(frames_data)})", 
                0, len(frames_data)-1, 
                st.session_state.current_frame_idx
            )
            st.session_state.current_frame_idx = frame_idx
            
            # Display current frame
            frame_data = frames_data[frame_idx]
            fig = PointCloudVisualizer.create_preview_plot(
                frame_data['points'],
                frame_data['colors'],
                title_prefix=f"Frame {frame_idx + 1}/{len(frames_data)}"
            )
            st.pyplot(fig)
            plt.close(fig)  # Clean up memory
        
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
        """Render the Analysis tab for data merging and analysis."""
        st.header("Analysis")
        
        # Create tabs within Analysis
        analysis_tabs = st.tabs(["Merge and Import", "Feature Analysis", "Model Training"])
        
        with analysis_tabs[0]:
            self.render_merge_and_import()
        with analysis_tabs[1]:
            self.render_feature_analysis()
        with analysis_tabs[2]:
            self.render_model_training()
    
    def render_merge_and_import(self):
        """Render the merge and import interface with side-by-side folder views."""
        st.subheader("Merge and Import")
        
        # Get the currently selected experiment path from session state
        current_experiment = None
        if st.session_state.csv_file_path:
            current_experiment = Path(st.session_state.csv_file_path).parent
        
        # Create side-by-side columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### READ")
            if current_experiment:
                st.caption(f"📂 {current_experiment}")
                
                # List contents of read directory
                try:
                    files = sorted(current_experiment.glob("*.csv"))
                    if files:
                        st.markdown("#### CSV Files:")
                        for file in files:
                            st.text(f"📄 {file.name}")
                    else:
                        st.info("No CSV files found in directory")
                except Exception as e:
                    st.error(f"Error reading directory: {str(e)}")
            else:
                st.info("Please select an experiment in the Import tab first")
        
        with col2:
            st.markdown("### WRITE")
            if current_experiment:
                # Create matching write directory path
                write_dir = self.data_write_dir / current_experiment.name
                st.caption(f"📂 {write_dir}")
                
                # Create directory if it doesn't exist
                write_dir.mkdir(parents=True, exist_ok=True)
                
                # List contents of write directory
                try:
                    # Look for processed files (animations, videos, etc.)
                    processed_files = []
                    processed_files.extend(write_dir.glob("*.mp4"))  # Videos
                    processed_files.extend(write_dir.glob("*.ply"))  # Point clouds
                    processed_files.extend(write_dir.glob("*.json")) # Metadata
                    
                    if processed_files:
                        st.markdown("#### Processed Files:")
                        for file in sorted(processed_files):
                            icon = "🎥" if file.suffix == ".mp4" else "📄"
                            st.text(f"{icon} {file.name}")
                    else:
                        st.info("No processed files yet")
                except Exception as e:
                    st.error(f"Error reading directory: {str(e)}")
            else:
                st.info("Waiting for experiment selection...")
    
    def render_feature_analysis(self):
        """Render the feature analysis interface (placeholder)."""
        st.info("🚧 Feature analysis coming soon...")
        st.markdown("""
        Planned features:
        - Movement pattern analysis
        - Statistical summaries
        - Feature extraction
        """)
    
    def render_model_training(self):
        """Render the model training interface (placeholder)."""
        st.info("🚧 Model training coming soon...")
        st.markdown("""
        Planned features:
        - Trial type prediction
        - Cross-validation
        - Model evaluation
        """)


def main():
    """Main entry point."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 