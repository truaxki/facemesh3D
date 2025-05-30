"""Session State Manager Module

Centralized management of Streamlit session state.
Provides default values and initialization logic.
"""

import streamlit as st
from typing import Dict, Any


class SessionStateManager:
    """Manages Streamlit session state initialization and defaults."""
    
    # Default session state values
    DEFAULTS = {
        'current_tab': 'Import',
        'csv_file_path': None,
        'csv_data': None,
        'frames_data': None,
        'animation_created': False,
        'z_scale': 25.0,
        'color_mode': 'point_cloud_sd',  # Standard deviation as default
        'baseline_frames': 30,
        'animation_fps': 15,
        'head_movement_compensation': 'kabsch',  # Default to Kabsch
        'rolling_average_smoothing': 'off',
        'smoothing_window': 3,
        'comprehensive_analysis_done': False,
        'show_advanced_settings': False,
        'show_cluster_analysis': False
    }
    
    @classmethod
    def initialize(cls):
        """Initialize session state with default values."""
        for key, value in cls.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @classmethod
    def reset_analysis_state(cls):
        """Reset analysis-related state variables."""
        st.session_state.csv_data = None
        st.session_state.frames_data = None
        st.session_state.animation_created = False
        st.session_state.comprehensive_analysis_done = False
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from session state with optional default."""
        return getattr(st.session_state, key, default)
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Set a value in session state."""
        st.session_state[key] = value
    
    @classmethod
    def has(cls, key: str) -> bool:
        """Check if a key exists in session state."""
        return hasattr(st.session_state, key) and getattr(st.session_state, key) is not None
    
    @classmethod
    def check_optimal_settings(cls, best_method: str, best_smoothing: str, best_window: int) -> bool:
        """Check if current settings match the optimal filter combination."""
        return (
            st.session_state.head_movement_compensation == best_method.lower().replace('-', '_') and
            st.session_state.rolling_average_smoothing == best_smoothing and
            (best_smoothing == "off" or st.session_state.smoothing_window == best_window)
        ) 