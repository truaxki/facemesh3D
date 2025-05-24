"""File Manager Module

Handles all file I/O operations for point clouds.
Supports PLY, PCD, XYZ, and CSV formats with proper error handling.
"""

import os
import glob
import tempfile
import json
import time
import numpy as np
import open3d as o3d
import pandas as pd
from io import StringIO
from pathlib import Path


class FileManager:
    """Handles file operations for point clouds."""
    
    @staticmethod
    def create_point_cloud(points, colors=None):
        """Convert numpy arrays to Open3D point cloud."""
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
        if colors is not None:
            pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
        pcd.estimate_normals()
        return pcd
    
    @staticmethod
    def save_point_cloud(points, colors, config):
        """Save point cloud to temporary PLY file with config."""
        timestamp = int(time.time() * 1000)
        temp_dir = tempfile.mkdtemp(prefix=f"open3d_{timestamp}_")
        
        try:
            # Save point cloud
            pcd = FileManager.create_point_cloud(points, colors)
            ply_path = os.path.join(temp_dir, f"pointcloud_{timestamp}.ply")
            success = o3d.io.write_point_cloud(ply_path, pcd)
            
            if not success:
                raise RuntimeError("Failed to write PLY file")
            
            # Save config
            config_path = os.path.join(temp_dir, f"config_{timestamp}.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            return ply_path, config_path, temp_dir
            
        except Exception as e:
            # Clean up on error
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
            raise e
    
    @staticmethod
    def load_uploaded_file(uploaded_file):
        """Load point cloud from uploaded file."""
        try:
            if uploaded_file.name.endswith('.csv'):
                return FileManager._load_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.ply', '.pcd', '.xyz')):
                return FileManager._load_binary_file(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {uploaded_file.name}")
                
        except Exception as e:
            raise RuntimeError(f"Error loading file: {str(e)}")
    
    @staticmethod
    def _load_csv(uploaded_file):
        """Load CSV file with X,Y,Z and optional R,G,B columns."""
        content = StringIO(uploaded_file.getvalue().decode('utf-8'))
        df = pd.read_csv(content)
        
        if len(df.columns) < 3:
            raise ValueError("CSV must have at least 3 columns (X, Y, Z)")
        
        points = df.iloc[:, :3].values
        colors = None
        
        if len(df.columns) >= 6:
            colors = df.iloc[:, 3:6].values
            if np.max(colors) > 1:
                colors = colors / 255.0
        
        return points, colors
    
    @staticmethod
    def _load_binary_file(uploaded_file):
        """Load PLY/PCD/XYZ files using Open3D."""
        # Create temp file with proper Windows handling
        temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(uploaded_file.name)[1])
        try:
            # Write data to temp file
            with os.fdopen(temp_fd, 'wb') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            
            # Read with Open3D
            pcd = o3d.io.read_point_cloud(temp_path)
            points = np.asarray(pcd.points)
            colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
            
            return points, colors
            
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # Temp files will be cleaned up by OS
    
    @staticmethod
    def load_animation_folder(folder_path):
        """Load all PLY files from a folder in alphabetical order."""
        try:
            ply_files = sorted(glob.glob(os.path.join(folder_path, "*.ply")))
            
            if not ply_files:
                raise ValueError(f"No PLY files found in {folder_path}")
            
            frames_data = []
            
            for ply_file in ply_files:
                try:
                    pcd = o3d.io.read_point_cloud(ply_file)
                    points = np.asarray(pcd.points)
                    colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
                    
                    frames_data.append({
                        'points': points,
                        'colors': colors,
                        'filename': os.path.basename(ply_file)
                    })
                    
                except Exception as e:
                    print(f"Warning: Could not load {ply_file}: {e}")
                    continue
            
            if not frames_data:
                raise ValueError("No valid PLY files could be loaded")
                
            return frames_data
                
        except Exception as e:
            raise RuntimeError(f"Error loading folder: {e}")
    
    @staticmethod
    def save_animation_frames(frames_data):
        """Save animation frames for desktop viewer."""
        timestamp = int(time.time() * 1000)
        temp_dir = tempfile.mkdtemp(prefix=f"animation_{timestamp}_")
        
        try:
            ply_paths = []
            
            for i, frame_data in enumerate(frames_data):
                points = frame_data['points']
                colors = frame_data['colors']
                
                # Create point cloud
                pcd = FileManager.create_point_cloud(points, colors)
                
                # Save frame
                ply_path = os.path.join(temp_dir, f"frame_{i:04d}.ply")
                o3d.io.write_point_cloud(ply_path, pcd)
                ply_paths.append(ply_path)
            
            # Save animation config
            config = {
                'type': 'animation',
                'num_frames': len(frames_data),
                'frame_paths': ply_paths,
                'fps': 10
            }
            
            config_path = os.path.join(temp_dir, "animation_config.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            return temp_dir, config_path, ply_paths
            
        except Exception as e:
            # Clean up on error
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
            raise e
    
    @staticmethod
    def get_animation_folders():
        """Get available animation folders."""
        animations_dir = os.path.join(os.getcwd(), "animations")
        
        if not os.path.exists(animations_dir):
            return []
        
        try:
            subfolders = [f for f in os.listdir(animations_dir) 
                         if os.path.isdir(os.path.join(animations_dir, f))]
            return sorted(subfolders)
        except Exception:
            return []


def get_supported_formats():
    """Get list of supported file formats."""
    return {
        'upload': ['csv', 'ply', 'pcd', 'xyz'],
        'export': ['ply'],
        'animation': ['ply']
    } 