"""Video Exporter Module

Simplified video export with minimal settings and automatic fallbacks.
Focuses on "just works" approach instead of overwhelming options.
"""

import os
import tempfile
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class VideoExporter:
    """Simplified video exporter with automatic codec fallback."""
    
    # Simplified codec list - try best first, fallback automatically
    CODECS = [
        ('mp4v', '.mp4'),  # Most compatible
        ('XVID', '.avi'),  # Fallback
        ('MJPG', '.avi'),  # Last resort
    ]
    
    def __init__(self, progress_callback=None):
        """Initialize exporter with optional progress callback."""
        self.progress_callback = progress_callback
        self.update_status("Ready to export")
    
    def update_status(self, message):
        """Update export status."""
        if self.progress_callback:
            self.progress_callback(message)
    
    def export_video(self, frames_data, fps=10):
        """Export animation as video - simplified with auto-fallback."""
        try:
            self.update_status("Starting video export...")
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="video_export_")
            frame_paths = []
            
            # Pre-calculate bounds for consistency
            all_points = np.vstack([f['points'] for f in frames_data])
            max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
            mid = np.mean(all_points, axis=0)
            bounds = {
                'xlim': [mid[0] - max_range, mid[0] + max_range],
                'ylim': [mid[1] - max_range, mid[1] + max_range],
                'zlim': [mid[2] - max_range, mid[2] + max_range]
            }
            
            # Render frames
            total_frames = len(frames_data)
            for i, frame_data in enumerate(frames_data):
                progress = (i + 1) / total_frames
                self.update_status(f"Rendering frame {i+1}/{total_frames} ({progress*100:.0f}%)")
                
                frame_path = self._render_frame(frame_data, i, total_frames, bounds, temp_dir)
                frame_paths.append(frame_path)
            
            # Create video with automatic codec fallback
            self.update_status("Encoding video...")
            video_path = self._create_video(frame_paths, fps, temp_dir)
            
            if video_path:
                file_size = os.path.getsize(video_path)
                self.update_status(f"Export complete! ({file_size / (1024*1024):.1f} MB)")
                return video_path
            else:
                raise RuntimeError("All video codecs failed")
                
        except Exception as e:
            self.update_status(f"Export failed: {str(e)}")
            raise e
    
    def _render_frame(self, frame_data, frame_num, total_frames, bounds, temp_dir):
        """Render a single frame to PNG."""
        points = frame_data['points']
        colors = frame_data['colors']
        
        # Clean matplotlib rendering (no emoji to prevent stalling)
        fig = plt.figure(figsize=(12, 9), facecolor='black', dpi=100)
        ax = fig.add_subplot(111, projection='3d', facecolor='black')
        
        if colors is not None:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=3, alpha=0.8, edgecolors='none')
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=points[:, 2], cmap='viridis', s=3, alpha=0.8, edgecolors='none')
        
        # Clean styling (NO emoji characters anywhere)
        ax.set_xlabel('X', color='white', fontsize=12)
        ax.set_ylabel('Y', color='white', fontsize=12)
        ax.set_zlabel('Z', color='white', fontsize=12)
        ax.tick_params(colors='white', labelsize=10)
        ax.set_title(f'Frame {frame_num+1}/{total_frames} | {len(points)} points', 
                   color='white', fontsize=14, pad=20)
        
        # Apply consistent bounds
        ax.set_xlim(bounds['xlim'])
        ax.set_ylim(bounds['ylim'])
        ax.set_zlim(bounds['zlim'])
        
        # Save frame
        frame_path = os.path.join(temp_dir, f"frame_{frame_num:04d}.png")
        plt.savefig(frame_path, dpi=100, bbox_inches='tight', 
                  facecolor='black', edgecolor='none', format='png')
        plt.close()
        
        # Verify frame was created properly
        if not os.path.exists(frame_path) or os.path.getsize(frame_path) < 1000:
            raise ValueError(f"Frame {frame_num+1} failed to render properly")
        
        return frame_path
    
    def _create_video(self, frame_paths, fps, temp_dir):
        """Create video with automatic codec fallback."""
        if not frame_paths:
            raise ValueError("No frames to encode")
        
        # Get video dimensions from first frame
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            raise ValueError("Could not read first frame")
        
        height, width, layers = first_frame.shape
        
        # Try codecs in order until one works
        for codec, ext in self.CODECS:
            self.update_status(f"Trying {codec} codec...")
            
            try:
                video_path = os.path.join(temp_dir, f"animation{ext}")
                fourcc = cv2.VideoWriter_fourcc(*codec)
                video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
                
                if not video_writer.isOpened():
                    video_writer.release()
                    continue
                
                # Write all frames
                for frame_path in frame_paths:
                    frame = cv2.imread(frame_path)
                    if frame is not None:
                        video_writer.write(frame)
                    else:
                        video_writer.release()
                        raise ValueError(f"Could not read frame: {frame_path}")
                
                video_writer.release()
                
                # Verify the video file
                if os.path.exists(video_path) and os.path.getsize(video_path) > 5000:
                    return video_path
                    
            except Exception:
                continue
        
        # If we get here, all codecs failed
        return None
    
    @staticmethod
    def get_export_info():
        """Get information about export capabilities."""
        return {
            'default_fps': 10,
            'max_fps': 30,
            'supported_formats': ['MP4', 'AVI'],
            'automatic_fallback': True,
            'quality': 'High (100 DPI)'
        }


def create_simple_export(frames_data, fps=10, progress_callback=None):
    """Simple function interface for video export."""
    exporter = VideoExporter(progress_callback)
    return exporter.export_video(frames_data, fps) 