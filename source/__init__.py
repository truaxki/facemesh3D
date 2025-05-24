"""Source Package

Modular point cloud visualization package for Open3D and Streamlit.
Clean separation of concerns with focused modules.
"""

from source.point_cloud_generator import PointCloudGenerator
from source.file_manager import FileManager
from source.video_exporter import VideoExporter
from source.desktop_launcher import DesktopLauncher
from source.visualization import PointCloudVisualizer
from source.streamlit_interface import StreamlitInterface

__version__ = "2.0.0"
__author__ = "Point Cloud Visualization Team"

# Package metadata
__all__ = [
    'PointCloudGenerator',
    'FileManager', 
    'VideoExporter',
    'DesktopLauncher',
    'PointCloudVisualizer',
    'StreamlitInterface'
] 