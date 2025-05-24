"""Animation Data Management

Handles loading, validation, and management of animation frame data.
Separated from UI logic for better testability and reuse.
"""

import os
import glob
import numpy as np
import open3d as o3d
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from .config import CONFIG


class AnimationFrameData:
    """Container for a single animation frame."""
    
    def __init__(self, points: np.ndarray, colors: Optional[np.ndarray] = None, filename: str = ""):
        self.points = points
        self.colors = colors
        self.filename = filename
        self.frame_info = {
            'num_points': len(points),
            'has_colors': colors is not None,
            'bounds': self._calculate_bounds()
        }
    
    def _calculate_bounds(self) -> Dict[str, float]:
        """Calculate bounding box for the frame."""
        if len(self.points) == 0:
            return {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0, 'min_z': 0, 'max_z': 0}
        
        mins = np.min(self.points, axis=0)
        maxs = np.max(self.points, axis=0)
        return {
            'min_x': mins[0], 'max_x': maxs[0],
            'min_y': mins[1], 'max_y': maxs[1], 
            'min_z': mins[2], 'max_z': maxs[2]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            'points': self.points,
            'colors': self.colors,
            'filename': self.filename
        }


class AnimationLoader:
    """Loads and validates animation data from various sources."""
    
    def __init__(self):
        self.frames: List[AnimationFrameData] = []
        self.metadata = {}
    
    def load_from_folder(
        self, 
        folder_path: str, 
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Load animation frames from PLY files in a folder.
        
        Args:
            folder_path: Path to folder containing PLY files
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(folder_path):
            if progress_callback:
                progress_callback(f"Folder not found: {folder_path}", 0.0)
            return False
        
        # Find PLY files
        ply_files = sorted(glob.glob(os.path.join(folder_path, "*.ply")))
        if not ply_files:
            if progress_callback:
                progress_callback(f"No PLY files found in {folder_path}", 0.0)
            return False
        
        # Load frames
        self.frames = []
        successful_loads = 0
        
        for i, ply_file in enumerate(ply_files):
            progress = (i + 1) / len(ply_files)
            
            if progress_callback:
                progress_callback(
                    f"Loading frame {i+1}/{len(ply_files)}: {os.path.basename(ply_file)}", 
                    progress
                )
            
            try:
                pcd = o3d.io.read_point_cloud(ply_file)
                points = np.asarray(pcd.points)
                colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
                
                if len(points) > 0:
                    frame = AnimationFrameData(
                        points=points,
                        colors=colors,
                        filename=os.path.basename(ply_file)
                    )
                    self.frames.append(frame)
                    successful_loads += 1
                else:
                    if progress_callback:
                        progress_callback(f"Warning: Empty frame {ply_file}", progress)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error loading {ply_file}: {e}", progress)
                continue
        
        # Update metadata
        self.metadata = {
            'source_folder': folder_path,
            'total_files': len(ply_files),
            'successful_loads': successful_loads,
            'failed_loads': len(ply_files) - successful_loads,
            'frame_count': len(self.frames)
        }
        
        success = len(self.frames) > 0
        if progress_callback:
            if success:
                progress_callback(
                    f"Successfully loaded {len(self.frames)} frames from {len(ply_files)} files", 
                    1.0
                )
            else:
                progress_callback("Failed to load any valid frames", 1.0)
        
        return success
    
    def validate_frames(self) -> Dict[str, Any]:
        """Validate loaded frames and return validation report."""
        if not self.frames:
            return {
                'valid': False,
                'error': 'No frames loaded',
                'warnings': []
            }
        
        warnings = []
        
        # Check frame consistency
        first_frame = self.frames[0]
        point_counts = [len(frame.points) for frame in self.frames]
        
        if len(set(point_counts)) > 1:
            warnings.append(f"Inconsistent point counts: {min(point_counts)}-{max(point_counts)}")
        
        # Check color consistency
        color_states = [frame.colors is not None for frame in self.frames]
        if not all(color_states) and any(color_states):
            warnings.append("Mixed color/no-color frames")
        
        # Check for reasonable bounds
        all_points = np.vstack([frame.points for frame in self.frames])
        max_coord = np.max(np.abs(all_points))
        if max_coord > 1000:
            warnings.append(f"Large coordinates detected (max: {max_coord:.1f})")
        
        return {
            'valid': True,
            'frame_count': len(self.frames),
            'point_count_range': (min(point_counts), max(point_counts)),
            'has_colors': any(color_states),
            'consistent_colors': len(set(color_states)) == 1,
            'warnings': warnings,
            'metadata': self.metadata
        }
    
    def get_frame_data_list(self) -> List[Dict[str, Any]]:
        """Get frames in dictionary format for compatibility with existing code."""
        return [frame.to_dict() for frame in self.frames]
    
    def get_animation_bounds(self) -> Dict[str, float]:
        """Get overall bounding box for the entire animation."""
        if not self.frames:
            return {}
        
        all_points = np.vstack([frame.points for frame in self.frames])
        mins = np.min(all_points, axis=0)
        maxs = np.max(all_points, axis=0)
        
        return {
            'min_x': mins[0], 'max_x': maxs[0],
            'min_y': mins[1], 'max_y': maxs[1],
            'min_z': mins[2], 'max_z': maxs[2],
            'center': np.mean([mins, maxs], axis=0),
            'extent': maxs - mins
        }


def find_animation_folders(base_path: str = "animations") -> List[str]:
    """Find available animation folders.
    
    Args:
        base_path: Base directory to search for animations
        
    Returns:
        List of animation folder names
    """
    if not os.path.exists(base_path):
        return []
    
    try:
        folders = []
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                # Check if folder contains PLY files
                ply_files = glob.glob(os.path.join(item_path, "*.ply"))
                if ply_files:
                    folders.append(item)
        return sorted(folders)
    except Exception:
        return []


def get_animation_info(folder_path: str) -> Dict[str, Any]:
    """Get quick info about an animation folder without loading all data.
    
    Args:
        folder_path: Path to animation folder
        
    Returns:
        Dictionary with animation info
    """
    info = {
        'exists': False,
        'frame_count': 0,
        'ply_files': [],
        'size_mb': 0.0,
        'error': None
    }
    
    try:
        if not os.path.exists(folder_path):
            info['error'] = 'Folder does not exist'
            return info
        
        info['exists'] = True
        
        # Find PLY files
        ply_files = sorted(glob.glob(os.path.join(folder_path, "*.ply")))
        info['ply_files'] = [os.path.basename(f) for f in ply_files]
        info['frame_count'] = len(ply_files)
        
        # Calculate total size
        total_size = sum(os.path.getsize(f) for f in ply_files if os.path.exists(f))
        info['size_mb'] = total_size / (1024 * 1024)
        
    except Exception as e:
        info['error'] = str(e)
    
    return info
