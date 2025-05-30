"""
Facemesh 3D Point Cloud Visualization - Source Package

This package contains all the source code for the facial microexpression analysis system.
"""

# Core functionality modules
from .viewer_core import ViewerCore
from .file_manager import FileManager
from .animation_player import AnimationPlayer, ComparisonAnimationPlayer
from .desktop_launcher import DesktopLauncher
from .data_filters import DataFilters
from .visualization import VisualizationManager
from .video_exporter import VideoExporter
from .facial_clusters import FACIAL_CLUSTERS

# UI modules (refactored for modularity)
from .streamlit_interface import StreamlitInterface
from .ui_components import StatusSidebar, AdvancedSettings, DataPreview, FilterAnalysisDisplay
from .color_processors import ColorProcessor
from .session_state_manager import SessionStateManager
from .cluster_analysis_ui import ClusterAnalysisUI

__version__ = "2.0.0"
__author__ = "Point Cloud Visualization Team"

__all__ = [
    'ViewerCore',
    'FileManager', 
    'AnimationPlayer',
    'ComparisonAnimationPlayer',
    'DesktopLauncher',
    'DataFilters',
    'VisualizationManager',
    'VideoExporter',
    'FACIAL_CLUSTERS',
    'StreamlitInterface',
    'StatusSidebar',
    'AdvancedSettings',
    'DataPreview',
    'FilterAnalysisDisplay',
    'ColorProcessor',
    'SessionStateManager',
    'ClusterAnalysisUI'
] 