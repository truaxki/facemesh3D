"""Streamlit Interface - Refactored for Microexpression Analysis

Streamlined interface focused on facial landmark visualization and analysis.
Three tabs: Import, Animation, Analysis
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
from typing import List, Dict, Any

# Import core functionality modules
from file_manager import FileManager
from desktop_launcher import DesktopLauncher
from data_filters import DataFilters

# Import new modular UI components
from ui_components import StatusSidebar, AdvancedSettings, DataPreview, FilterAnalysisDisplay
from color_processors import ColorProcessor
from session_state_manager import SessionStateManager
from cluster_analysis_ui import ClusterAnalysisUI


class StreamlitInterface:
    """Streamlined Streamlit interface for facial microexpression analysis."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Facial Microexpression Analysis",
            page_icon="🎭",
            layout="wide"
        )
        SessionStateManager.initialize()
        self.setup_directories()
    
    def setup_directories(self):
        """Ensure data directories exist."""
        self.data_read_dir = Path("data/read")
        self.data_write_dir = Path("data/write")
        self.data_read_dir.mkdir(parents=True, exist_ok=True)
        self.data_write_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """Main application entry point."""
        st.title("🎭 Facial Microexpression Analysis")
        
        # Render status sidebar
        StatusSidebar.render()
        
        # Determine which tab should be active based on state
        if SessionStateManager.has('current_experiment'):
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
                SessionStateManager.set('current_experiment', experiment_path)
        else:
            st.warning("No experiment folders found in data/read/ directory. Please add your experiment folders containing facial landmark CSV files.")
            st.info("Expected folder structure: data/read/experiment_name/*.csv\nExpected CSV format: feat_0_x, feat_0_y, feat_0_z, ... for 478 facial landmarks")
    
    def render_animation_tab(self):
        """Render the Animation tab with 2-click system: Select → Analyze → Create."""
        st.header("Facial Animation & Filter Analysis")
        
        if not SessionStateManager.has('current_experiment'):
            st.warning("Please select an experiment in the Import tab first.")
            return
            
        experiment_path = SessionStateManager.get('current_experiment')
        csv_files = list(experiment_path.glob("*.csv"))
        
        if not csv_files:
            st.warning("No CSV files found in the selected experiment.")
            return
        
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
        
        # Test Selection
        st.subheader("🎯 Test Selection")
        selected_test = st.selectbox(
            "Choose test for analysis",
            test_options,
            index=0,
            help="Select the test to analyze. Analysis will run automatically upon selection."
        )
        
        # Get the selected file path
        file_path = next(f for f in csv_files if f.stem == selected_test)
        
        # Check if file changed and reset analysis state
        if file_path != SessionStateManager.get('csv_file_path'):
            SessionStateManager.set('csv_file_path', file_path)
            SessionStateManager.reset_analysis_state()
            
            # Load CSV data
            try:
                df = pd.read_csv(file_path)
                if 'Time (s)' in df.columns:
                    df = df.sort_values('Time (s)').reset_index(drop=True)
                SessionStateManager.set('csv_data', df)
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return
        
        # Comprehensive Analysis (Auto-run)
        if SessionStateManager.get('csv_data') is not None and not SessionStateManager.get('comprehensive_analysis_done'):
            st.subheader("🔬 Analyzing Filter Performance...")
            
            with st.spinner("Analyzing optimal filters and smoothing combinations..."):
                # Parse CSV to frames
                original_frames = self.parse_csv_to_frames(SessionStateManager.get('csv_data'))
                
                # Run comprehensive analysis
                comprehensive_results = DataFilters.comprehensive_alignment_comparison(
                    original_frames, 
                    baseline_frame_count=SessionStateManager.get('baseline_frames')
                )
                
                SessionStateManager.set('comprehensive_analysis', comprehensive_results)
                SessionStateManager.set('original_frames', original_frames)
                SessionStateManager.set('comprehensive_analysis_done', True)
        
        # Show Analysis Results
        if SessionStateManager.get('comprehensive_analysis_done'):
            st.subheader("📊 Filter Performance Results")
            
            # Display comprehensive comparison results
            comprehensive_results = SessionStateManager.get('comprehensive_analysis')
            best_method, best_type, best_overall, best_smoothing, best_window = \
                FilterAnalysisDisplay.show_comprehensive_results(comprehensive_results)
            
            st.info(f"🏆 **Best Filter Combination:** {best_method} with {best_type} ({best_overall:.2f}% movement reduction)")
            
            # Check if current settings match the best combination
            if SessionStateManager.check_optimal_settings(best_method, best_smoothing, best_window):
                st.success("✅ **Current settings match the optimal filter combination!**")
            
            # Create Animation Button
            if st.button("🎬 Create Side-by-Side Animation", type="primary", use_container_width=True):
                self.create_comparison_animation()
        
        # Show animation results if created
        if SessionStateManager.get('animation_created') and SessionStateManager.get('frames_data'):
            st.markdown("---")
            
            # Quick actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Create New Animation", type="secondary", use_container_width=True, key="recreate_btn"):
                    self.create_comparison_animation()
            
            with col2:
                if st.button("📈 View Detailed Analysis", type="secondary", use_container_width=True, key="analysis_btn"):
                    SessionStateManager.set('current_tab', 'Analysis')
                    st.rerun()
        
        # Advanced Settings Footer
        if SessionStateManager.has('current_experiment'):
            st.markdown("---")
            AdvancedSettings.render()
    
    def parse_csv_to_frames(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse CSV dataframe to frames format."""
        x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
        y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
        z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
        
        frames = []
        for i in range(len(df)):
            points = np.zeros((len(x_cols), 3))
            for j in range(len(x_cols)):
                points[j] = [
                    df[x_cols[j]].iloc[i],
                    df[y_cols[j]].iloc[i],
                    df[z_cols[j]].iloc[i] * SessionStateManager.get('z_scale')
                ]
            frames.append({
                'points': points,
                'colors': None
            })
        
        return frames
    
    def create_comparison_animation(self):
        """Create a comparison animation between original and filtered frames."""
        try:
            with st.spinner("Creating comparison animation..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Parse facial landmarks
                status_text.text("Parsing facial landmarks...")
                df = SessionStateManager.get('csv_data')
                
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
                            df[z_cols[j]].iloc[i] * SessionStateManager.get('z_scale')
                        ]
                    
                    frames_data.append({
                        'points': points,
                        'colors': None  # Will be set based on color mode
                    })
                
                # Apply rolling average smoothing if enabled (pre-alignment)
                if SessionStateManager.get('rolling_average_smoothing') == 'pre':
                    status_text.text(f"Applying {SessionStateManager.get('smoothing_window')}-frame rolling average smoothing...")
                    frames_data = DataFilters.apply_rolling_average_smoothing(
                        frames_data, 
                        SessionStateManager.get('smoothing_window')
                    )
                
                # Apply selected head movement compensation
                if SessionStateManager.get('head_movement_compensation') != 'off':
                    if SessionStateManager.get('head_movement_compensation') == 'kabsch':
                        status_text.text("Applying Kabsch alignment to remove head motion...")
                        frames_data = DataFilters.align_frames_to_baseline(
                            frames_data, 
                            baseline_frame_count=SessionStateManager.get('baseline_frames')
                        )
                    elif SessionStateManager.get('head_movement_compensation') == 'kabsch_umeyama':
                        status_text.text("Applying Kabsch-Umeyama alignment to remove head motion with scale...")
                        frames_data = DataFilters.align_frames_to_baseline_umeyama(
                            frames_data, 
                            baseline_frame_count=SessionStateManager.get('baseline_frames')
                        )
                
                # Apply rolling average smoothing if enabled (post-alignment)
                if SessionStateManager.get('rolling_average_smoothing') == 'post':
                    status_text.text(f"Applying {SessionStateManager.get('smoothing_window')}-frame rolling average smoothing...")
                    frames_data = DataFilters.apply_rolling_average_smoothing(
                        frames_data, 
                        SessionStateManager.get('smoothing_window')
                    )
                
                # Apply coloring using the ColorProcessor module
                status_text.text("Applying color mode...")
                frames_data = ColorProcessor.apply_coloring(
                    frames_data,
                    SessionStateManager.get('color_mode'),
                    SessionStateManager.get('baseline_frames')
                )
                
                progress_bar.progress(1.0)
                
                # Generate animation name based on source file
                source_name = SessionStateManager.get('csv_file_path').stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                animation_name = f"{source_name}_{num_frames}frames_{timestamp}"
                
                # Save animation
                save_path = self.data_write_dir / animation_name
                save_path.mkdir(exist_ok=True)
                
                status_text.text("Saving animation frames...")
                temp_dir, config_path, ply_paths = FileManager.save_animation_frames(frames_data, str(save_path))
                
                # Create metadata file
                metadata = {
                    'source_file': SessionStateManager.get('csv_file_path').name,
                    'num_frames': len(frames_data),
                    'num_landmarks': len(frames_data[0]['points']),
                    'color_mode': SessionStateManager.get('color_mode'),
                    'z_scale': SessionStateManager.get('z_scale'),
                    'baseline_frames': SessionStateManager.get('baseline_frames'),
                    'fps': SessionStateManager.get('animation_fps'),
                    'created_at': datetime.now().isoformat(),
                    'head_movement_compensation': SessionStateManager.get('head_movement_compensation'),
                    'kabsch_aligned': SessionStateManager.get('head_movement_compensation') != 'off',
                    'rolling_average_smoothing': SessionStateManager.get('rolling_average_smoothing'),
                    'smoothing_window': SessionStateManager.get('smoothing_window') if SessionStateManager.get('rolling_average_smoothing') != 'off' else None
                }
                
                metadata_path = save_path / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Store in session state
                SessionStateManager.set('frames_data', frames_data)
                SessionStateManager.set('animation_created', True)
                SessionStateManager.set('animation_name', animation_name)
                
                status_text.empty()
                progress_bar.empty()
                
                # Launch comparison viewer directly
                comparison_label = f"Original vs {SessionStateManager.get('head_movement_compensation').title()}"
                if SessionStateManager.get('rolling_average_smoothing') != 'off':
                    comparison_label += f" + {SessionStateManager.get('smoothing_window')}-frame smoothing ({SessionStateManager.get('color_mode').replace('_', ' ').title()})"
                
                success, message = DesktopLauncher.launch_comparison_animation_player(
                    SessionStateManager.get('original_frames'),
                    SessionStateManager.get('frames_data'),
                    SessionStateManager.get('animation_fps'),
                    comparison_label
                )
                
                # Show result in sidebar
                StatusSidebar.show_notification(
                    "🎬 Animation viewer launched!" if success else "❌ Failed to launch viewer",
                    "success" if success else "error"
                )
                if not success:
                    StatusSidebar.show_notification(message, "error")
                
        except Exception as e:
            st.error(f"Error creating animation: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    def render_analysis_tab(self):
        """Render the Analysis tab for data merging and analysis."""
        st.header("Analysis")
        
        # Create tabs within Analysis
        analysis_tabs = st.tabs(["Merge and Import", "Feature Analysis", "Model Training"])
        
        with analysis_tabs[0]:
            self.render_merge_and_import()
        with analysis_tabs[1]:
            ClusterAnalysisUI.render_feature_analysis()
        with analysis_tabs[2]:
            self.render_model_training()
    
    def render_merge_and_import(self):
        """Render the merge and import interface with side-by-side folder views."""
        st.subheader("Merge and Import")
        
        # Get the currently selected experiment path from session state
        current_experiment = SessionStateManager.get('current_experiment')
        
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
                            SessionStateManager.set('selected_read_files', selected_files)
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
                            SessionStateManager.set('selected_write_files', selected_files)
                    else:
                        st.info("No processed files yet")
                except Exception as e:
                    st.error(f"Error reading directory: {str(e)}")
            else:
                st.info("Waiting for experiment selection...")
        
        # Show data preview for selected files
        if SessionStateManager.has('selected_read_files') and SessionStateManager.get('selected_read_files'):
            with st.expander("Preview Selected Data", expanded=True):
                for file in SessionStateManager.get('selected_read_files'):
                    st.markdown(f"#### {file.name}")
                    try:
                        df = pd.read_csv(file)
                        DataPreview.show_csv_preview(df, file)
                    except Exception as e:
                        st.error(f"Error loading {file.name}: {str(e)}")
    
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