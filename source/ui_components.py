"""UI Components Module

Provides reusable UI components and helpers for the Streamlit interface.
Helps modularize the main interface and reduce code duplication.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
import numpy as np


class StatusSidebar:
    """Manages the sidebar status display."""
    
    @staticmethod
    def render():
        """Render the complete status sidebar."""
        with st.sidebar:
            st.markdown("### 📊 Status")
            
            # Show current experiment info
            if hasattr(st.session_state, 'current_experiment'):
                st.success(f"📂 Experiment: {st.session_state.current_experiment.name}")
                
                # Show current file if loaded
                if hasattr(st.session_state, 'csv_file_path') and st.session_state.csv_file_path:
                    st.info(f"📄 File: {st.session_state.csv_file_path.stem}")
                    
                    if st.session_state.csv_data is not None:
                        frame_count = len(st.session_state.csv_data)
                        landmark_count = len([c for c in st.session_state.csv_data.columns 
                                            if c.startswith('feat_') and c.endswith('_x')])
                        st.caption(f"🎬 {frame_count} frames, {landmark_count} landmarks")
                
                # Show analysis status
                if hasattr(st.session_state, 'comprehensive_analysis_done') and st.session_state.comprehensive_analysis_done:
                    st.success("✅ Filter analysis complete")
                
                # Show animation status
                if hasattr(st.session_state, 'animation_created') and st.session_state.animation_created:
                    st.success("🎬 Animation created")
                    if hasattr(st.session_state, 'animation_name'):
                        st.caption(f"📁 {st.session_state.animation_name}")
            else:
                st.warning("⚠️ No experiment selected")
            
            st.markdown("---")
            
            # Quick settings display
            if hasattr(st.session_state, 'head_movement_compensation'):
                st.markdown("### ⚙️ Current Settings")
                st.caption(f"🔧 Filter: {st.session_state.head_movement_compensation.title()}")
                st.caption(f"🌊 Smoothing: {st.session_state.rolling_average_smoothing.title()}")
                if st.session_state.rolling_average_smoothing != "off":
                    st.caption(f"🪟 Window: {st.session_state.smoothing_window}")
                st.caption(f"🎨 Color: {st.session_state.color_mode.replace('_', ' ').title()}")
    
    @staticmethod
    def show_notification(message: str, notification_type: str = "info"):
        """Show a notification in the sidebar."""
        with st.sidebar:
            if notification_type == "success":
                st.success(message)
            elif notification_type == "error":
                st.error(message)
            elif notification_type == "warning":
                st.warning(message)
            else:
                st.info(message)


class AdvancedSettings:
    """Manages the advanced settings UI component."""
    
    @staticmethod
    def render():
        """Render the advanced settings expander."""
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
                
                st.selectbox(
                    "Head Movement Compensation",
                    ["off", "kabsch", "kabsch_umeyama"],
                    key='head_movement_compensation',
                    format_func=lambda x: {
                        "off": "Off (no compensation)",
                        "kabsch": "Rotation and displacement (Kabsch)",
                        "kabsch_umeyama": "Rotation, displacement and scale (Kabsch-Umeyama)"
                    }[x],
                    help="Choose method for removing head movement to isolate microexpressions"
                )
                
            with col2:
                st.selectbox(
                    "Rolling Average Smoothing",
                    ["off", "pre", "post"],
                    key='rolling_average_smoothing',
                    format_func=lambda x: {
                        "off": "Off",
                        "pre": "Before alignment",
                        "post": "After alignment"
                    }[x],
                    help="Apply rolling average to reduce noise"
                )
                
                if st.session_state.rolling_average_smoothing != "off":
                    st.number_input(
                        "Smoothing Window Size",
                        min_value=3,
                        max_value=5,
                        value=3,
                        key='smoothing_window',
                        help="Number of frames for rolling average"
                    )
            
            # Color mode section
            st.markdown("---")
            st.selectbox(
                "Color Mode",
                ["none", "point_cloud_continuous", "point_cloud_sd", "clusters_continuous", "clusters_sd"],
                key='color_mode',
                format_func=lambda x: {
                    "none": "None (White Points)",
                    "point_cloud_continuous": "Point Cloud (Continuous)",
                    "point_cloud_sd": "Point Cloud (Standard Deviation)",
                    "clusters_continuous": "Clusters (Continuous)",
                    "clusters_sd": "Clusters (Standard Deviation)"
                }[x],
                help="Choose how to color the point cloud based on movement analysis"
            )


class DataPreview:
    """Handles data preview displays."""
    
    @staticmethod
    def show_csv_preview(df: pd.DataFrame, file_path: Path):
        """Display a preview of the loaded CSV data."""
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
                st.dataframe(preview_df, use_container_width=True)
                
                # Show time range info
                time_col = df['Time (s)']
                st.info(f"⏱️ Time range: {time_col.min():.3f}s to {time_col.max():.3f}s "
                       f"(Duration: {time_col.max() - time_col.min():.3f}s)")
            else:
                st.dataframe(preview_df, use_container_width=True)
            
            # Show landmark statistics
            DataPreview.show_landmark_statistics(df, num_landmarks)
    
    @staticmethod
    def show_landmark_statistics(df: pd.DataFrame, num_landmarks: int):
        """Display landmark statistics."""
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


class FilterAnalysisDisplay:
    """Handles the display of filter analysis results."""
    
    @staticmethod
    def show_comprehensive_results(comprehensive_results: Dict[str, Any]) -> tuple:
        """Display comprehensive filter analysis results.
        
        Returns:
            tuple: (best_method, best_type, best_overall, best_smoothing, best_window)
        """
        st.write("**Movement Reduction Comparison:**")
        st.caption("Higher percentages indicate better noise reduction while preserving microexpressions")
        
        # Create comprehensive DataFrame
        comparison_data = []
        for method_key in ['none', 'kabsch', 'kabsch_umeyama']:
            if method_key in comprehensive_results:
                result = comprehensive_results[method_key]
                
                row = {
                    'Method': result['method'],
                    'Reduction %': f"{result['reduction_percent']:.2f}%"
                }
                
                # Add pre-smoothing results
                for window in [3, 4, 5]:
                    key = f'pre_ras_{window}'
                    if key in result:
                        row[f'Pre-RAS {window}'] = f"{result[key]:.2f}%"
                    else:
                        row[f'Pre-RAS {window}'] = "N/A"
                
                # Add post-smoothing results
                for window in [3, 4, 5]:
                    key = f'post_ras_{window}'
                    if key in result:
                        row[f'Post-RAS {window}'] = f"{result[key]:.2f}%"
                    else:
                        row[f'Post-RAS {window}'] = "N/A"
                
                comparison_data.append(row)
        
        comprehensive_df = pd.DataFrame(comparison_data)
        st.dataframe(comprehensive_df, use_container_width=True)
        
        # Find best performing combination
        return FilterAnalysisDisplay.find_best_combination(comprehensive_results)
    
    @staticmethod
    def find_best_combination(comprehensive_results: Dict[str, Any]) -> tuple:
        """Find the best performing filter combination."""
        best_overall = 0
        best_method = ""
        best_type = ""
        best_smoothing = ""
        best_window = 0
        
        for method_key in ['none', 'kabsch', 'kabsch_umeyama']:
            if method_key in comprehensive_results:
                result = comprehensive_results[method_key]
                
                # Check base method
                if result['reduction_percent'] > best_overall:
                    best_overall = result['reduction_percent']
                    best_method = result['method']
                    best_type = "Base alignment"
                    best_smoothing = "off"
                    best_window = 0
                
                # Check pre-smoothing
                for window in [3, 4, 5]:
                    key = f'pre_ras_{window}'
                    if key in result and result[key] > best_overall:
                        best_overall = result[key]
                        best_method = result['method']
                        best_type = f"Pre-RAS {window}-frame"
                        best_smoothing = "pre"
                        best_window = window
                
                # Check post-smoothing
                for window in [3, 4, 5]:
                    key = f'post_ras_{window}'
                    if key in result and result[key] > best_overall:
                        best_overall = result[key]
                        best_method = result['method']
                        best_type = f"Post-RAS {window}-frame"
                        best_smoothing = "post"
                        best_window = window
        
        return best_method, best_type, best_overall, best_smoothing, best_window 