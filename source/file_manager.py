"""File Manager Module

Handles all file I/O operations for point clouds.
Supports PLY, PCD, XYZ, and CSV formats with proper error handling.
Enhanced with facial landmark time series CSV support and data filtering.
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
from data_filters import DataFilters


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
    def _load_csv(uploaded_file, z_scale=50.0):
        """Load CSV file - detect format and handle appropriately."""
        content = StringIO(uploaded_file.getvalue().decode('utf-8'))
        df = pd.read_csv(content)
        
        # Check if this is a facial landmark time series CSV
        if FileManager._is_facial_landmark_csv(df):
            # For time series data, we'll return the first frame as preview
            # and provide info about the full dataset
            frames_data = FileManager._parse_facial_landmark_csv(df, 'movement', z_scale)
            if frames_data:
                return frames_data[0]['points'], frames_data[0]['colors']
            else:
                raise ValueError("No valid frames found in facial landmark CSV")
        else:
            # Standard X,Y,Z CSV format
            return FileManager._load_standard_csv(df)
    
    @staticmethod
    def _is_facial_landmark_csv(df):
        """Check if CSV contains facial landmark data (feat_N_x, feat_N_y, feat_N_z pattern)."""
        columns = df.columns.tolist()
        
        # Look for facial landmark pattern: feat_0_x, feat_0_y, feat_0_z, etc.
        feat_x_cols = [col for col in columns if col.startswith('feat_') and col.endswith('_x')]
        feat_y_cols = [col for col in columns if col.startswith('feat_') and col.endswith('_y')]
        feat_z_cols = [col for col in columns if col.startswith('feat_') and col.endswith('_z')]
        
        # Must have at least 10 facial landmarks and matching x,y,z columns
        return (len(feat_x_cols) >= 10 and 
                len(feat_x_cols) == len(feat_y_cols) == len(feat_z_cols))
    
    @staticmethod
    def _load_standard_csv(df):
        """Load standard CSV file with X,Y,Z and optional R,G,B columns."""
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
    def _parse_facial_landmark_csv(df, color_mode='movement', z_scale=50.0):
        """Parse facial landmark CSV into frame data."""
        columns = df.columns.tolist()
        
        # Find all feature indices
        feat_x_cols = sorted([col for col in columns if col.startswith('feat_') and col.endswith('_x')])
        feat_indices = []
        
        for x_col in feat_x_cols:
            # Extract feature number from feat_N_x format
            feat_num = x_col.replace('feat_', '').replace('_x', '')
            try:
                feat_idx = int(feat_num)
                feat_indices.append(feat_idx)
            except ValueError:
                continue
        
        feat_indices = sorted(feat_indices)
        print(f"📊 Found {len(feat_indices)} facial landmarks (feat_0 to feat_{max(feat_indices)})")
        print(f"🎯 Z-axis scaling factor: {z_scale}x")
        
        frames_data = []
        z_values_all = []  # Collect Z values for scaling analysis
        
        for row_idx, row in df.iterrows():
            points = []
            movement_data = []
            
            # Extract x,y,z coordinates and movement data for each feature
            for feat_idx in feat_indices:
                x_col = f'feat_{feat_idx}_x'
                y_col = f'feat_{feat_idx}_y'
                z_col = f'feat_{feat_idx}_z'
                
                # Movement difference columns
                xdiff_col = f'feat_{feat_idx}_xdiff'
                ydiff_col = f'feat_{feat_idx}_ydiff'
                zdiff_col = f'feat_{feat_idx}_zdiff'
                
                if x_col in columns and y_col in columns and z_col in columns:
                    x = row[x_col]
                    y = row[y_col]
                    z = row[z_col]
                    
                    # Skip invalid points
                    if pd.notna(x) and pd.notna(y) and pd.notna(z):
                        # Apply Z-axis scaling for better 3D visualization
                        z_scaled = z * z_scale
                        points.append([x, y, z_scaled])
                        z_values_all.append(z)  # Store original Z for analysis
                        
                        # Extract movement data if available
                        movement = {'xdiff': 0, 'ydiff': 0, 'zdiff': 0}
                        if xdiff_col in columns and pd.notna(row[xdiff_col]):
                            movement['xdiff'] = row[xdiff_col]
                        if ydiff_col in columns and pd.notna(row[ydiff_col]):
                            movement['ydiff'] = row[ydiff_col]
                        if zdiff_col in columns and pd.notna(row[zdiff_col]):
                            movement['zdiff'] = row[zdiff_col] * z_scale  # Scale Z movement too
                        
                        movement_data.append(movement)
            
            if len(points) > 0:
                points = np.array(points)
                
                # Generate colors based on mode
                colors = FileManager._generate_facial_colors(points, feat_indices, color_mode, movement_data)
                
                # Get timestamp if available
                timestamp = row.get('Time (s)', row_idx)
                
                frames_data.append({
                    'points': points,
                    'colors': colors,
                    'timestamp': timestamp,
                    'frame_index': row_idx,
                    'movement_data': movement_data
                })
        
        # Analyze Z-axis scaling results
        if z_values_all:
            z_values_all = np.array(z_values_all)
            z_range = np.max(z_values_all) - np.min(z_values_all)
            print(f"📏 Original Z range: {np.min(z_values_all):.4f} to {np.max(z_values_all):.4f} (range: {z_range:.4f})")
            print(f"📏 Scaled Z range: {np.min(z_values_all)*z_scale:.4f} to {np.max(z_values_all)*z_scale:.4f} (range: {z_range*z_scale:.4f})")
        
        print(f"✅ Parsed {len(frames_data)} frames from facial landmark data")
        return frames_data
    
    @staticmethod
    def _generate_facial_colors(points, feat_indices, color_mode='movement', movement_data=None):
        """Generate colors for facial landmark points."""
        num_points = len(points)
        
        if color_mode == 'movement' and movement_data:
            # Color by movement intensity (cool blue=static, hot red=high movement)
            movement_intensities = []
            
            for move_data in movement_data:
                # Calculate 3D movement magnitude
                xdiff = move_data.get('xdiff', 0)
                ydiff = move_data.get('ydiff', 0)
                zdiff = move_data.get('zdiff', 0)
                
                # Calculate movement magnitude (Euclidean distance)
                intensity = np.sqrt(xdiff**2 + ydiff**2 + zdiff**2)
                movement_intensities.append(intensity)
            
            movement_intensities = np.array(movement_intensities)
            
            # Normalize movement intensities
            if np.max(movement_intensities) > 0:
                # Use percentile-based normalization to handle outliers
                p95 = np.percentile(movement_intensities, 95)
                movement_norm = np.clip(movement_intensities / p95, 0, 1)
            else:
                movement_norm = np.zeros_like(movement_intensities)
            
            # Create heat map colors: blue (static) -> green -> yellow -> red (high movement)
            colors = np.zeros((num_points, 3))
            
            for i, intensity in enumerate(movement_norm):
                if intensity < 0.25:  # Very low movement - blue to cyan
                    colors[i] = [0, intensity*4, 1.0]
                elif intensity < 0.5:  # Low movement - cyan to green
                    t = (intensity - 0.25) * 4
                    colors[i] = [0, 1.0, 1.0 - t]
                elif intensity < 0.75:  # Medium movement - green to yellow
                    t = (intensity - 0.5) * 4
                    colors[i] = [t, 1.0, 0]
                else:  # High movement - yellow to red
                    t = (intensity - 0.75) * 4
                    colors[i] = [1.0, 1.0 - t, 0]
            
            print(f"🎨 Movement intensity range: {np.min(movement_intensities):.4f} to {np.max(movement_intensities):.4f}")
            
        elif color_mode == 'depth':
            # Color by Z depth (blue=close, red=far)
            z_values = points[:, 2]
            z_min, z_max = np.min(z_values), np.max(z_values)
            if z_max > z_min:
                z_norm = (z_values - z_min) / (z_max - z_min)
            else:
                z_norm = np.ones_like(z_values) * 0.5
            
            colors = np.zeros((num_points, 3))
            colors[:, 0] = z_norm        # Red for far
            colors[:, 2] = 1.0 - z_norm  # Blue for close
            colors[:, 1] = 0.3           # Slight green tint
            
        elif color_mode == 'regions':
            # Color by facial regions (simplified MediaPipe face mesh regions)
            colors = np.zeros((num_points, 3))
            
            for i, feat_idx in enumerate(feat_indices):
                if feat_idx < 17:  # Face contour
                    colors[i] = [1.0, 0.8, 0.6]  # Skin tone
                elif feat_idx < 27:  # Right eyebrow  
                    colors[i] = [0.6, 0.4, 0.2]  # Brown
                elif feat_idx < 36:  # Left eyebrow
                    colors[i] = [0.6, 0.4, 0.2]  # Brown
                elif feat_idx < 42:  # Right eye
                    colors[i] = [0.2, 0.6, 1.0]  # Blue
                elif feat_idx < 48:  # Left eye
                    colors[i] = [0.2, 0.6, 1.0]  # Blue
                elif feat_idx < 68:  # Mouth
                    colors[i] = [1.0, 0.4, 0.4]  # Red/pink
                else:  # Other features
                    colors[i] = [0.8, 0.8, 0.8]  # Light gray
                    
        elif color_mode == 'single':
            # Single color for all points
            colors = np.ones((num_points, 3)) * [0.7, 0.7, 0.9]  # Light blue-gray
            
        else:  # Default to movement if data available, otherwise depth
            if movement_data:
                colors = FileManager._generate_facial_colors(points, feat_indices, 'movement', movement_data)
            else:
                colors = FileManager._generate_facial_colors(points, feat_indices, 'depth')
        
        return colors
    
    @staticmethod
    def create_facial_animation_folder(uploaded_file, folder_name=None, color_mode='movement', max_frames=None, z_scale=50.0, filters=None):
        """Create animation folder from facial landmark CSV with optional filtering."""
        try:
            # Parse the CSV
            content = StringIO(uploaded_file.getvalue().decode('utf-8'))
            df = pd.read_csv(content)
            
            if not FileManager._is_facial_landmark_csv(df):
                raise ValueError("CSV does not contain facial landmark data")
            
            frames_data = FileManager._parse_facial_landmark_csv(df, color_mode, z_scale)
            
            if max_frames and len(frames_data) > max_frames:
                # Subsample frames evenly
                indices = np.linspace(0, len(frames_data)-1, max_frames, dtype=int)
                frames_data = [frames_data[i] for i in indices]
                print(f"📊 Subsampled to {len(frames_data)} frames")
            
            # Apply filters if specified
            if filters and len(filters) > 0:
                print(f"🔧 Applying {len(filters)} filter(s) to animation data...")
                frames_data = DataFilters.apply_filter_chain(frames_data, filters)
            
            # Generate folder name if not provided
            if not folder_name:
                base_name = uploaded_file.name.replace('.csv', '')
                subject = df.iloc[0].get('Subject Name', 'unknown') if 'Subject Name' in df.columns else 'unknown'
                test = df.iloc[0].get('Test Name', 'baseline') if 'Test Name' in df.columns else 'baseline'
                
                # Add filter suffix to folder name
                filter_suffix = ""
                if filters:
                    filter_names = [f['filter'] for f in filters]
                    if 'kabsch_alignment' in filter_names:
                        filter_suffix += "_aligned"
                    if 'center_frames' in filter_names:
                        filter_suffix += "_centered"
                    if 'remove_outliers' in filter_names:
                        filter_suffix += "_filtered"
                
                folder_name = f"facemesh_{subject}_{test}_{len(frames_data)}frames{filter_suffix}"
            
            # Create animation folder
            animations_dir = Path("animations")
            animations_dir.mkdir(exist_ok=True)
            
            folder_path = animations_dir / folder_name
            folder_path.mkdir(exist_ok=True)
            
            # Save each frame as PLY
            saved_frames = 0
            for frame_data in frames_data:
                timestamp = frame_data['timestamp']
                frame_idx = frame_data['frame_index']
                
                # Create filename with timestamp
                if isinstance(timestamp, (int, float)):
                    filename = f"frame_{frame_idx:04d}_t{timestamp:.3f}s.ply"
                else:
                    filename = f"frame_{frame_idx:04d}.ply"
                
                ply_path = folder_path / filename
                
                # Create and save point cloud
                pcd = FileManager.create_point_cloud(frame_data['points'], frame_data['colors'])
                success = o3d.io.write_point_cloud(str(ply_path), pcd)
                
                if success:
                    saved_frames += 1
            
            # Create metadata file
            metadata = {
                'type': 'facial_landmark_animation',
                'source_file': uploaded_file.name,
                'total_frames': int(len(frames_data)),
                'saved_frames': int(saved_frames),
                'color_mode': color_mode,
                'z_scale': float(z_scale),
                'landmarks_count': int(len(frames_data[0]['points'])) if frames_data else 0,
                'subject': str(df.iloc[0].get('Subject Name', 'unknown')) if 'Subject Name' in df.columns else 'unknown',
                'test': str(df.iloc[0].get('Test Name', 'baseline')) if 'Test Name' in df.columns else 'baseline',
                'duration_seconds': float(df.iloc[-1].get('Time (s)', len(frames_data))) if 'Time (s)' in df.columns else float(len(frames_data)),
                'applied_filters': filters if filters else [],
                'created_timestamp': time.time()
            }
            
            metadata_path = folder_path / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Created facial animation: {folder_path}")
            print(f"📊 {saved_frames} frames saved")
            if filters:
                print(f"🔧 Applied filters: {[f['filter'] for f in filters]}")
            
            return str(folder_path), saved_frames, metadata
            
        except Exception as e:
            raise RuntimeError(f"Error creating facial animation folder: {str(e)}")
    
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