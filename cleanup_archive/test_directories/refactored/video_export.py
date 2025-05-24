"""Simplified Video Export Module

Streamlined MP4 export with minimal user-facing settings.
Focus: Just FPS and Quality. Everything else is automatic.
"""

import os
import tempfile
import cv2
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from .config import CONFIG, VideoExportSettings


class SimpleVideoExporter:
    """Simplified video exporter - minimal settings, maximum reliability."""
    
    def __init__(self, fps: int = 10, quality: str = "standard"):
        """Initialize with simple settings.
        
        Args:
            fps: Frames per second (1-30)
            quality: "draft", "standard", or "high"
        """
        self.fps = max(1, min(30, fps))  # Clamp FPS
        self.quality = quality if quality in ["draft", "standard", "high"] else "standard"
        self.settings = CONFIG.video_export.quality_settings[self.quality]
        
        # Status tracking
        self.current_status = "Ready"
        self.progress = 0.0
        
    def export_animation(
        self, 
        frames_data: List[Dict[str, Any]], 
        progress_callback: Optional[Callable] = None
    ) -> Optional[bytes]:
        """Export animation to MP4 - one method, automatic everything.
        
        Args:
            frames_data: List of frame dicts with 'points' and 'colors'
            progress_callback: Optional callback for progress updates
            
        Returns:
            Video file bytes if successful, None if failed
        """
        if not frames_data:
            self._update_status("No frames to export", progress_callback)
            return None
        
        temp_dir = None
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="video_export_")
            self._update_status(f"Starting export of {len(frames_data)} frames...", progress_callback)
            
            # Render frames
            frame_paths = self._render_frames(frames_data, temp_dir, progress_callback)
            if not frame_paths:
                return None
            
            # Create video
            video_data = self._create_video(frame_paths, progress_callback)
            return video_data
            
        except Exception as e:
            self._update_status(f"Export failed: {str(e)}", progress_callback)
            return None
        finally:
            # Cleanup
            if temp_dir and CONFIG.cleanup_temp_files:
                self._cleanup_temp_dir(temp_dir)
    
    def _render_frames(
        self, 
        frames_data: List[Dict[str, Any]], 
        temp_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """Render all frames to PNG files."""
        frame_paths = []
        total_frames = len(frames_data)
        
        # Pre-compute consistent view limits for all frames
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
        mid = np.mean(all_points, axis=0)
        xlim = [mid[0] - max_range, mid[0] + max_range]
        ylim = [mid[1] - max_range, mid[1] + max_range]
        zlim = [mid[2] - max_range, mid[2] + max_range]
        
        for i, frame_data in enumerate(frames_data):
            try:
                progress = (i + 1) / total_frames
                self.progress = progress * 0.7  # 70% for rendering
                self._update_status(
                    f"Rendering frame {i+1}/{total_frames} ({progress*100:.0f}%)",
                    progress_callback
                )
                
                # Create frame
                frame_path = self._render_single_frame(
                    frame_data, i, temp_dir, xlim, ylim, zlim
                )
                
                if frame_path and os.path.exists(frame_path):
                    frame_paths.append(frame_path)
                else:
                    raise ValueError(f"Frame {i+1} rendering failed")
                    
            except Exception as e:
                self._update_status(f"Frame {i+1} failed: {e}", progress_callback)
                return []
        
        self._update_status(f"All {len(frame_paths)} frames rendered successfully!", progress_callback)
        return frame_paths
    
    def _render_single_frame(
        self, 
        frame_data: Dict[str, Any], 
        frame_index: int,
        temp_dir: str,
        xlim: List[float],
        ylim: List[float],
        zlim: List[float]
    ) -> str:
        """Render a single frame to PNG."""
        points = frame_data['points']
        colors = frame_data['colors']
        
        # Create figure with quality settings
        fig = plt.figure(
            figsize=self.settings['figure_size'],
            facecolor='black',
            dpi=self.settings['dpi']
        )
        ax = fig.add_subplot(111, projection='3d', facecolor='black')
        
        # Plot points
        if colors is not None:
            ax.scatter(
                points[:, 0], points[:, 1], points[:, 2],
                c=colors, 
                s=self.settings['point_size'],
                alpha=CONFIG.render.alpha,
                edgecolors='none'
            )
        else:
            ax.scatter(
                points[:, 0], points[:, 1], points[:, 2],
                c=points[:, 2], 
                cmap='viridis',
                s=self.settings['point_size'],
                alpha=CONFIG.render.alpha,
                edgecolors='none'
            )
        
        # Clean styling
        ax.set_xlabel('X', color='white', fontsize=12)
        ax.set_ylabel('Y', color='white', fontsize=12)
        ax.set_zlabel('Z', color='white', fontsize=12)
        ax.tick_params(colors='white', labelsize=10)
        ax.set_title(
            f'Frame {frame_index+1} | {len(points)} points',
            color='white', fontsize=14, pad=20
        )
        
        # Set consistent limits
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)
        
        # Save frame
        frame_path = os.path.join(temp_dir, f"frame_{frame_index:04d}.png")
        plt.savefig(
            frame_path,
            dpi=self.settings['dpi'],
            bbox_inches='tight',
            facecolor='black',
            edgecolor='none',
            format='png'
        )
        plt.close()
        
        return frame_path
    
    def _create_video(
        self, 
        frame_paths: List[str],
        progress_callback: Optional[Callable] = None
    ) -> Optional[bytes]:
        """Create video from frame files."""
        if not frame_paths:
            return None
        
        # Get first frame dimensions
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            self._update_status("Could not read first frame", progress_callback)
            return None
        
        height, width, layers = first_frame.shape
        
        # Try codecs in order
        for codec, ext, description in CONFIG.video_export._codecs_to_try:
            self.progress = 0.8  # 80% for video creation
            self._update_status(f"Trying {description}...", progress_callback)
            
            try:
                # Create temporary video file
                temp_video = tempfile.mktemp(suffix=ext)
                fourcc = cv2.VideoWriter_fourcc(*codec)
                video = cv2.VideoWriter(temp_video, fourcc, self.fps, (width, height))
                
                if not video.isOpened():
                    video.release()
                    continue
                
                # Write frames
                for frame_path in frame_paths:
                    frame = cv2.imread(frame_path)
                    if frame is not None:
                        video.write(frame)
                    else:
                        video.release()
                        raise ValueError(f"Could not read frame: {frame_path}")
                
                video.release()
                
                # Verify video file
                if os.path.exists(temp_video):
                    file_size = os.path.getsize(temp_video)
                    if file_size > 5000:  # Reasonable minimum size
                        # Read video data
                        with open(temp_video, 'rb') as f:
                            video_data = f.read()
                        
                        # Cleanup temp video
                        try:
                            os.unlink(temp_video)
                        except:
                            pass
                        
                        self.progress = 1.0
                        self._update_status(
                            f"Video ready! ({file_size / (1024*1024):.1f} MB, {description})",
                            progress_callback
                        )
                        return video_data
                
            except Exception as e:
                self._update_status(f"{description} failed: {e}", progress_callback)
                continue
        
        self._update_status("All video codecs failed", progress_callback)
        return None
    
    def _update_status(self, status: str, callback: Optional[Callable] = None):
        """Update status and call callback if provided."""
        self.current_status = status
        if callback:
            callback(self.current_status, self.progress)
    
    def _cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass  # Silent cleanup failure


def export_video_simple(
    frames_data: List[Dict[str, Any]], 
    fps: int = 10, 
    quality: str = "standard"
) -> Optional[bytes]:
    """One-function video export for simple use cases.
    
    Args:
        frames_data: Animation frame data
        fps: Frames per second (1-30)
        quality: "draft", "standard", or "high"
    
    Returns:
        Video bytes or None if failed
    """
    exporter = SimpleVideoExporter(fps=fps, quality=quality)
    return exporter.export_animation(frames_data)


def get_export_filename(num_frames: int, fps: int, format: str = "mp4") -> str:
    """Generate standard filename for exported video."""
    return f"pointcloud_animation_{num_frames}frames_{fps}fps.{format}"
