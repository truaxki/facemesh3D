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
        """Initialize the Streamlit interface."""
        self.setup_page_config()
        self.setup_directories()
        self.init_session_state()
    
    def setup_page_config(self):
        st.set_page_config(
            page_title="Facial Microexpression Analysis",
            page_icon="🎭",
            layout="wide"
        )
    
    def setup_directories(self):
        """Ensure data directories exist."""
        self.data_read_dir = Path("data/read")
        self.data_write_dir = Path("data/write")
        self.data_read_dir.mkdir(parents=True, exist_ok=True)
        self.data_write_dir.mkdir(parents=True, exist_ok=True)
    
    def init_session_state(self):
        """Initialize session state variables."""
        defaults = {
            'csv_data': None,
            'csv_file_path': None,
            'baseline_mode': 'first_frame',  # Default to first frame mode
            'statistical_baseline': None,
            'baseline_csv_path': None,
            'color_mode': 'local_movement',
            'enable_scaling': True,
            'current_animation': None,
            'frames_data': None,  # Store animation frames for interactive player
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
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
        """Render the Import tab for CSV file selection."""
        st.header("Import Facial Landmark Data")
        
        # Get available CSV files
        csv_files = list(self.data_read_dir.glob("*.csv"))
        
        if not csv_files:
            st.warning(f"No CSV files found in `{self.data_read_dir}`")
            st.info("Place your facial landmark CSV files in the `data/read/` directory.")
            return
        
        # File selection
        file_names = [f.name for f in csv_files]
        selected_file = st.selectbox(
            "Select CSV file:",
            file_names,
            help="Choose a facial landmark CSV file to import"
        )
        
        if selected_file:
            file_path = self.data_read_dir / selected_file
            
            # Load and preview if different file selected
            if st.session_state.csv_file_path != file_path:
                st.session_state.csv_file_path = file_path
                self.load_and_preview_csv(file_path)
        
        # Baseline Configuration Section
        if st.session_state.csv_data is not None:
            st.markdown("---")
            st.subheader("🎯 Baseline Configuration")
            st.info("The baseline determines the reference frame for Kabsch alignment (head motion removal)")
            
            # Baseline mode selection
            baseline_mode = st.radio(
                "Baseline Mode:",
                ["first_frame", "custom_csv"],
                format_func=lambda x: {
                    "first_frame": "First Frame (Default) - Use first frame of current data",
                    "custom_csv": "Custom Statistical Baseline - Use mean from separate CSV file"
                }[x],
                help="Choose how to define the baseline for alignment"
            )
            st.session_state.baseline_mode = baseline_mode
            
            if baseline_mode == "custom_csv":
                st.markdown("#### Custom Baseline CSV")
                
                # Baseline CSV file selection
                baseline_file_names = [f.name for f in csv_files]
                selected_baseline_file = st.selectbox(
                    "Select baseline CSV file:",
                    baseline_file_names,
                    help="Choose a CSV file to generate statistical baseline from"
                )
                
                if selected_baseline_file:
                    baseline_file_path = self.data_read_dir / selected_baseline_file
                    
                    # Generate statistical baseline button
                    if st.button("📊 Generate Statistical Baseline", type="secondary"):
                        with st.spinner("Generating statistical baseline..."):
                            try:
                                statistical_baseline = DataFilters.create_statistical_baseline_from_csv(
                                    str(baseline_file_path),
                                    z_scale=25.0
                                )
                                st.session_state.baseline_csv_path = baseline_file_path
                                st.session_state.statistical_baseline = statistical_baseline
                                
                                st.success("✅ Statistical baseline generated successfully!")
                                
                                # Display baseline statistics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Source Frames", statistical_baseline['num_frames'])
                                with col2:
                                    st.metric("Landmarks", statistical_baseline['num_landmarks'])
                                with col3:
                                    st.metric("Mean Std Dev", f"{statistical_baseline['statistics']['mean_std_dev']:.4f}")
                                
                                # Show coordinate ranges
                                with st.expander("Baseline Statistics", expanded=False):
                                    stats = statistical_baseline['statistics']
                                    st.write("**Coordinate Ranges:**")
                                    st.write(f"- X: {stats['coordinate_range']['x'][0]:.3f} to {stats['coordinate_range']['x'][1]:.3f}")
                                    st.write(f"- Y: {stats['coordinate_range']['y'][0]:.3f} to {stats['coordinate_range']['y'][1]:.3f}")
                                    st.write(f"- Z: {stats['coordinate_range']['z'][0]:.3f} to {stats['coordinate_range']['z'][1]:.3f}")
                                    st.write(f"**Standard Deviation Range:** {stats['min_std_dev']:.4f} to {stats['max_std_dev']:.4f}")
                                
                            except Exception as e:
                                st.error(f"Error generating statistical baseline: {str(e)}")
                
                # Show current baseline status
                if st.session_state.statistical_baseline is not None:
                    baseline_info = st.session_state.statistical_baseline
                    st.success(f"✅ Statistical baseline ready from {baseline_info['num_frames']} frames")
                    st.caption(f"Source: {Path(baseline_info['source_file']).name}")
                else:
                    st.warning("⚠️ Click 'Generate Statistical Baseline' to create custom baseline")
            
            else:
                # First frame mode - clear any custom baseline
                st.session_state.baseline_csv_path = None
                st.session_state.statistical_baseline = None
                st.info("✅ Using first frame of current data as baseline (default behavior)")
        
        # Show current status
        if st.session_state.csv_data is not None:
            st.markdown("---")
            st.success("📁 Data loaded and ready for animation creation!")
            st.info("Go to the **Animation** tab to create your visualization.")
    
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
            
            # Preview data (expanded by default)
            with st.expander("Preview Data", expanded=True):
                # Show first few rows
                st.subheader("First 5 frames")
                preview_df = df.head()
                st.dataframe(preview_df, use_container_width=True)
                
                # Show time info if available
                if 'Time (s)' in df.columns:
                    time_col = df['Time (s)']
                    st.caption(f"⏱️ Duration: {time_col.max() - time_col.min():.2f}s")
            
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
            
            # Color mode selection 
            color_mode_options = ["local_movement", "single"]
            color_mode_labels = {
                "local_movement": "Movement Heatmap",
                "single": "Single Color"
            }
            
            # Add statistical deviation option if statistical baseline is available
            if (st.session_state.baseline_mode == 'custom_csv' and 
                st.session_state.statistical_baseline is not None):
                color_mode_options.insert(1, "statistical_deviation")
                color_mode_labels["statistical_deviation"] = "Statistical Deviation"
            
            color_mode = st.selectbox(
                "Color Mode",
                color_mode_options,
                format_func=lambda x: color_mode_labels[x]
            )
            st.session_state.color_mode = color_mode
            
            # Show color scheme explanation only if needed
            if color_mode == "statistical_deviation":
                st.caption("🔵 Normal • 🟡 Elevated • 🔴 Extreme")
            
            # Alignment settings
            st.markdown("---")
            st.subheader("Alignment")
            
            # Scaling option
            enable_scaling = st.checkbox(
                "Size Normalization",
                value=True,
                help="Remove size differences between subjects"
            )
            st.session_state.enable_scaling = enable_scaling
            
            if enable_scaling:
                st.caption("✅ Kabsch-Umeyama (with scaling)")
            else:
                st.caption("📌 Kabsch only (no scaling)")
            
            # Show baseline status
            st.markdown("---")
            st.subheader("Baseline")
            if st.session_state.baseline_mode == 'custom_csv':
                if st.session_state.statistical_baseline is not None:
                    st.success("📊 Custom Statistical")
                    baseline_info = st.session_state.statistical_baseline
                    st.caption(f"{Path(baseline_info['source_file']).name}")
                else:
                    st.warning("⚠️ Generate Statistical Baseline First")
                    st.caption("Go to Import tab")
            else:
                st.info("📌 First Frame")
                st.caption("Using first frame of data")
            
            # Create animation button
            st.markdown("---")
            if st.button("🎬 Create Animation", type="primary", use_container_width=True):
                self.create_animation()
        
        # Main area - animation display
        if st.session_state.current_animation:
            self.render_animation_viewer()
        else:
            st.info("Click '🎬 Create Animation' in the sidebar to generate the animation.")
    
    def create_animation(self):
        """Create animation with current settings."""
        if st.session_state.csv_data is None:
            st.error("No CSV data loaded")
            return
        
        try:
            with st.spinner("Creating animation..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Parse facial landmarks from CSV
                status_text.text("Parsing facial landmarks...")
                df = st.session_state.csv_data
                
                # Convert color mode mapping
                color_mode_map = {
                    'local_movement': 'movement',
                    'single': 'single',
                    'statistical_deviation': 'single'  # Will be overridden later
                }
                
                file_color_mode = color_mode_map.get(st.session_state.color_mode, 'movement')
                frames_data = FileManager._parse_facial_landmark_csv(df, file_color_mode, z_scale=25.0)
                
                if not frames_data:
                    st.error("No valid frames found in CSV data")
                    return
                
                progress_bar.progress(0.3)
                
                # Apply Kabsch alignment
                status_text.text("Applying Kabsch alignment to remove head motion...")
                
                if st.session_state.baseline_mode == 'custom_csv':
                    if st.session_state.statistical_baseline is not None:
                        # Use statistical baseline
                        frames_data = DataFilters.align_frames_to_statistical_baseline(
                            frames_data, 
                            st.session_state.statistical_baseline,
                            enable_scaling=st.session_state.enable_scaling
                        )
                        baseline_info = {
                            'type': 'statistical',
                            'source': 'custom',
                            'num_baseline_frames': st.session_state.statistical_baseline['num_frames'],
                            'scaling_enabled': st.session_state.enable_scaling,
                            'algorithm': 'Kabsch-Umeyama' if st.session_state.enable_scaling else 'Kabsch'
                        }
                    else:
                        st.error("Statistical baseline not found")
                        return
                else:
                    # Use first frame baseline
                    frames_data = DataFilters.align_frames_to_baseline(
                        frames_data, 
                        baseline_frame_idx=0,
                        enable_scaling=st.session_state.enable_scaling
                    )
                    baseline_info = {
                        'type': 'first_frame',
                        'baseline_frame_idx': 0,
                        'scaling_enabled': st.session_state.enable_scaling,
                        'algorithm': 'Kabsch-Umeyama' if st.session_state.enable_scaling else 'Kabsch'
                    }
                
                progress_bar.progress(0.6)
                
                # Apply coloring based on mode
                status_text.text("Applying color scheme...")
                if st.session_state.color_mode == 'local_movement':
                    frames_data = self.apply_local_movement_coloring(frames_data)
                elif (st.session_state.color_mode == 'statistical_deviation' and 
                      st.session_state.baseline_mode == 'custom_csv' and 
                      st.session_state.statistical_baseline is not None):
                    frames_data = DataFilters.generate_statistical_deviation_colors(
                        frames_data, 
                        st.session_state.statistical_baseline
                    )
                else:
                    # Single color mode
                    for frame in frames_data:
                        frame['colors'] = np.tile([0.5, 0.7, 1.0], (len(frame['points']), 1))
                
                progress_bar.progress(0.8)
                
                # Generate animation name and save location
                source_name = st.session_state.csv_file_path.stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                animation_name = f"{source_name}_{len(frames_data)}frames_{timestamp}"
                
                save_path = self.data_write_dir / animation_name
                save_path.mkdir(exist_ok=True)
                
                # Save animation frames
                status_text.text("Saving animation frames...")
                temp_dir, config_path, ply_paths = FileManager.save_animation_frames(frames_data, str(save_path))
                
                # Create enhanced metadata file
                metadata = {
                    'source_file': st.session_state.csv_file_path.name,
                    'num_frames': len(frames_data),
                    'num_landmarks': len(frames_data[0]['points']),
                    'color_mode': st.session_state.color_mode,
                    'z_scale': 25.0,
                    'created_at': datetime.now().isoformat(),
                    'baseline_info': baseline_info
                }
                
                metadata_path = save_path / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                progress_bar.progress(1.0)
                status_text.empty()
                
                # Store animation data for viewer
                st.session_state.current_animation = config_path
                st.session_state.frames_data = frames_data  # Store frames for interactive player
                st.success(f"✅ Animation created: {animation_name}")
                
        except Exception as e:
            st.error(f"Animation creation failed: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")
    
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
        """Render the animation viewer section."""
        if st.session_state.current_animation is None:
            st.info("No animation created yet. Create one in the sidebar!")
            return
        
        if st.session_state.frames_data is None:
            st.warning("Animation data not available in memory. Please recreate the animation.")
            return
        
        animation_path = Path(st.session_state.current_animation)
        if not animation_path.exists():
            st.error("Animation file not found")
            return
        
        st.success(f"🎬 Animation ready: {animation_path.name}")
        st.info(f"📊 {len(st.session_state.frames_data)} frames loaded in memory")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎮 Launch 3D Player", use_container_width=True):
                try:
                    if st.session_state.frames_data is not None:
                        # Use interactive animation player with stored frames data
                        success, message = DesktopLauncher.launch_interactive_animation_player(
                            st.session_state.frames_data, fps=15
                        )
                    else:
                        success, message = False, "No animation data available"
                    
                    if success:
                        st.success("✅ 3D player launched!")
                        st.info("**Controls:** SPACE=play/pause • N/P=next/prev • C=toggle axes")
                    else:
                        st.error(f"Launch failed: {message}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("📊 View Metadata", use_container_width=True):
                self.show_animation_metadata(animation_path)
        
        with col3:
            if st.button("📁 Open Folder", use_container_width=True):
                try:
                    import subprocess
                    subprocess.run(['explorer', str(animation_path.parent)], check=True)
                    st.success("✅ Folder opened")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    def show_animation_metadata(self, animation_path):
        """Display animation metadata in an expandable section."""
        metadata_file = animation_path.parent / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                with st.expander("📊 Animation Details", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Frames", metadata.get('num_frames', 'N/A'))
                        st.metric("Landmarks", metadata.get('num_landmarks', 'N/A'))
                        st.metric("Color Mode", metadata.get('color_mode', 'N/A'))
                    
                    with col2:
                        st.metric("Source File", metadata.get('source_file', 'N/A'))
                        baseline_info = metadata.get('baseline_info', {})
                        if baseline_info:
                            baseline_type = baseline_info.get('type', 'unknown')
                            st.metric("Baseline", baseline_type.title())
                            
                            algorithm = baseline_info.get('algorithm', 'Unknown')
                            st.metric("Algorithm", algorithm)
            except Exception as e:
                st.error(f"Error reading metadata: {str(e)}")
        else:
            st.warning("No metadata file found")
    
    def render_analysis_tab(self):
        """Render the Analysis tab for detailed data analysis."""
        st.header("Facial Landmark Analysis")
        
        if st.session_state.csv_data is None:
            st.warning("No data loaded. Please import CSV data first.")
            return
        
        # Analysis content would go here
        st.info("🚧 Analysis features coming soon!")
        st.markdown("""
        **Planned Features:**
        - Frame-by-frame movement analysis
        - Statistical comparison tools  
        - Expression pattern detection
        - Export analysis reports
        """)


def main():
    """Main entry point."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 