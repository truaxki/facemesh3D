"""Configuration Management

Centralized settings and defaults for the point cloud system.
Reduces scattered magic numbers and provides single source of truth.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import tempfile
import os


@dataclass
class RenderSettings:
    """3D Rendering configuration."""
    point_size: float = 3.0
    figure_size: tuple = (12, 9)
    dpi: int = 100
    alpha: float = 0.8
    background_colors: List[List[float]] = None
    
    def __post_init__(self):
        if self.background_colors is None:
            self.background_colors = [
                [0.05, 0.05, 0.2],  # Dark blue
                [0, 0, 0],          # Black
                [1, 1, 1],          # White
                [0.2, 0.2, 0.2],    # Dark gray
            ]


@dataclass
class AnimationSettings:
    """Animation configuration."""
    default_fps: int = 10
    max_fps: int = 30
    min_fps: int = 1
    auto_cleanup: bool = True
    frame_format: str = "frame_{:04d}.png"
    temp_prefix: str = "animation_"


@dataclass
class VideoExportSettings:
    """Video export configuration - SIMPLIFIED."""
    # Core settings only - no overwhelming options
    fps: int = 10
    quality: str = "standard"  # "draft", "standard", "high"
    format: str = "mp4"        # "mp4", "avi"
    
    # Internal settings (not exposed to user)
    _codecs_to_try: List[tuple] = None
    _max_file_size_mb: int = 50
    
    def __post_init__(self):
        if self._codecs_to_try is None:
            self._codecs_to_try = [
                ('mp4v', '.mp4', 'MP4 Standard'),
                ('XVID', '.avi', 'XVID AVI'),
                ('MJPG', '.avi', 'Motion JPEG'),
            ]
    
    @property
    def quality_settings(self) -> Dict[str, Any]:
        """Get quality-specific settings."""
        settings = {
            "draft": {"dpi": 72, "point_size": 2.0, "figure_size": (8, 6)},
            "standard": {"dpi": 100, "point_size": 3.0, "figure_size": (12, 9)},
            "high": {"dpi": 150, "point_size": 4.0, "figure_size": (16, 12)},
        }
        return settings.get(self.quality, settings["standard"])


@dataclass
class AppConfig:
    """Main application configuration."""
    window_title: str = "Open3D Point Cloud System"
    temp_dir: str = None
    auto_launch_viewer: bool = True
    cleanup_temp_files: bool = True
    
    # Component settings
    render: RenderSettings = None
    animation: AnimationSettings = None
    video_export: VideoExportSettings = None
    
    def __post_init__(self):
        if self.temp_dir is None:
            self.temp_dir = tempfile.gettempdir()
        if self.render is None:
            self.render = RenderSettings()
        if self.animation is None:
            self.animation = AnimationSettings()
        if self.video_export is None:
            self.video_export = VideoExportSettings()


# Global configuration instance
CONFIG = AppConfig()


def get_shape_defaults() -> Dict[str, Dict[str, Any]]:
    """Get default parameters for each shape type."""
    return {
        "Sphere": {"radius": 1.0},
        "Torus": {"major_radius": 1.0, "minor_radius": 0.3},
        "Helix": {"turns": 3, "height": 2.0, "radius": 1.0},
        "Cube": {"side_length": 2.0},
        "Random": {}
    }


def get_temp_directory(prefix: str = "pointcloud_") -> str:
    """Create a temporary directory with timestamp."""
    import time
    timestamp = int(time.time() * 1000)
    return tempfile.mkdtemp(prefix=f"{prefix}{timestamp}_")
