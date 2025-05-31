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
from derived_features import DerivedFeatures
from model_training import ModelTraining

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
        """Render the Analysis tab for data processing and feature extraction."""
        st.header("Analysis & Feature Extraction")
        
        # Create tabs within Analysis
        analysis_tabs = st.tabs(["File Overview", "Feature Analysis", "Model Training"])
        
        with analysis_tabs[0]:
            self.render_unified_file_table()
        with analysis_tabs[1]:
            self.render_feature_analysis()
        with analysis_tabs[2]:
            self.render_model_training()
    
    def render_unified_file_table(self):
        """Render the unified file table showing both READ and WRITE files."""
        st.subheader("File Overview")
        
        current_experiment = SessionStateManager.get('current_experiment')
        if not current_experiment:
            st.info("Please select an experiment in the Import tab first")
            return
        
        # Get files from both READ and WRITE directories
        read_dir = current_experiment
        write_dir = self.data_write_dir / current_experiment.name
        write_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all files
        all_files = []
        
        # Read files
        try:
            read_files = list(read_dir.glob("*.csv"))
            for file in read_files:
                df = pd.read_csv(file)
                all_files.append({
                    'File Name': file.name,
                    'Source': 'READ',
                    'Type': 'Raw Data',
                    'Rows': len(df),
                    'Point Features': len([col for col in df.columns if col.startswith('feat_')]) // 3,
                    'Derived Features': 0,  # Raw files have no derived features
                    'Has Time Column': 'Time (s)' in df.columns,
                    'Memory (MB)': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'Path': str(file)
                })
        except Exception as e:
            st.error(f"Error reading READ directory: {str(e)}")
        
        # Write files
        try:
            write_files = list(write_dir.glob("*.csv"))
            for file in write_files:
                try:
                    df = pd.read_csv(file)
                    point_features = len([col for col in df.columns if col.startswith('feat_')]) // 3
                    derived_features = len([col for col in df.columns if not col.startswith('feat_') and 
                                          col not in ['Time (s)', 'source_file', 'frame_index', 'time_seconds']])
                    
                    all_files.append({
                        'File Name': file.name,
                        'Source': 'WRITE',
                        'Type': 'Processed Data',
                        'Rows': len(df),
                        'Point Features': point_features,
                        'Derived Features': derived_features,
                        'Has Time Column': 'Time (s)' in df.columns or 'time_seconds' in df.columns,
                        'Memory (MB)': df.memory_usage(deep=True).sum() / 1024 / 1024,
                        'Path': str(file)
                    })
                except Exception as e:
                    st.warning(f"Could not analyze {file.name}: {str(e)}")
        except Exception as e:
            st.error(f"Error reading WRITE directory: {str(e)}")
        
        if all_files:
            # Convert to DataFrame for display
            files_df = pd.DataFrame(all_files)
            files_df['Memory (MB)'] = files_df['Memory (MB)'].round(2)
            
            # Color code the table based on source
            def color_source(val):
                if val == 'READ':
                    return 'background-color: #e8f4fd; border-left: 4px solid #1f77b4'  # Light blue with border
                elif val == 'WRITE':
                    return 'background-color: #f0f8e8; border-left: 4px solid #2ca02c'  # Light green with border
                return ''
            
            # Display styled table with modern Streamlit styling
            styled_df = files_df.style.map(color_source, subset=['Source'])
            styled_df = styled_df.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', '#262730'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #e6e9ef')]},
                {'selector': 'tr:hover', 'props': [('background-color', '#f8f9fa')]}
            ])
            st.dataframe(styled_df, use_container_width=True)
            
            # Store file information for feature analysis tab
            SessionStateManager.set('available_files_info', files_df.to_dict('records'))
        else:
            st.info("No CSV files found in the experiment directories")
    
    def render_feature_analysis(self):
        """Render the feature analysis interface."""
        st.subheader("Feature Analysis")
        
        # Get the currently selected experiment path from session state
        current_experiment = SessionStateManager.get('current_experiment')
        
        if current_experiment:
            # List available feature analysis methods
            feature_analysis_methods = [
                "Cluster Analysis",
                "Feature Extraction",
                "Feature Comparison"
            ]
            
            # Select feature analysis method
            selected_method = st.selectbox(
                "Select feature analysis method",
                feature_analysis_methods,
                index=0
            )
            
            if selected_method == "Cluster Analysis":
                ClusterAnalysisUI.render_feature_analysis()
            elif selected_method == "Feature Extraction":
                self.render_feature_extraction()
            elif selected_method == "Feature Comparison":
                self.render_feature_comparison()
        else:
            st.warning("Please select an experiment in the Import tab first")
    
    def render_model_training(self):
        """Render the model training interface."""
        st.subheader("Model Training & Evaluation")
        
        # Check if we have available processed files with features
        available_files = SessionStateManager.get('available_files_info', [])
        write_files = [f for f in available_files if f['Source'] == 'WRITE' and f['Derived Features'] > 0]
        
        if not write_files:
            st.warning("⚠️ No processed files with derived features found. Please extract features first in the Feature Analysis tab.")
            st.info("💡 **Next Steps:**\n1. Go to Feature Analysis tab\n2. Select files and extract features\n3. Return here to train models")
            return
        
        # Initialize model trainer
        if 'model_trainer' not in st.session_state:
            st.session_state.model_trainer = ModelTraining()
        
        trainer = st.session_state.model_trainer
        
        # 1. DATA SELECTION
        with st.expander("📊 Select Training Data", expanded=True):
            st.markdown("**Available Feature Files:**")
            
            selected_feature_files = []
            
            for file_info in write_files:
                file_path = file_info['Path']
                file_name = file_info['File Name']
                features_count = file_info['Derived Features']
                samples_count = file_info['Rows']
                
                if st.checkbox(f"📈 {file_name}", 
                             key=f"train_file_{file_name}",
                             value=True,  # Default selected
                             help=f"{features_count} derived features, {samples_count} samples"):
                    selected_feature_files.append(file_path)
            
            if selected_feature_files:
                st.success(f"✅ Selected {len(selected_feature_files)} files for training")
            else:
                st.warning("⚠️ Please select at least one feature file")
                return
        
        # 2. LOAD AND PREVIEW DATA
        if selected_feature_files:
            try:
                with st.spinner("Loading feature data..."):
                    combined_df = trainer.load_extracted_features(selected_feature_files)
                    combined_df = trainer.create_labels_from_filenames(combined_df)
                
                # Store in session state
                st.session_state.training_data = combined_df
                
                # Show data preview
                with st.expander("🔍 Data Preview", expanded=False):
                    st.dataframe(combined_df.head(10), use_container_width=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Samples", len(combined_df))
                    with col2:
                        st.metric("Subjects", len(combined_df['subject'].unique()))
                    with col3:
                        st.metric("Test Types", len(combined_df['test'].unique()))
                    with col4:
                        feature_cols = [col for col in combined_df.columns 
                                      if col.startswith('displacement_') or col.startswith('quaternion_')]
                        st.metric("Features", len(feature_cols))
                
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                return
        
        # 3. CORRELATION ANALYSIS
        st.markdown("---")
        st.subheader("🔗 Correlation Analysis")
        
        if 'training_data' in st.session_state:
            training_data = st.session_state.training_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_target = st.selectbox(
                    "Analysis Target",
                    ["subject", "test"],
                    help="Choose what to predict"
                )
            
            with col2:
                feature_type_for_analysis = st.selectbox(
                    "Feature Type",
                    ["combined", "displacement", "quaternion"],
                    help="Choose features for correlation analysis"
                )
            
            if st.button("🔄 Run Correlation Analysis", type="secondary"):
                try:
                    with st.spinner("Computing correlations..."):
                        # Get feature types
                        feature_types = trainer.separate_feature_types(training_data)
                        
                        # Select features based on type
                        if feature_type_for_analysis == 'displacement':
                            analysis_features = feature_types['displacement']
                        elif feature_type_for_analysis == 'quaternion':
                            analysis_features = feature_types['quaternion']
                        else:  # combined
                            analysis_features = feature_types['displacement'] + feature_types['quaternion']
                        
                        if not analysis_features:
                            st.error(f"No {feature_type_for_analysis} features found!")
                            return
                        
                        # Compute correlations
                        correlation_matrix, feature_names, target_correlations = trainer.compute_correlation_matrix(
                            training_data, analysis_features, analysis_target
                        )
                        
                        # Store results
                        st.session_state.correlation_results = {
                            'matrix': correlation_matrix,
                            'features': feature_names,
                            'target_correlations': target_correlations,
                            'target': analysis_target,
                            'feature_type': feature_type_for_analysis
                        }
                
                except Exception as e:
                    st.error(f"❌ Correlation analysis failed: {str(e)}")
            
            # Display correlation results
            if 'correlation_results' in st.session_state:
                results = st.session_state.correlation_results
                
                # Create correlation plot
                try:
                    fig = trainer.plot_feature_correlations(
                        results['matrix'], 
                        results['features'], 
                        results['target_correlations'],
                        results['target'].title()
                    )
                    st.pyplot(fig)
                    
                    # Show top correlations
                    st.markdown("**🏆 Top Feature Correlations:**")
                    sorted_indices = np.argsort(np.abs(results['target_correlations']))[::-1]
                    top_10 = sorted_indices[:10]
                    
                    correlation_df = pd.DataFrame({
                        'Feature': [results['features'][i] for i in top_10],
                        'Correlation': [results['target_correlations'][i] for i in top_10],
                        'Abs Correlation': [abs(results['target_correlations'][i]) for i in top_10]
                    })
                    
                    st.dataframe(correlation_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error creating correlation plot: {str(e)}")
        
        # 4. MODEL TRAINING
        st.markdown("---")
        st.subheader("🎯 Model Training")
        
        if 'training_data' in st.session_state:
            training_data = st.session_state.training_data
            
            # Training configuration
            col1, col2, col3 = st.columns(3)
            
            with col1:
                model_type = st.selectbox(
                    "Model Type",
                    ["displacement", "quaternion", "combined"],
                    index=2,  # Default to combined
                    help="Choose which features to use for training"
                )
            
            with col2:
                prediction_target = st.selectbox(
                    "Prediction Target",
                    ["subject", "test"],
                    help="Choose what the model should predict"
                )
            
            with col3:
                test_size = st.slider(
                    "Test Split",
                    0.1, 0.5, 0.2,
                    help="Fraction of data for testing"
                )
            
            # Train button
            if st.button("🚀 Train Models", type="primary", use_container_width=True):
                try:
                    with st.spinner("Training models... This may take a few minutes."):
                        # Progress tracking
                        progress_text = st.empty()
                        progress_text.text("🔄 Preparing data and training models...")
                        
                        # Train the model pipeline
                        training_results = trainer.train_model_pipeline(
                            training_data,
                            model_type=model_type,
                            target=prediction_target,
                            test_size=test_size,
                            random_state=42
                        )
                        
                        # Store results
                        st.session_state.training_results = training_results
                        st.session_state.current_model_key = f"{model_type}_{prediction_target}"
                        
                        progress_text.empty()
                        st.balloons()
                        st.success(f"🎉 Training completed! Best model: {training_results['best_model']}")
                
                except Exception as e:
                    st.error(f"❌ Training failed: {str(e)}")
                    with st.expander("🔍 Error Details"):
                        import traceback
                        st.code(traceback.format_exc())
        
        # 5. RESULTS DISPLAY
        if 'training_results' in st.session_state:
            st.markdown("---")
            st.subheader("📈 Training Results")
            
            results = st.session_state.training_results
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Best Model", results['best_model'])
            with col2:
                st.metric("Test Accuracy", f"{results['best_accuracy']:.3f}")
            with col3:
                st.metric("Features Used", results['selected_feature_count'])
            with col4:
                st.metric("Training Samples", results['train_samples'])
            
            # Detailed results for each model
            st.markdown("**🔍 Model Comparison:**")
            
            comparison_data = []
            for model_name, model_results in results['results'].items():
                comparison_data.append({
                    'Model': model_name,
                    'Train Accuracy': f"{model_results['train_accuracy']:.3f}",
                    'Test Accuracy': f"{model_results['test_accuracy']:.3f}",
                    'CV Mean': f"{model_results['cv_mean']:.3f}",
                    'CV Std': f"{model_results['cv_std']:.3f}"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Confusion matrices
            st.markdown("**🎯 Confusion Matrices:**")
            
            # Create tabs for each model
            model_tabs = st.tabs(list(results['results'].keys()))
            
            for i, (model_name, tab) in enumerate(zip(results['results'].keys(), model_tabs)):
                with tab:
                    model_results = results['results'][model_name]
                    cm = model_results['confusion_matrix']
                    
                    # Get class names
                    if st.session_state.model_trainer.label_encoders[st.session_state.current_model_key]:
                        class_names = st.session_state.model_trainer.label_encoders[st.session_state.current_model_key].classes_
                    else:
                        class_names = [str(i) for i in range(cm.shape[0])]
                    
                    # Create confusion matrix plot
                    try:
                        fig = trainer.plot_confusion_matrix(
                            cm, 
                            class_names, 
                            title=f"{model_name} - {results['model_type'].title()} Model ({prediction_target.title()} Prediction)"
                        )
                        st.pyplot(fig)
                        
                        # Classification report
                        with st.expander(f"📊 {model_name} Classification Report"):
                            class_report = model_results['classification_report']
                            report_df = pd.DataFrame(class_report).transpose()
                            st.dataframe(report_df, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"❌ Error creating confusion matrix for {model_name}: {str(e)}")
            
            # Save models option
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save Trained Models", type="secondary"):
                    try:
                        save_dir = f"models/{results['model_type']}_{prediction_target}"
                        trainer.save_models(save_dir)
                        st.success(f"✅ Models saved to {save_dir}/")
                    except Exception as e:
                        st.error(f"❌ Error saving models: {str(e)}")
            
            with col2:
                if st.button("🔄 Train Different Configuration", type="secondary"):
                    # Clear results to allow retraining
                    if 'training_results' in st.session_state:
                        del st.session_state.training_results
                    if 'correlation_results' in st.session_state:
                        del st.session_state.correlation_results
                    st.rerun()
        
        # 6. BATCH TRAINING (ADVANCED)
        st.markdown("---")
        with st.expander("🚀 Advanced: Batch Training", expanded=False):
            st.markdown("**Train all three model types automatically:**")
            
            if st.button("🔥 Train All Model Types", type="secondary"):
                if 'training_data' not in st.session_state:
                    st.error("❌ Please load training data first")
                    return
                
                training_data = st.session_state.training_data
                batch_results = {}
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                model_types = ["displacement", "quaternion", "combined"]
                targets = ["subject", "test"]
                
                total_combinations = len(model_types) * len(targets)
                current_step = 0
                
                try:
                    for target in targets:
                        for model_type in model_types:
                            current_step += 1
                            status_text.text(f"Training {model_type} model for {target} prediction... ({current_step}/{total_combinations})")
                            
                            try:
                                results = trainer.train_model_pipeline(
                                    training_data,
                                    model_type=model_type,
                                    target=target,
                                    test_size=test_size,
                                    random_state=42
                                )
                                batch_results[f"{model_type}_{target}"] = results
                                
                            except Exception as e:
                                st.warning(f"⚠️ Failed to train {model_type} model for {target}: {str(e)}")
                            
                            progress_bar.progress(current_step / total_combinations)
                    
                    # Save batch results
                    st.session_state.batch_training_results = batch_results
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Show summary
                    st.success(f"🎉 Batch training completed! Trained {len(batch_results)} model configurations.")
                    
                    # Summary table
                    summary_data = []
                    for config_name, results in batch_results.items():
                        summary_data.append({
                            'Configuration': config_name,
                            'Best Model': results['best_model'],
                            'Test Accuracy': f"{results['best_accuracy']:.3f}",
                            'Features': results['selected_feature_count']
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Batch training failed: {str(e)}")
                    status_text.empty()
                    progress_bar.empty()
    
    def render_feature_extraction(self):
        """Render the feature extraction interface."""
        st.subheader("Feature Extraction Pipeline")
        
        # Check if we have available files
        available_files = SessionStateManager.get('available_files_info', [])
        if not available_files:
            st.warning("⚠️ No files available. Please go to File Overview tab first to load experiment data.")
            return
        
        # 1. FILE SELECTION (moved from File Overview)
        with st.expander("📁 Select Files for Processing", expanded=True):
            files_df = pd.DataFrame(available_files)
            
            col1, col2 = st.columns(2)
            selected_files = []
            
            with col1:
                st.markdown("**READ Files (Raw Data)**")
                read_files = files_df[files_df['Source'] == 'READ']
                for _, file_info in read_files.iterrows():
                    if st.checkbox(f"📄 {file_info['File Name']}", 
                                 key=f"feat_read_{file_info['File Name']}", 
                                 value=True):  # Default selected
                        selected_files.append(file_info['Path'])
            
            with col2:
                st.markdown("**WRITE Files (Processed Data)**")
                write_files = files_df[files_df['Source'] == 'WRITE']
                for _, file_info in write_files.iterrows():
                    icon = "📊" if file_info['Derived Features'] > 0 else "📄"
                    if st.checkbox(f"{icon} {file_info['File Name']}", 
                                 key=f"feat_write_{file_info['File Name']}"):
                        selected_files.append(file_info['Path'])
            
            if selected_files:
                st.success(f"✅ Selected {len(selected_files)} files for processing")
                SessionStateManager.set('selected_analysis_files', selected_files)
            else:
                st.warning("⚠️ No files selected for processing")
                SessionStateManager.set('selected_analysis_files', [])
        
        # 2. FEATURE SELECTION (more compact)
        with st.expander("🎯 Landmark Selection", expanded=True):
            col1, col2 = st.columns([3, 2])
            
            with col1:
                feature_input = st.text_input(
                    "Landmark Indices",
                    value="1",
                    help="Examples: '1' (nose tip), '1-10' (range), '20,34,7' (list)",
                    placeholder="Enter landmark indices..."
                )
            
            with col2:
                available_clusters = DerivedFeatures.get_available_clusters()
                selected_clusters = st.multiselect(
                    "Facial Clusters",
                    options=list(available_clusters.keys()),
                    default=[],
                    help="Select predefined facial regions"
                )
            
            # Parse and validate selection
            try:
                parsed_indices = DerivedFeatures.parse_feature_selection(feature_input, selected_clusters)
                if parsed_indices:
                    st.info(f"📍 Selected {len(parsed_indices)} landmarks: {parsed_indices[:10]}{'...' if len(parsed_indices) > 10 else ''}")
                else:
                    st.error("❌ No valid landmarks selected. Please enter at least one landmark index.")
                    parsed_indices = [1]  # Fallback to nose tip
            except Exception as e:
                st.error(f"❌ Error parsing selection: {str(e)}")
                parsed_indices = [1]  # Fallback to nose tip
        
        # 3. PROCESSING PIPELINE (more compact)
        with st.expander("⚙️ Processing Pipeline", expanded=False):
            # Initialize pipeline if not exists
            if 'processing_pipeline' not in st.session_state:
                st.session_state.processing_pipeline = []
            
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                step_type = st.selectbox(
                    "Add Step",
                    ["none", "rolling_average", "kabsch_alignment", "kabsch_umeyama_alignment"],
                    help="Choose processing step to add. Select 'none' for raw data extraction."
                )
            
            with col2:
                if step_type == "none":
                    st.info("💡 No preprocessing - raw displacement extraction")
                    param_value = None
                    param_key = None
                elif step_type == "rolling_average":
                    param_value = st.slider("Window Size", 2, 10, 3)
                    param_key = "window_size"
                else:
                    param_value = st.slider("Baseline Frames", 1, 20, 5)
                    param_key = "baseline_frame_count"
            
            with col3:
                if st.button("➕", help="Add pipeline step"):
                    if step_type == "none":
                        # Clear pipeline for raw extraction
                        st.session_state.processing_pipeline = []
                        st.success("🔄 Pipeline cleared for raw data extraction")
                        st.rerun()
                    else:
                        new_step = {
                            'type': step_type,
                            'params': {param_key: param_value}
                        }
                        st.session_state.processing_pipeline.append(new_step)
                        st.rerun()
            
            with col4:
                if st.button("🗑️", help="Clear all steps"):
                    st.session_state.processing_pipeline = []
                    st.success("🧹 Pipeline cleared")
                    st.rerun()
            
            # Display current pipeline status
            if st.session_state.processing_pipeline:
                st.markdown("**Current Pipeline:**")
                for i, step in enumerate(st.session_state.processing_pipeline):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(f"{i+1}. {step['type']} - {step['params']}")
                    with col2:
                        if st.button("❌", key=f"remove_step_{i}", help="Remove step"):
                            st.session_state.processing_pipeline.pop(i)
                            st.rerun()
            else:
                st.info("📋 **Empty Pipeline** - Raw data will be processed without filtering or alignment")
                st.caption("💡 Perfect for baseline displacement models")
        
        # 4. FEATURE CONFIGURATION (more compact)
        with st.expander("🔬 Feature Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Displacement Features**")
                displacement_enabled = st.checkbox("Enable", value=True, key="disp_enabled")
                
                if displacement_enabled:
                    displacement_type = st.radio(
                        "Type",
                        ["previous_frame", "baseline"],
                        horizontal=True,
                        help="Frame-to-frame or baseline displacement"
                    )
                    
                    baseline_count = st.slider("Baseline Frames", 1, 20, 5, key="disp_baseline")
                else:
                    displacement_type = "previous_frame"
                    baseline_count = 5
            
            with col2:
                st.markdown("**Quaternion Features**")
                quaternion_enabled = st.checkbox("Enable", value=False, key="quat_enabled")
                
                if quaternion_enabled:
                    quaternion_baseline = st.slider("Baseline Frames", 1, 20, 5, key="quat_baseline")
                    st.caption("💡 Extracted from rotation matrices")
                else:
                    quaternion_baseline = 5
        
        # 5. BUILD CONFIGURATION AND EXTRACT
        if selected_files and parsed_indices:
            # Build the complete configuration
            config = {
                'selected_indices': parsed_indices,  # This was missing!
                'displacement': {
                    'enabled': displacement_enabled,
                    'selected_indices': parsed_indices,  # Add here too for validation
                    'type': displacement_type,
                    'baseline_frame_count': baseline_count
                },
                'quaternion': {
                    'enabled': quaternion_enabled,
                    'baseline_frame_count': quaternion_baseline
                },
                'pipeline': st.session_state.processing_pipeline
            }
            
            # Validate configuration
            is_valid, error_msg = DerivedFeatures.validate_feature_config(config)
            
            if is_valid:
                st.success("✅ Configuration is valid")
                
                # Extract Features Button
                if st.button("🚀 Extract Features", type="primary", use_container_width=True):
                    self.execute_feature_extraction_improved(config, selected_files)
            else:
                st.error(f"❌ Configuration Error: {error_msg}")
                st.info("💡 **Fix:** Ensure at least one feature type is enabled and landmarks are selected.")
        else:
            st.warning("⚠️ Please select files and landmarks before extracting features.")
    
    def execute_feature_extraction_improved(self, config: Dict, selected_files: List[str]):
        """Execute feature extraction with improved UI feedback."""
        try:
            progress_container = st.container()
            
            with progress_container:
                st.info(f"🔄 Processing {len(selected_files)} files...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                extracted_features = []
                
                for i, file_path in enumerate(selected_files):
                    file_name = Path(file_path).name
                    status_text.text(f"Processing {file_name}...")
                    progress_bar.progress((i + 1) / len(selected_files))
                    
                    # Extract features
                    features_df = DerivedFeatures.extract_features_from_csv(file_path, config)
                    features_df['source_file'] = file_name
                    extracted_features.append(features_df)
                
                # Combine results
                if extracted_features:
                    combined_features = pd.concat(extracted_features, ignore_index=True)
                    
                    # Save results
                    current_experiment = SessionStateManager.get('current_experiment')
                    write_dir = self.data_write_dir / current_experiment.name
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    output_filename = f"extracted_features_{timestamp}.csv"
                    output_path = write_dir / output_filename
                    combined_features.to_csv(output_path, index=False)
                    
                    # Clear progress and show results
                    progress_container.empty()
                    
                    st.balloons()
                    st.success(f"🎉 Feature extraction completed successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Files Processed", len(selected_files))
                    with col2:
                        st.metric("Total Frames", len(combined_features))
                    with col3:
                        feature_cols = [col for col in combined_features.columns 
                                      if col.startswith('displacement_') or col.startswith('quaternion_')]
                        st.metric("Derived Features", len(feature_cols))
                    
                    st.info(f"📁 Saved: `{output_filename}`")
                    
                    # Show preview
                    with st.expander("📊 Preview Results", expanded=False):
                        st.dataframe(combined_features.head(10), use_container_width=True)
                        
                        if feature_cols:
                            st.markdown("**Extracted Features:**")
                            st.code(", ".join(feature_cols))
                
        except Exception as e:
            st.error(f"❌ Extraction failed: {str(e)}")
            with st.expander("🔍 Error Details"):
                import traceback
                st.code(traceback.format_exc())
    
    def render_feature_comparison(self):
        """Render the feature comparison interface."""
        st.subheader("Feature Comparison")
        st.info("🚧 Feature comparison coming soon...")
        st.markdown("""
        Planned features:
        - Side-by-side feature visualization
        - Statistical comparisons
        - Correlation analysis
        """)


def main():
    """Main entry point."""
    app = StreamlitInterface()
    app.run()


if __name__ == "__main__":
    main() 