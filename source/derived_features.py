"""Derived Features Module

Extracts derived features from facial landmark point cloud data for machine learning training.
Supports euclidean distance calculations, quaternion extraction from rotation matrices,
and modular feature processing pipelines.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union, Any
from scipy.spatial.transform import Rotation
from facial_clusters import FACIAL_CLUSTERS, get_cluster_indices
from data_filters import DataFilters


class DerivedFeatures:
    """Collection of derived feature extraction methods for ML training."""
    
    @staticmethod
    def parse_feature_selection(feature_input: str, selected_clusters: List[str] = None) -> List[int]:
        """
        Parse feature selection input and return list of landmark indices.
        
        Args:
            feature_input: String input like "320", "1-10", "20,34,7"
            selected_clusters: List of cluster names from facial_clusters.py
            
        Returns:
            List of landmark indices (0-477)
        """
        indices = set()
        
        # Parse text input
        if feature_input.strip():
            parts = feature_input.replace(' ', '').split(',')
            for part in parts:
                if '-' in part:
                    # Range input like "1-10"
                    try:
                        start, end = map(int, part.split('-'))
                        indices.update(range(start, end + 1))
                    except ValueError:
                        print(f"⚠️ Invalid range format: {part}")
                else:
                    # Single number
                    try:
                        indices.add(int(part))
                    except ValueError:
                        print(f"⚠️ Invalid number: {part}")
        
        # Add cluster selections
        if selected_clusters:
            for cluster_name in selected_clusters:
                cluster_indices = get_cluster_indices(cluster_name)
                indices.update(cluster_indices)
        
        # Validate indices are in MediaPipe range (0-477)
        valid_indices = [i for i in indices if 0 <= i <= 477]
        if len(valid_indices) != len(indices):
            print(f"⚠️ Some indices were out of range (0-477). Using {len(valid_indices)} valid indices.")
        
        return sorted(valid_indices)
    
    @staticmethod
    def calculate_displacement_features(frames_data: List[Dict], selected_indices: List[int], 
                                      displacement_type: str = 'previous_frame', 
                                      baseline_frame_count: int = 5) -> Dict[str, List[float]]:
        """
        Calculate displacement features for selected landmarks.
        
        Args:
            frames_data: List of frame dictionaries with 'points'
            selected_indices: List of landmark indices to analyze
            displacement_type: 'previous_frame' or 'baseline'
            baseline_frame_count: Number of frames for baseline calculation
            
        Returns:
            Dictionary with displacement features for each selected landmark
        """
        if len(frames_data) < 2:
            print("⚠️ Need at least 2 frames for displacement calculation")
            return {}
        
        print(f"📐 Calculating {displacement_type} displacement for {len(selected_indices)} landmarks...")
        
        # Calculate baseline if needed
        baseline_points = None
        if displacement_type == 'baseline':
            actual_baseline_count = min(baseline_frame_count, len(frames_data))
            baseline_frames = frames_data[:actual_baseline_count]
            
            # Average the selected points across baseline frames
            baseline_sum = np.zeros((len(selected_indices), 3))
            for frame in baseline_frames:
                selected_points = frame['points'][selected_indices]
                baseline_sum += selected_points
            baseline_points = baseline_sum / actual_baseline_count
        
        # Initialize feature dictionaries
        displacement_features = {}
        for i, landmark_idx in enumerate(selected_indices):
            displacement_features[f'displacement_landmark_{landmark_idx}'] = []
        
        # Calculate displacements
        for frame_idx, frame_data in enumerate(frames_data):
            current_points = frame_data['points'][selected_indices]
            
            if displacement_type == 'previous_frame':
                if frame_idx == 0:
                    # First frame - no displacement
                    for i, landmark_idx in enumerate(selected_indices):
                        displacement_features[f'displacement_landmark_{landmark_idx}'].append(0.0)
                else:
                    # Calculate displacement from previous frame
                    previous_points = frames_data[frame_idx - 1]['points'][selected_indices]
                    displacements = np.linalg.norm(current_points - previous_points, axis=1)
                    
                    for i, landmark_idx in enumerate(selected_indices):
                        displacement_features[f'displacement_landmark_{landmark_idx}'].append(float(displacements[i]))
                        
            elif displacement_type == 'baseline':
                # Calculate displacement from baseline
                displacements = np.linalg.norm(current_points - baseline_points, axis=1)
                
                for i, landmark_idx in enumerate(selected_indices):
                    displacement_features[f'displacement_landmark_{landmark_idx}'].append(float(displacements[i]))
        
        print(f"✅ Displacement calculation complete!")
        return displacement_features
    
    @staticmethod
    def extract_quaternion_features(frames_data: List[Dict], baseline_frame_count: int = 5) -> Dict[str, List[float]]:
        """
        Extract quaternion features from Kabsch rotation matrices.
        
        Args:
            frames_data: List of frame dictionaries (should have kabsch transform data)
            baseline_frame_count: Number of frames for baseline calculation
            
        Returns:
            Dictionary with quaternion features [x, y, z, w]
        """
        print(f"🔄 Extracting quaternion features from rotation matrices...")
        
        # Check if frames have Kabsch transform data
        has_transforms = any('kabsch_transform' in frame or 'kabsch_umeyama_transform' in frame 
                           for frame in frames_data)
        
        if not has_transforms:
            print("⚠️ No Kabsch transform data found. Applying Kabsch alignment first...")
            frames_data = DataFilters.align_frames_to_baseline(frames_data, baseline_frame_count)
        
        # Initialize quaternion features
        quaternion_features = {
            'quaternion_x': [],
            'quaternion_y': [],
            'quaternion_z': [],
            'quaternion_w': []
        }
        
        # Extract quaternions from rotation matrices
        for frame_data in frames_data:
            # Get rotation matrix from transform data
            rotation_matrix = None
            
            if 'kabsch_transform' in frame_data:
                rotation_matrix = frame_data['kabsch_transform']['rotation_matrix']
            elif 'kabsch_umeyama_transform' in frame_data:
                rotation_matrix = frame_data['kabsch_umeyama_transform']['rotation_matrix']
            
            if rotation_matrix is not None:
                # Convert rotation matrix to quaternion using scipy
                r = Rotation.from_matrix(rotation_matrix)
                quaternion = r.as_quat()  # Returns [x, y, z, w] format
                
                quaternion_features['quaternion_x'].append(float(quaternion[0]))
                quaternion_features['quaternion_y'].append(float(quaternion[1]))
                quaternion_features['quaternion_z'].append(float(quaternion[2]))
                quaternion_features['quaternion_w'].append(float(quaternion[3]))
            else:
                # No rotation matrix found - use identity quaternion
                quaternion_features['quaternion_x'].append(0.0)
                quaternion_features['quaternion_y'].append(0.0)
                quaternion_features['quaternion_z'].append(0.0)
                quaternion_features['quaternion_w'].append(1.0)
        
        print(f"✅ Quaternion extraction complete!")
        return quaternion_features
    
    @staticmethod
    def create_processing_pipeline(pipeline_config: List[Dict]) -> callable:
        """
        Create a processing pipeline function based on configuration.
        
        Args:
            pipeline_config: List of processing steps with their parameters
            
        Returns:
            Function that processes frames_data through the pipeline
        """
        def process_pipeline(frames_data: List[Dict]) -> List[Dict]:
            result_frames = frames_data.copy()
            
            for step in pipeline_config:
                step_type = step['type']
                params = step.get('params', {})
                
                print(f"🔧 Pipeline step: {step_type}")
                
                if step_type == 'rolling_average':
                    window_size = params.get('window_size', 3)
                    result_frames = DataFilters.apply_rolling_average_smoothing(result_frames, window_size)
                
                elif step_type == 'kabsch_alignment':
                    baseline_count = params.get('baseline_frame_count', 5)
                    result_frames = DataFilters.align_frames_to_baseline(result_frames, baseline_count)
                
                elif step_type == 'kabsch_umeyama_alignment':
                    baseline_count = params.get('baseline_frame_count', 5)
                    result_frames = DataFilters.align_frames_to_baseline_umeyama(result_frames, baseline_count)
                
                else:
                    print(f"⚠️ Unknown pipeline step: {step_type}")
            
            return result_frames
        
        return process_pipeline
    
    @staticmethod
    def extract_features_from_csv(csv_path: str, feature_extraction_config: Dict) -> pd.DataFrame:
        """
        Extract derived features from a CSV file based on configuration.
        
        Args:
            csv_path: Path to CSV file
            feature_extraction_config: Configuration for feature extraction
            
        Returns:
            DataFrame with derived features
        """
        print(f"📊 Extracting features from {csv_path}...")
        
        # Load CSV data
        df = pd.read_csv(csv_path)
        if 'Time (s)' in df.columns:
            df = df.sort_values('Time (s)').reset_index(drop=True)
        
        # Parse CSV to point cloud format
        frames_data = DerivedFeatures._parse_csv_to_frames(df)
        
        # Apply processing pipeline
        pipeline_config = feature_extraction_config.get('pipeline', [])
        if pipeline_config:
            process_pipeline = DerivedFeatures.create_processing_pipeline(pipeline_config)
            frames_data = process_pipeline(frames_data)
        
        # Extract features
        all_features = {}
        
        # Add source information
        all_features['source_file'] = [csv_path] * len(frames_data)
        all_features['frame_index'] = list(range(len(frames_data)))
        
        # Add time information if available
        if 'Time (s)' in df.columns:
            all_features['time_seconds'] = df['Time (s)'].tolist()
        
        # Extract displacement features
        displacement_config = feature_extraction_config.get('displacement', {})
        if displacement_config.get('enabled', False):
            selected_indices = displacement_config['selected_indices']
            displacement_type = displacement_config.get('type', 'previous_frame')
            baseline_count = displacement_config.get('baseline_frame_count', 5)
            
            displacement_features = DerivedFeatures.calculate_displacement_features(
                frames_data, selected_indices, displacement_type, baseline_count
            )
            all_features.update(displacement_features)
        
        # Extract quaternion features
        quaternion_config = feature_extraction_config.get('quaternion', {})
        if quaternion_config.get('enabled', False):
            baseline_count = quaternion_config.get('baseline_frame_count', 5)
            quaternion_features = DerivedFeatures.extract_quaternion_features(frames_data, baseline_count)
            all_features.update(quaternion_features)
        
        # Create DataFrame
        features_df = pd.DataFrame(all_features)
        
        print(f"✅ Feature extraction complete! Shape: {features_df.shape}")
        return features_df
    
    @staticmethod
    def _parse_csv_to_frames(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Parse CSV dataframe to frames format (internal helper).
        
        Args:
            df: CSV dataframe with feat_*_x, feat_*_y, feat_*_z columns
            
        Returns:
            List of frame dictionaries with 'points'
        """
        x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
        y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
        z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
        
        frames = []
        for i in range(len(df)):
            points = np.zeros((len(x_cols), 3))
            for j in range(len(x_cols)):
                points[j] = [
                    df[x_cols[j]].iloc[i],
                    df[y_cols[j]].iloc[i],
                    df[z_cols[j]].iloc[i]
                ]
            frames.append({
                'points': points,
                'colors': None
            })
        
        return frames
    
    @staticmethod
    def create_training_labels(file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Create training labels from file paths for Subject Name and Test Name prediction.
        
        Args:
            file_paths: List of CSV file paths
            
        Returns:
            Dictionary with subject and test name labels
        """
        subjects = []
        test_names = []
        
        for file_path in file_paths:
            # Extract filename without extension
            filename = file_path.split('/')[-1].replace('.csv', '')
            
            # Try to parse subject and test info from filename
            # Assuming format like "subject1_test2" or similar
            parts = filename.split('_')
            if len(parts) >= 2:
                subject = parts[0]
                test_name = '_'.join(parts[1:])
            else:
                subject = filename
                test_name = filename
            
            subjects.append(subject)
            test_names.append(test_name)
        
        return {
            'subject_name': subjects,
            'test_name': test_names
        }
    
    @staticmethod
    def get_available_clusters() -> Dict[str, List[int]]:
        """Get available facial clusters for feature selection."""
        return FACIAL_CLUSTERS.copy()
    
    @staticmethod
    def validate_feature_config(config: Dict) -> Tuple[bool, str]:
        """
        Validate feature extraction configuration.
        
        Args:
            config: Feature extraction configuration
            
        Returns:
            (is_valid, error_message)
        """
        # Check if at least one feature type is enabled
        has_displacement = config.get('displacement', {}).get('enabled', False)
        has_quaternion = config.get('quaternion', {}).get('enabled', False)
        
        if not (has_displacement or has_quaternion):
            return False, "At least one feature type (displacement or quaternion) must be enabled"
        
        # Validate displacement config
        if has_displacement:
            displacement_config = config['displacement']
            selected_indices = displacement_config.get('selected_indices', [])
            if not selected_indices:
                return False, "Displacement features require selected landmark indices"
            
            # Check indices are valid
            invalid_indices = [i for i in selected_indices if not (0 <= i <= 477)]
            if invalid_indices:
                return False, f"Invalid landmark indices: {invalid_indices}. Must be 0-477."
        
        return True, "" 