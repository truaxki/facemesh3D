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
import threading
from pathlib import Path
from datetime import datetime
from file_manager import FileManager
from desktop_launcher import DesktopLauncher
from data_filters import DataFilters


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
            'head_movement_compensation': 'kabsch'  # New default setting
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def run(self):
        """Main application entry point."""
        st.title("🎭 Facial Microexpression Analysis")
        
        # Determine which tab should be active based on state
        if hasattr(st.session_state, 'current_experiment') and st.session_state.current_experiment:
            default_tab = 1  # Animation tab
        else:
            default_tab = 0  # Import tab
        
        # Create tabs
        tabs = st.tabs(["Import", "Animation", "Analysis"])
        
        with tabs[0]:
            self.render_import_tab()
        
        with tabs[1]:
            self.render_animation_tab()
        
        with tabs[2]:
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
                st.session_state.current_experiment = experiment_path
                st.success(f"✅ Selected experiment: {selected_experiment}\n\nGo to the Animation tab to select a test and create visualization.")
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
        
        if not hasattr(st.session_state, 'current_experiment'):
            st.warning("Please select an experiment in the Import tab first.")
            return
            
        experiment_path = st.session_state.current_experiment
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
            
            # Test selection dropdown (full width)
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
                
                # Load CSV silently
                try:
                    df = pd.read_csv(file_path)
                    st.session_state.csv_data = df
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
                    return
            
            # Always set these defaults even if settings are hidden
            if 'baseline_frames' not in st.session_state:
                st.session_state.baseline_frames = 30
            if 'color_mode' not in st.session_state:
                st.session_state.color_mode = 'local_movement'
            if 'head_movement_compensation' not in st.session_state:
                st.session_state.head_movement_compensation = 'kabsch'
            st.session_state.z_scale = 25.0  # Always use 25x
            
            # Create animation button - only show if data is loaded
            if st.session_state.csv_data is not None:
                if st.button("🎬 Create Facial Animation", type="primary", use_container_width=True):
                    self.create_animation()
        
        # Main area - animation display
        if st.session_state.animation_created and st.session_state.frames_data:
            st.success("✅ Animation created successfully!\n\nThe interactive 3D viewer has been launched in a separate window.")
            
            # Add cluster analysis section
            st.markdown("---")
            if st.button("📊 Analyze Facial Cluster Movements", type="secondary", use_container_width=True, key="analyze_clusters_btn"):
                with st.spinner("Analyzing facial clusters..."):
                    cluster_results = DataFilters.analyze_all_clusters(st.session_state.frames_data)
                    st.session_state.cluster_analysis = cluster_results
                    st.session_state.show_cluster_analysis = True
            
            # Display saved analysis if exists
            if hasattr(st.session_state, 'show_cluster_analysis') and st.session_state.show_cluster_analysis:
                self.display_cluster_analysis_results()
            
            # Check if we need to launch the viewer
            if hasattr(st.session_state, 'launch_viewer_pending') and st.session_state.launch_viewer_pending:
                st.session_state.launch_viewer_pending = False
                
                # Capture data before thread
                frames_data = st.session_state.frames_data
                animation_fps = st.session_state.animation_fps
                
                # Launch viewer in background
                def launch_viewer():
                    success, message = DesktopLauncher.launch_interactive_animation_player(
                        frames_data, 
                        animation_fps
                    )
                    if not success:
                        print(f"Failed to launch viewer: {message}")
                
                viewer_thread = threading.Thread(target=launch_viewer)
                viewer_thread.daemon = True
                viewer_thread.start()
                
        else:
            if st.session_state.csv_data is None:
                st.info("Select a test above to begin.")
        
        # Settings footer (expandable) - always at the bottom
        if hasattr(st.session_state, 'current_experiment'):
            with st.expander("⚙️ Advanced Settings", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input(
                        "Baseline Frames for Alignment",
                        min_value=1,
                        max_value=100,
                        value=30,
                        key='baseline_frames',
                        help="Number of initial frames to average for stable baseline"
                    )
                    
                    st.radio(
                        "Head Movement Compensation",
                        options=['off', 'kabsch', 'kabsch_umeyama'],
                        key='head_movement_compensation',
                        format_func=lambda x: {
                            'off': 'Off (No compensation)',
                            'kabsch': 'Rotation & Translation (Kabsch)',
                            'kabsch_umeyama': 'Rotation, Translation & Scale (Kabsch-Umeyama)'
                        }[x],
                        help="Method for removing head movement to isolate facial expressions"
                    )
                    
                with col2:
                    st.selectbox(
                        "Color Mode",
                        ["local_movement", "single"],
                        key='color_mode',
                        format_func=lambda x: {
                            "local_movement": "Local Movement (Microexpressions)",
                            "single": "Single Color"
                        }[x],
                        help="Local Movement highlights facial movements after head motion removal"
                    )
    
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
                
                # Apply selected head movement compensation
                if st.session_state.head_movement_compensation != 'off':
                    if st.session_state.head_movement_compensation == 'kabsch':
                        status_text.text("Applying Kabsch alignment to remove head motion...")
                        frames_data = DataFilters.align_frames_to_baseline(
                            frames_data, 
                            baseline_frame_count=st.session_state.baseline_frames
                        )
                    elif st.session_state.head_movement_compensation == 'kabsch_umeyama':
                        status_text.text("Applying Kabsch-Umeyama alignment to remove head motion and scaling...")
                        frames_data = DataFilters.align_frames_to_baseline_umeyama(
                            frames_data, 
                            baseline_frame_count=st.session_state.baseline_frames
                        )
                else:
                    status_text.text("No head movement compensation applied...")
                
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
                    'head_movement_compensation': st.session_state.head_movement_compensation,
                    'kabsch_aligned': st.session_state.head_movement_compensation != 'off'
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
                st.info("Launching interactive 3D viewer...")
                
                # Set flag to launch viewer after rerun
                st.session_state.launch_viewer_pending = True
                
                # Force UI update before launching viewer
                st.rerun()
                
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
    
    def display_cluster_analysis_results(self):
        """Display cluster analysis results from stored session state."""
        if not hasattr(st.session_state, 'cluster_analysis'):
            return
            
        cluster_results = st.session_state.cluster_analysis
        
        st.subheader("🔬 Facial Cluster Movement Analysis")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Individual Clusters", "Cluster Groups", "Comparison"])
        
        with tab1:
            st.write("### Movement by Individual Facial Clusters")
            
            # Sort clusters by total movement
            sorted_clusters = sorted(
                [(k, v) for k, v in cluster_results.items() if not k.startswith('GROUP_')],
                key=lambda x: x[1]['total_movement'],
                reverse=True
            )
            
            # Display top movers
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Active Clusters:**")
                for i, (name, stats) in enumerate(sorted_clusters[:10]):
                    st.write(f"{i+1}. **{name}**: {stats['total_movement']:.2f} total movement")
                    st.write(f"   - Mean: {stats['mean_movement']:.4f}")
                    st.write(f"   - Max: {stats['max_movement']:.4f}")
            
            with col2:
                st.write("**Least Active Clusters:**")
                for i, (name, stats) in enumerate(sorted_clusters[-10:][::-1]):
                    st.write(f"{i+1}. **{name}**: {stats['total_movement']:.2f} total movement")
                    st.write(f"   - Mean: {stats['mean_movement']:.4f}")
                    st.write(f"   - Max: {stats['max_movement']:.4f}")
        
        with tab2:
            st.write("### Movement by Cluster Groups")
            
            # Get group results
            group_results = [(k, v) for k, v in cluster_results.items() if k.startswith('GROUP_')]
            sorted_groups = sorted(group_results, key=lambda x: x[1]['total_movement'], reverse=True)
            
            # Create bar chart data
            import pandas as pd
            
            group_data = pd.DataFrame([
                {
                    'Group': name.replace('GROUP_', ''),
                    'Total Movement': stats['total_movement'],
                    'Mean Movement': stats['mean_movement'],
                    'Landmarks': stats['num_landmarks']
                }
                for name, stats in sorted_groups
            ])
            
            st.bar_chart(group_data.set_index('Group')['Total Movement'])
            
            # Display detailed stats
            for name, stats in sorted_groups:
                group_name = name.replace('GROUP_', '')
                with st.expander(f"📊 {group_name.title()} Details"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Movement", f"{stats['total_movement']:.2f}")
                    with col2:
                        st.metric("Mean Movement", f"{stats['mean_movement']:.4f}")
                    with col3:
                        st.metric("Landmarks", stats['num_landmarks'])
        
        with tab3:
            st.write("### Alignment Method Comparison")
            
            if st.button("🔬 Compare Alignment Methods", key="compare_alignment_methods_display_btn"):
                with st.spinner("Comparing alignment methods..."):
                    # Need to get original unaligned frames for comparison
                    # Re-parse the CSV to get original frames
                    df = st.session_state.csv_data
                    
                    # Get coordinate columns
                    x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
                    y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
                    z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
                    
                    num_frames = len(df)
                    num_landmarks = len(x_cols)
                    
                    original_frames = []
                    
                    # Recreate original frames
                    for i in range(num_frames):
                        points = np.zeros((num_landmarks, 3))
                        for j in range(num_landmarks):
                            points[j] = [
                                df[x_cols[j]].iloc[i],
                                df[y_cols[j]].iloc[i],
                                df[z_cols[j]].iloc[i] * st.session_state.z_scale
                            ]
                        
                        original_frames.append({
                            'points': points,
                            'colors': None
                        })
                    
                    comparison = DataFilters.compare_alignment_methods(
                        original_frames, 
                        baseline_frame_count=st.session_state.baseline_frames
                    )
                
                # Display comparison results
                st.write("#### Movement Reduction by Method:")
                
                baseline = comparison['no_alignment']['total_movement']
                
                comparison_df = pd.DataFrame([
                    {
                        'Method': 'No Alignment',
                        'Total Movement': baseline,
                        'Reduction %': 0
                    },
                    {
                        'Method': 'Kabsch',
                        'Total Movement': comparison['kabsch']['total_movement'],
                        'Reduction %': (1 - comparison['kabsch']['total_movement']/baseline) * 100
                    },
                    {
                        'Method': 'Kabsch-Umeyama',
                        'Total Movement': comparison['kabsch_umeyama']['total_movement'],
                        'Reduction %': (1 - comparison['kabsch_umeyama']['total_movement']/baseline) * 100
                    }
                ])
                
                st.dataframe(comparison_df)
                
                # Store comparison in session state
                st.session_state.alignment_comparison = comparison
    
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
        current_experiment = getattr(st.session_state, 'current_experiment', None)
        
        # Create side-by-side columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### READ")
            if current_experiment:
                st.caption(f"📂 {current_experiment}")
                
                # List contents of read directory with selection
                try:
                    files = sorted(current_experiment.glob("*.csv"))
                    if files:
                        st.markdown("#### CSV Files:")
                        selected_files = []
                        for file in files:
                            if st.checkbox(f"📄 {file.name}", key=f"read_{file.name}"):
                                selected_files.append(file)
                        
                        if selected_files:
                            st.session_state.selected_read_files = selected_files
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
                
                # List contents of write directory with selection
                try:
                    # Look for processed files (animations, videos, etc.)
                    processed_files = []
                    processed_files.extend(write_dir.glob("*.mp4"))  # Videos
                    processed_files.extend(write_dir.glob("*.ply"))  # Point clouds
                    processed_files.extend(write_dir.glob("*.json")) # Metadata
                    
                    if processed_files:
                        st.markdown("#### Processed Files:")
                        selected_files = []
                        for file in sorted(processed_files):
                            icon = "🎥" if file.suffix == ".mp4" else "📄"
                            if st.checkbox(f"{icon} {file.name}", key=f"write_{file.name}"):
                                selected_files.append(file)
                        
                        if selected_files:
                            st.session_state.selected_write_files = selected_files
                    else:
                        st.info("No processed files yet")
                except Exception as e:
                    st.error(f"Error reading directory: {str(e)}")
            else:
                st.info("Waiting for experiment selection...")
        
        # Show data preview for selected files
        if hasattr(st.session_state, 'selected_read_files') and st.session_state.selected_read_files:
            with st.expander("Preview Selected Data", expanded=True):
                for file in st.session_state.selected_read_files:
                    st.markdown(f"#### {file.name}")
                    try:
                        df = pd.read_csv(file)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows (Frames)", len(df))
                        with col2:
                            st.metric("Columns", len(df.columns))
                        with col3:
                            coord_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith(('_x', '_y', '_z'))]
                            num_landmarks = len(coord_cols) // 3
                            st.metric("Facial Landmarks", num_landmarks)
                        
                        # Show first few rows
                        st.dataframe(df.head(), use_container_width=True)
                        
                        # Show time range if available
                        if 'Time (s)' in df.columns:
                            time_col = df['Time (s)']
                            st.info(f"⏱️ Time range: {time_col.min():.3f}s to {time_col.max():.3f}s (Duration: {time_col.max() - time_col.min():.3f}s)")
                    except Exception as e:
                        st.error(f"Error loading {file.name}: {str(e)}")
    
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