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
    
    @staticmethod
    def create_statistical_baseline_from_csv(csv_file_path: str, z_scale: float = 25.0) -> Dict:
        """
        Create a statistical baseline from a CSV file containing multiple frames.
        
        Args:
            csv_file_path: Path to CSV file with facial landmark data
            z_scale: Z-axis scaling factor
            
        Returns:
            Dictionary containing:
            - 'baseline_points': Mean coordinates for each landmark (N x 3)
            - 'std_dev': Standard deviation for each landmark (N x 3)
            - 'num_frames': Number of frames used
            - 'num_landmarks': Number of landmarks
            - 'source_file': Source CSV filename
        """
        try:
            # Load CSV data
            df = pd.read_csv(csv_file_path)
            
            # Sort by time if available
            if 'Time (s)' in df.columns:
                df = df.sort_values('Time (s)').reset_index(drop=True)
            
            # Get coordinate columns
            x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
            y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
            z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
            
            if not (x_cols and y_cols and z_cols):
                raise ValueError("CSV file does not contain facial landmark data (feat_N_x, feat_N_y, feat_N_z columns)")
            
            num_frames = len(df)
            num_landmarks = len(x_cols)
            
            if num_landmarks != len(y_cols) or num_landmarks != len(z_cols):
                raise ValueError("Inconsistent number of landmarks across x, y, z coordinates")
            
            print(f"📊 Processing baseline CSV: {num_frames} frames, {num_landmarks} landmarks")
            
            # Collect all frames data
            all_frames_points = np.zeros((num_frames, num_landmarks, 3))
            
            for frame_idx in range(num_frames):
                for landmark_idx in range(num_landmarks):
                    all_frames_points[frame_idx, landmark_idx] = [
                        df[x_cols[landmark_idx]].iloc[frame_idx],
                        df[y_cols[landmark_idx]].iloc[frame_idx],
                        df[z_cols[landmark_idx]].iloc[frame_idx] * z_scale
                    ]
            
            # Calculate statistics across all frames
            baseline_points = np.mean(all_frames_points, axis=0)  # Mean across frames
            std_dev = np.std(all_frames_points, axis=0)  # Standard deviation across frames
            
            # Calculate additional statistics
            min_coords = np.min(all_frames_points, axis=0)
            max_coords = np.max(all_frames_points, axis=0)
            
            print(f"✅ Statistical baseline created:")
            print(f"   Mean displacement range: {np.mean(std_dev):.4f}")
            print(f"   Max std deviation: {np.max(std_dev):.4f}")
            print(f"   Min std deviation: {np.min(std_dev):.4f}")
            
            return {
                'baseline_points': baseline_points,
                'std_dev': std_dev,
                'min_coords': min_coords,
                'max_coords': max_coords,
                'num_frames': num_frames,
                'num_landmarks': num_landmarks,
                'source_file': csv_file_path,
                'z_scale': z_scale,
                'statistics': {
                    'mean_std_dev': np.mean(std_dev),
                    'max_std_dev': np.max(std_dev),
                    'min_std_dev': np.min(std_dev),
                    'coordinate_range': {
                        'x': [float(np.min(min_coords[:, 0])), float(np.max(max_coords[:, 0]))],
                        'y': [float(np.min(min_coords[:, 1])), float(np.max(max_coords[:, 1]))],
                        'z': [float(np.min(min_coords[:, 2])), float(np.max(max_coords[:, 2]))]
                    }
                }
            }
            
        except Exception as e:
            print(f"❌ Error creating statistical baseline: {str(e)}")
            raise
    
    @staticmethod
    def align_frames_to_statistical_baseline(frames_data: List[Dict], statistical_baseline: Dict) -> List[Dict]:
        """
        Align all frames to a statistical baseline using Kabsch algorithm.
        
        Args:
            frames_data: List of frame dictionaries with 'points' and 'colors'
            statistical_baseline: Dictionary from create_statistical_baseline_from_csv()
            
        Returns:
            List of aligned frame dictionaries
        """
        baseline_points = statistical_baseline['baseline_points']
        aligned_frames = []
        alignment_stats = []
        
        print(f"🎯 Aligning {len(frames_data)} frames to statistical baseline")
        print(f"📊 Statistical baseline from {statistical_baseline['num_frames']} frames")
        print(f"📍 Baseline has {len(baseline_points)} landmarks")
        
        for i, frame_data in enumerate(frames_data):
            current_points = frame_data['points'].copy()
            
            if len(current_points) != len(baseline_points):
                print(f"⚠️ Frame {i}: Point count mismatch ({len(current_points)} vs {len(baseline_points)})")
                aligned_frames.append(frame_data.copy())
                continue
            
            # Apply Kabsch alignment to statistical baseline
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
                'baseline_type': 'statistical',
                'baseline_source': statistical_baseline['source_file'],
                'baseline_frames': statistical_baseline['num_frames']
            }
            
            alignment_stats.append({
                'frame_idx': i,
                'rmsd': rmsd,
                'baseline_type': 'statistical'
            })
            
            aligned_frames.append(aligned_frame)
        
        # Print alignment statistics
        rmsds = [stat['rmsd'] for stat in alignment_stats]
        if rmsds:
            print(f"📈 Statistical baseline alignment RMSD statistics:")
            print(f"   Mean: {np.mean(rmsds):.4f}")
            print(f"   Std:  {np.std(rmsds):.4f}")
            print(f"   Min:  {np.min(rmsds):.4f}")
            print(f"   Max:  {np.max(rmsds):.4f}")
        
        print(f"✅ Statistical baseline alignment complete!")
        return aligned_frames
    
    @staticmethod
    def generate_statistical_deviation_colors(frames_data: List[Dict], statistical_baseline: Dict) -> List[Dict]:
        """
        Generate colors based on statistical deviation from baseline mean.
        
        Color scheme:
        - Blue: Within 1 standard deviation (normal)
        - Yellow: 1-3 standard deviations (elevated)
        - Red: Beyond 3 standard deviations (extreme)
        
        Args:
            frames_data: List of frame dictionaries with 'points'
            statistical_baseline: Dictionary from create_statistical_baseline_from_csv()
            
        Returns:
            List of frame dictionaries with updated colors
        """
        if 'baseline_points' not in statistical_baseline or 'std_dev' not in statistical_baseline:
            raise ValueError("Statistical baseline must contain 'baseline_points' and 'std_dev'")
        
        baseline_points = statistical_baseline['baseline_points']
        baseline_std_dev = statistical_baseline['std_dev']
        
        print(f"🎨 Generating statistical deviation colors for {len(frames_data)} frames")
        print(f"📊 Using baseline with {len(baseline_points)} landmarks")
        
        colored_frames = []
        all_deviations = []
        
        for frame_idx, frame_data in enumerate(frames_data):
            current_points = frame_data['points']
            
            if len(current_points) != len(baseline_points):
                print(f"⚠️ Frame {frame_idx}: Point count mismatch, using default colors")
                colored_frame = frame_data.copy()
                colored_frame['colors'] = np.ones((len(current_points), 3)) * [0.7, 0.7, 0.9]
                colored_frames.append(colored_frame)
                continue
            
            # Calculate deviation from baseline mean for each point
            point_deviations = current_points - baseline_points  # (N, 3) array
            
            # Calculate magnitude of deviation for each point
            deviation_magnitudes = np.linalg.norm(point_deviations, axis=1)  # (N,) array
            
            # Calculate standard deviation magnitudes for normalization
            std_dev_magnitudes = np.linalg.norm(baseline_std_dev, axis=1)  # (N,) array
            
            # Avoid division by zero
            std_dev_magnitudes = np.where(std_dev_magnitudes == 0, 1e-6, std_dev_magnitudes)
            
            # Calculate how many standard deviations each point is from baseline
            normalized_deviations = deviation_magnitudes / std_dev_magnitudes  # (N,) array
            
            # Store for global statistics
            all_deviations.extend(normalized_deviations)
            
            # Generate colors based on deviation levels
            colors = np.zeros((len(current_points), 3))
            
            for i, deviation in enumerate(normalized_deviations):
                if deviation <= 1.0:
                    # Within 1 std dev - Blue gradient (darker blue = closer to baseline)
                    intensity = deviation  # 0 to 1
                    colors[i] = [0, 0, 1.0 - 0.3 * intensity]  # Dark blue to medium blue
                elif deviation <= 3.0:
                    # 1-3 std dev - Blue to Yellow gradient
                    intensity = (deviation - 1.0) / 2.0  # 0 to 1
                    colors[i] = [intensity, intensity, 1.0 - intensity]  # Blue to yellow
                else:
                    # Beyond 3 std dev - Yellow to Red gradient
                    intensity = min((deviation - 3.0) / 2.0, 1.0)  # 0 to 1, capped at 1
                    colors[i] = [1.0, 1.0 - intensity, 0]  # Yellow to red
            
            # Create colored frame
            colored_frame = frame_data.copy()
            colored_frame['colors'] = colors
            colored_frame['statistical_deviations'] = normalized_deviations
            colored_frame['deviation_magnitudes'] = deviation_magnitudes
            
            colored_frames.append(colored_frame)
        
        # Calculate and print global statistics
        if all_deviations:
            all_deviations = np.array(all_deviations)
            
            print(f"📈 Statistical deviation coloring statistics:")
            print(f"   Mean deviation: {np.mean(all_deviations):.3f} std devs")
            print(f"   Max deviation: {np.max(all_deviations):.3f} std devs")
            print(f"   Points > 1 std dev: {np.sum(all_deviations > 1.0)} ({100*np.sum(all_deviations > 1.0)/len(all_deviations):.1f}%)")
            print(f"   Points > 3 std dev: {np.sum(all_deviations > 3.0)} ({100*np.sum(all_deviations > 3.0)/len(all_deviations):.1f}%)")
        
        print(f"✅ Statistical deviation coloring complete!")
        return colored_frames 