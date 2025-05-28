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
    def align_frames_to_baseline(frames_data: List[Dict], baseline_frame_count: int = 30) -> List[Dict]:
        """
        Align all frames to a baseline computed from the average of the first N frames using Kabsch algorithm.
        
        Args:
            frames_data: List of frame dictionaries with 'points' and 'colors'
            baseline_frame_count: Number of initial frames to average for baseline (default: 30)
            
        Returns:
            List of aligned frame dictionaries
        """
        if not frames_data:
            raise ValueError("Empty frames data")
        
        # Determine actual number of frames to use for baseline
        actual_baseline_count = min(baseline_frame_count, len(frames_data))
        
        print(f"🎯 Computing baseline from average of first {actual_baseline_count} frames")
        print(f"📊 Total frames to align: {len(frames_data)}")
        
        # Compute average baseline points
        baseline_frames = frames_data[:actual_baseline_count]
        first_frame_point_count = len(baseline_frames[0]['points'])
        
        # Check that all baseline frames have the same number of points
        for i, frame in enumerate(baseline_frames):
            if len(frame['points']) != first_frame_point_count:
                print(f"⚠️ Baseline frame {i}: Point count mismatch ({len(frame['points'])} vs {first_frame_point_count})")
                raise ValueError(f"Inconsistent point counts in baseline frames")
        
        # Calculate average points across baseline frames
        baseline_points = np.zeros((first_frame_point_count, 3))
        for frame in baseline_frames:
            baseline_points += frame['points']
        baseline_points /= actual_baseline_count
        
        print(f"📍 Baseline computed from {actual_baseline_count} frames with {len(baseline_points)} points each")
        
        aligned_frames = []
        alignment_stats = []
        
        for i, frame_data in enumerate(frames_data):
            current_points = frame_data['points'].copy()
            
            if len(current_points) != len(baseline_points):
                print(f"⚠️ Frame {i}: Point count mismatch ({len(current_points)} vs {len(baseline_points)})")
                # For now, skip frames with different point counts
                # In future, could implement point correspondence matching
                aligned_frames.append(frame_data.copy())
                continue
            
            if i < actual_baseline_count:
                # For frames used in baseline computation, align to the computed average baseline
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
                    'baseline_type': f'average_of_{actual_baseline_count}_frames',
                    'is_baseline_frame': True
                }
            else:
                # Apply Kabsch alignment to computed baseline
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
                    'baseline_type': f'average_of_{actual_baseline_count}_frames',
                    'is_baseline_frame': False
                }
            
            alignment_stats.append({
                'frame_idx': i,
                'rmsd': rmsd,
                'is_baseline_contributor': i < actual_baseline_count
            })
            
            aligned_frames.append(aligned_frame)
        
        # Print alignment statistics
        baseline_rmsds = [stat['rmsd'] for stat in alignment_stats if stat['is_baseline_contributor']]
        other_rmsds = [stat['rmsd'] for stat in alignment_stats if not stat['is_baseline_contributor']]
        
        if baseline_rmsds:
            print(f"📈 Baseline frames alignment RMSD statistics:")
            print(f"   Mean: {np.mean(baseline_rmsds):.4f}")
            print(f"   Std:  {np.std(baseline_rmsds):.4f}")
            print(f"   Min:  {np.min(baseline_rmsds):.4f}")
            print(f"   Max:  {np.max(baseline_rmsds):.4f}")
        
        if other_rmsds:
            print(f"📈 Non-baseline frames alignment RMSD statistics:")
            print(f"   Mean: {np.mean(other_rmsds):.4f}")
            print(f"   Std:  {np.std(other_rmsds):.4f}")
            print(f"   Min:  {np.min(other_rmsds):.4f}")
            print(f"   Max:  {np.max(other_rmsds):.4f}")
        
        print(f"✅ Kabsch alignment complete using average baseline!")
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
                'description': 'Align all frames to a baseline computed from average of first N frames',
                'parameters': ['baseline_frame_count'],
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
    def calculate_post_filter_movement(frames_data: List[Dict]) -> List[Dict]:
        """
        Calculate frame-to-frame displacement after filters have been applied.
        This measures actual local movement after removing rigid body motion.
        
        Args:
            frames_data: List of filtered frame dictionaries
            
        Returns:
            List of frame dictionaries with post-filter movement data
        """
        if len(frames_data) < 2:
            print("⚠️ Need at least 2 frames to calculate movement")
            return frames_data
        
        print(f"📐 Calculating post-filter movement for {len(frames_data)} frames...")
        
        enhanced_frames = []
        all_displacements = []
        
        for i, frame_data in enumerate(frames_data):
            enhanced_frame = frame_data.copy()
            
            if i == 0:
                # First frame - no previous frame to compare
                num_points = len(frame_data['points'])
                enhanced_frame['post_filter_displacement'] = np.zeros(num_points)
                enhanced_frame['displacement_magnitude'] = np.zeros(num_points)
            else:
                # Calculate displacement from previous frame
                current_points = frame_data['points']
                previous_points = frames_data[i-1]['points']
                
                if len(current_points) != len(previous_points):
                    print(f"⚠️ Frame {i}: Point count mismatch, using zero displacement")
                    enhanced_frame['post_filter_displacement'] = np.zeros(len(current_points))
                    enhanced_frame['displacement_magnitude'] = np.zeros(len(current_points))
                else:
                    # Calculate 3D displacement vectors
                    displacement_vectors = current_points - previous_points
                    
                    # Calculate displacement magnitudes
                    displacement_magnitudes = np.linalg.norm(displacement_vectors, axis=1)
                    
                    enhanced_frame['post_filter_displacement'] = displacement_vectors
                    enhanced_frame['displacement_magnitude'] = displacement_magnitudes
                    
                    # Collect for global statistics
                    all_displacements.extend(displacement_magnitudes)
            
            enhanced_frames.append(enhanced_frame)
        
        # Calculate global displacement statistics for normalization
        if all_displacements:
            all_displacements = np.array(all_displacements)
            
            # Calculate statistics
            mean_disp = np.mean(all_displacements)
            std_disp = np.std(all_displacements)
            p95_disp = np.percentile(all_displacements, 95)
            p99_disp = np.percentile(all_displacements, 99)
            max_disp = np.max(all_displacements)
            
            print(f"📊 Post-filter displacement statistics:")
            print(f"   Mean: {mean_disp:.6f}")
            print(f"   Std:  {std_disp:.6f}")
            print(f"   95th percentile: {p95_disp:.6f}")
            print(f"   99th percentile: {p99_disp:.6f}")
            print(f"   Max: {max_disp:.6f}")
            
            # Add normalization metadata to all frames
            normalization_stats = {
                'mean_displacement': mean_disp,
                'std_displacement': std_disp,
                'p95_displacement': p95_disp,
                'p99_displacement': p99_disp,
                'max_displacement': max_disp
            }
            
            for frame in enhanced_frames:
                frame['displacement_stats'] = normalization_stats
        
        print(f"✅ Post-filter movement calculation complete!")
        return enhanced_frames
    
    @staticmethod
    def generate_post_filter_movement_colors(frames_data: List[Dict], normalization_method: str = 'percentile_95') -> List[Dict]:
        """
        Generate colors based on post-filter movement displacement.
        
        Args:
            frames_data: List of frame dictionaries with displacement data
            normalization_method: 'percentile_95', 'percentile_99', 'std_dev', or 'max'
            
        Returns:
            List of frame dictionaries with updated colors
        """
        print(f"🎨 Generating post-filter movement colors using {normalization_method} normalization...")
        
        colored_frames = []
        
        for frame_data in frames_data:
            colored_frame = frame_data.copy()
            
            if 'displacement_magnitude' not in frame_data:
                print("⚠️ No displacement data found, using default colors")
                num_points = len(frame_data['points'])
                colored_frame['colors'] = np.ones((num_points, 3)) * [0.7, 0.7, 0.9]
                colored_frames.append(colored_frame)
                continue
            
            displacement_magnitudes = frame_data['displacement_magnitude']
            stats = frame_data.get('displacement_stats', {})
            
            # Choose normalization strategy
            if normalization_method == 'percentile_95':
                norm_value = stats.get('p95_displacement', np.percentile(displacement_magnitudes, 95))
            elif normalization_method == 'percentile_99':
                norm_value = stats.get('p99_displacement', np.percentile(displacement_magnitudes, 99))
            elif normalization_method == 'std_dev':
                mean_val = stats.get('mean_displacement', np.mean(displacement_magnitudes))
                std_val = stats.get('std_displacement', np.std(displacement_magnitudes))
                norm_value = mean_val + 2 * std_val  # 2 standard deviations
            elif normalization_method == 'max':
                norm_value = stats.get('max_displacement', np.max(displacement_magnitudes))
            else:
                norm_value = stats.get('p95_displacement', np.percentile(displacement_magnitudes, 95))
            
            # Avoid division by zero
            if norm_value == 0:
                norm_value = 1.0
            
            # Normalize displacement magnitudes
            normalized_displacements = np.clip(displacement_magnitudes / norm_value, 0, 1)
            
            # Generate heat map colors: blue (static) -> green -> yellow -> red (high movement)
            colors = np.zeros((len(displacement_magnitudes), 3))
            
            for i, intensity in enumerate(normalized_displacements):
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
            
            colored_frame['colors'] = colors
            colored_frame['normalized_displacements'] = normalized_displacements
            colored_frame['normalization_method'] = normalization_method
            colored_frame['normalization_value'] = norm_value
            
            colored_frames.append(colored_frame)
        
        print(f"✅ Post-filter movement coloring complete!")
        return colored_frames
    
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
                baseline_count = params.get('baseline_frame_count', 30)
                result_frames = DataFilters.align_frames_to_baseline(result_frames, baseline_count)
            
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