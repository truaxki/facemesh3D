"""Data Filters Module

Provides filtering and transformation operations for point cloud data.
Includes Kabsch algorithm for rigid body alignment and other matrix operations.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
from scipy.spatial.distance import cdist
from scipy.linalg import svd, det


class DataFilters:
    """Collection of data filtering and transformation operations."""
    
    @staticmethod
    def kabsch_algorithm(P: np.ndarray, Q: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Kabsch algorithm for optimal rotation matrix calculation.
        
        Finds the optimal rotation matrix that minimizes RMSD between two point sets.
        Based on: https://en.wikipedia.org/wiki/Kabsch_algorithm
        
        Args:
            P: Reference point set (N x 3)
            Q: Point set to align to P (N x 3)
            
        Returns:
            R: Optimal rotation matrix (3 x 3)
            t: Translation vector (3,)
            rmsd: Root mean square deviation after alignment
        """
        assert P.shape == Q.shape, "Point sets must have same shape"
        assert P.shape[1] == 3, "Points must be 3D"
        
        # Step 1: Center both point sets (translation)
        centroid_P = np.mean(P, axis=0)
        centroid_Q = np.mean(Q, axis=0)
        
        P_centered = P - centroid_P
        Q_centered = Q - centroid_Q
        
        # Step 2: Compute cross-covariance matrix H
        H = P_centered.T @ Q_centered
        
        # Step 3: Singular Value Decomposition
        U, S, Vt = svd(H)
        
        # Step 4: Compute rotation matrix
        # Check for reflection case
        d = det(U @ Vt)
        
        if d < 0:
            # Reflection case - flip the last column of U
            U[:, -1] *= -1
        
        R = U @ Vt
        
        # Step 5: Compute translation
        t = centroid_P - R @ centroid_Q
        
        # Step 6: Calculate RMSD
        Q_aligned = (R @ Q_centered.T).T + centroid_P
        rmsd = np.sqrt(np.mean(np.sum((P - Q_aligned)**2, axis=1)))
        
        return R, t, rmsd
    
    @staticmethod
    def apply_transformation(points: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
        """
        Apply rotation and translation to point cloud.
        
        Args:
            points: Point cloud (N x 3)
            R: Rotation matrix (3 x 3)
            t: Translation vector (3,)
            
        Returns:
            Transformed points (N x 3)
        """
        return (R @ points.T).T + t
    
    @staticmethod
    def align_frames_to_baseline(frames_data: List[Dict], baseline_frame_idx: int = 0) -> List[Dict]:
        """
        Align all frames to a baseline frame using Kabsch algorithm.
        
        Args:
            frames_data: List of frame dictionaries with 'points' and 'colors'
            baseline_frame_idx: Index of frame to use as reference (default: 0)
            
        Returns:
            List of aligned frame dictionaries
        """
        if not frames_data or len(frames_data) <= baseline_frame_idx:
            raise ValueError("Invalid baseline frame index or empty frames data")
        
        baseline_points = frames_data[baseline_frame_idx]['points'].copy()
        aligned_frames = []
        alignment_stats = []
        
        print(f"🎯 Aligning {len(frames_data)} frames to baseline frame {baseline_frame_idx}")
        print(f"📊 Baseline frame has {len(baseline_points)} points")
        
        for i, frame_data in enumerate(frames_data):
            current_points = frame_data['points'].copy()
            
            if len(current_points) != len(baseline_points):
                print(f"⚠️ Frame {i}: Point count mismatch ({len(current_points)} vs {len(baseline_points)})")
                # For now, skip frames with different point counts
                # In future, could implement point correspondence matching
                aligned_frames.append(frame_data.copy())
                continue
            
            if i == baseline_frame_idx:
                # Baseline frame - no transformation needed
                aligned_frame = frame_data.copy()
                rmsd = 0.0
            else:
                # Apply Kabsch alignment
                R, t, rmsd = DataFilters.kabsch_algorithm(baseline_points, current_points)
                
                # Transform points
                aligned_points = DataFilters.apply_transformation(current_points, R, t)
                
                # Create aligned frame
                aligned_frame = frame_data.copy()
                aligned_frame['points'] = aligned_points
                
                # Store transformation info
                aligned_frame['kabsch_transform'] = {
                    'rotation_matrix': R,
                    'translation_vector': t,
                    'rmsd': rmsd,
                    'baseline_frame': baseline_frame_idx
                }
            
            alignment_stats.append({
                'frame_idx': i,
                'rmsd': rmsd,
                'is_baseline': i == baseline_frame_idx
            })
            
            aligned_frames.append(aligned_frame)
        
        # Print alignment statistics
        rmsds = [stat['rmsd'] for stat in alignment_stats if not stat['is_baseline']]
        if rmsds:
            print(f"📈 Alignment RMSD statistics:")
            print(f"   Mean: {np.mean(rmsds):.4f}")
            print(f"   Std:  {np.std(rmsds):.4f}")
            print(f"   Min:  {np.min(rmsds):.4f}")
            print(f"   Max:  {np.max(rmsds):.4f}")
        
        print(f"✅ Kabsch alignment complete!")
        return aligned_frames
    
    @staticmethod
    def center_frames(frames_data: List[Dict]) -> List[Dict]:
        """
        Center all frames at origin (remove translation).
        
        Args:
            frames_data: List of frame dictionaries
            
        Returns:
            List of centered frame dictionaries
        """
        centered_frames = []
        
        for frame_data in frames_data:
            points = frame_data['points'].copy()
            centroid = np.mean(points, axis=0)
            centered_points = points - centroid
            
            centered_frame = frame_data.copy()
            centered_frame['points'] = centered_points
            centered_frame['center_transform'] = {
                'original_centroid': centroid
            }
            
            centered_frames.append(centered_frame)
        
        return centered_frames
    
    @staticmethod
    def scale_frames(frames_data: List[Dict], scale_factor: float) -> List[Dict]:
        """
        Scale all frames by a constant factor.
        
        Args:
            frames_data: List of frame dictionaries
            scale_factor: Scaling factor (1.0 = no change)
            
        Returns:
            List of scaled frame dictionaries
        """
        scaled_frames = []
        
        for frame_data in frames_data:
            points = frame_data['points'].copy()
            scaled_points = points * scale_factor
            
            scaled_frame = frame_data.copy()
            scaled_frame['points'] = scaled_points
            scaled_frame['scale_transform'] = {
                'scale_factor': scale_factor
            }
            
            scaled_frames.append(scaled_frame)
        
        return scaled_frames
    
    @staticmethod
    def remove_outliers(frames_data: List[Dict], std_threshold: float = 2.0) -> List[Dict]:
        """
        Remove outlier points based on distance from centroid.
        
        Args:
            frames_data: List of frame dictionaries
            std_threshold: Standard deviation threshold for outlier detection
            
        Returns:
            List of filtered frame dictionaries
        """
        filtered_frames = []
        
        for frame_data in frames_data:
            points = frame_data['points'].copy()
            colors = frame_data.get('colors', None)
            
            # Calculate distances from centroid
            centroid = np.mean(points, axis=0)
            distances = np.linalg.norm(points - centroid, axis=1)
            
            # Find outliers
            mean_dist = np.mean(distances)
            std_dist = np.std(distances)
            threshold = mean_dist + std_threshold * std_dist
            
            # Keep points within threshold
            valid_mask = distances <= threshold
            filtered_points = points[valid_mask]
            filtered_colors = colors[valid_mask] if colors is not None else None
            
            # Create filtered frame
            filtered_frame = frame_data.copy()
            filtered_frame['points'] = filtered_points
            if filtered_colors is not None:
                filtered_frame['colors'] = filtered_colors
            
            filtered_frame['outlier_filter'] = {
                'original_count': len(points),
                'filtered_count': len(filtered_points),
                'removed_count': len(points) - len(filtered_points),
                'std_threshold': std_threshold,
                'distance_threshold': threshold
            }
            
            filtered_frames.append(filtered_frame)
        
        return filtered_frames
    
    @staticmethod
    def apply_custom_matrix(frames_data: List[Dict], matrix: np.ndarray) -> List[Dict]:
        """
        Apply a custom transformation matrix to all frames.
        
        Args:
            frames_data: List of frame dictionaries
            matrix: 4x4 transformation matrix or 3x3 rotation matrix
            
        Returns:
            List of transformed frame dictionaries
        """
        transformed_frames = []
        
        for frame_data in frames_data:
            points = frame_data['points'].copy()
            
            if matrix.shape == (4, 4):
                # Homogeneous transformation matrix
                # Convert points to homogeneous coordinates
                points_homo = np.hstack([points, np.ones((len(points), 1))])
                transformed_homo = (matrix @ points_homo.T).T
                transformed_points = transformed_homo[:, :3]
            elif matrix.shape == (3, 3):
                # 3x3 rotation matrix
                transformed_points = (matrix @ points.T).T
            else:
                raise ValueError("Matrix must be 3x3 or 4x4")
            
            # Create transformed frame
            transformed_frame = frame_data.copy()
            transformed_frame['points'] = transformed_points
            transformed_frame['custom_transform'] = {
                'matrix': matrix,
                'matrix_shape': matrix.shape
            }
            
            transformed_frames.append(transformed_frame)
        
        return transformed_frames
    
    @staticmethod
    def get_available_filters() -> Dict[str, Dict]:
        """
        Get list of available filters with descriptions.
        
        Returns:
            Dictionary of filter names and their descriptions
        """
        return {
            'kabsch_alignment': {
                'name': 'Kabsch Alignment',
                'description': 'Align all frames to a baseline frame using optimal rotation',
                'parameters': ['baseline_frame_idx'],
                'use_case': 'Remove rigid body motion, focus on shape changes'
            },
            'center_frames': {
                'name': 'Center Frames',
                'description': 'Center all frames at origin (remove translation)',
                'parameters': [],
                'use_case': 'Remove translational motion'
            },
            'scale_frames': {
                'name': 'Scale Frames',
                'description': 'Scale all frames by constant factor',
                'parameters': ['scale_factor'],
                'use_case': 'Normalize size or enhance/reduce scale'
            },
            'remove_outliers': {
                'name': 'Remove Outliers',
                'description': 'Remove points far from centroid',
                'parameters': ['std_threshold'],
                'use_case': 'Clean noisy data'
            },
            'custom_matrix': {
                'name': 'Custom Matrix Transform',
                'description': 'Apply custom transformation matrix',
                'parameters': ['matrix'],
                'use_case': 'Advanced transformations'
            }
        }
    
    @staticmethod
    def apply_filter_chain(frames_data: List[Dict], filter_chain: List[Dict]) -> List[Dict]:
        """
        Apply a chain of filters in sequence.
        
        Args:
            frames_data: List of frame dictionaries
            filter_chain: List of filter configurations
                         Each item: {'filter': 'filter_name', 'params': {...}}
        
        Returns:
            List of filtered frame dictionaries
        """
        result_frames = frames_data.copy()
        applied_filters = []
        
        for filter_config in filter_chain:
            filter_name = filter_config['filter']
            params = filter_config.get('params', {})
            
            print(f"🔧 Applying filter: {filter_name}")
            
            if filter_name == 'kabsch_alignment':
                baseline_idx = params.get('baseline_frame_idx', 0)
                result_frames = DataFilters.align_frames_to_baseline(result_frames, baseline_idx)
            
            elif filter_name == 'center_frames':
                result_frames = DataFilters.center_frames(result_frames)
            
            elif filter_name == 'scale_frames':
                scale_factor = params.get('scale_factor', 1.0)
                result_frames = DataFilters.scale_frames(result_frames, scale_factor)
            
            elif filter_name == 'remove_outliers':
                std_threshold = params.get('std_threshold', 2.0)
                result_frames = DataFilters.remove_outliers(result_frames, std_threshold)
            
            elif filter_name == 'custom_matrix':
                matrix = params.get('matrix')
                if matrix is not None:
                    result_frames = DataFilters.apply_custom_matrix(result_frames, matrix)
            
            else:
                print(f"⚠️ Unknown filter: {filter_name}")
                continue
            
            applied_filters.append(filter_config)
        
        # Add filter chain metadata to all frames
        for frame in result_frames:
            frame['applied_filters'] = applied_filters
        
        print(f"✅ Filter chain complete! Applied {len(applied_filters)} filters.")
        return result_frames 