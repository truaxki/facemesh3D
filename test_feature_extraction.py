#!/usr/bin/env python3
"""Test script for feature extraction functionality."""

import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

# Add source directory to path
sys.path.append('source')

from derived_features import DerivedFeatures


def create_sample_csv(filename: str, num_frames: int = 100, num_landmarks: int = 478):
    """Create a sample CSV file with facial landmark data."""
    print(f"Creating sample CSV: {filename}")
    
    # Create synthetic landmark data
    data = {}
    
    # Add time column
    data['Time (s)'] = np.linspace(0, num_frames/30, num_frames)  # 30 FPS
    
    # Create landmark coordinates with some simulated movement
    for landmark_idx in range(num_landmarks):
        # Base position
        base_x = np.random.uniform(-0.5, 0.5)
        base_y = np.random.uniform(-0.5, 0.5)
        base_z = np.random.uniform(-0.1, 0.1)
        
        # Add some movement over time
        t = np.linspace(0, 2*np.pi, num_frames)
        noise_scale = 0.01
        
        x_coords = base_x + noise_scale * np.sin(t + landmark_idx) + np.random.normal(0, 0.001, num_frames)
        y_coords = base_y + noise_scale * np.cos(t + landmark_idx) + np.random.normal(0, 0.001, num_frames)
        z_coords = base_z + noise_scale * np.sin(2*t + landmark_idx) + np.random.normal(0, 0.0005, num_frames)
        
        data[f'feat_{landmark_idx}_x'] = x_coords
        data[f'feat_{landmark_idx}_y'] = y_coords
        data[f'feat_{landmark_idx}_z'] = z_coords
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✅ Created {filename} with shape {df.shape}")
    return filename


def test_feature_parsing():
    """Test feature selection parsing."""
    print("\n🧪 Testing feature selection parsing...")
    
    # Test single feature
    result = DerivedFeatures.parse_feature_selection("1", [])
    assert result == [1], f"Expected [1], got {result}"
    print("✅ Single feature parsing works")
    
    # Test range
    result = DerivedFeatures.parse_feature_selection("1-5", [])
    assert result == [1, 2, 3, 4, 5], f"Expected [1,2,3,4,5], got {result}"
    print("✅ Range parsing works")
    
    # Test list
    result = DerivedFeatures.parse_feature_selection("1,3,5", [])
    assert result == [1, 3, 5], f"Expected [1,3,5], got {result}"
    print("✅ List parsing works")
    
    # Test cluster selection
    result = DerivedFeatures.parse_feature_selection("", ["noseTip"])
    assert 1 in result, f"Expected nose tip (1) in result, got {result}"
    print("✅ Cluster selection works")


def test_displacement_features():
    """Test displacement feature extraction."""
    print("\n🧪 Testing displacement feature extraction...")
    
    # Create sample data
    csv_file = create_sample_csv("test_sample.csv", num_frames=50)
    
    # Test configuration
    config = {
        'selected_indices': [1, 10, 20],  # Nose tip and a few others
        'displacement': {
            'enabled': True,
            'type': 'previous_frame',
            'baseline_frame_count': 5
        },
        'quaternion': {
            'enabled': False
        },
        'pipeline': []
    }
    
    # Extract features
    features_df = DerivedFeatures.extract_features_from_csv(csv_file, config)
    
    # Verify results
    expected_cols = ['displacement_landmark_1', 'displacement_landmark_10', 'displacement_landmark_20']
    for col in expected_cols:
        assert col in features_df.columns, f"Missing column: {col}"
    
    print(f"✅ Displacement features extracted. Shape: {features_df.shape}")
    print(f"✅ Feature columns: {[col for col in features_df.columns if col.startswith('displacement_')]}")
    
    # Clean up
    os.remove(csv_file)


def test_quaternion_features():
    """Test quaternion feature extraction."""
    print("\n🧪 Testing quaternion feature extraction...")
    
    # Create sample data
    csv_file = create_sample_csv("test_quaternion.csv", num_frames=30)
    
    # Test configuration with Kabsch alignment
    config = {
        'selected_indices': [1],
        'displacement': {
            'enabled': False
        },
        'quaternion': {
            'enabled': True,
            'baseline_frame_count': 5
        },
        'pipeline': [
            {
                'type': 'kabsch_alignment',
                'params': {'baseline_frame_count': 5}
            }
        ]
    }
    
    # Extract features
    features_df = DerivedFeatures.extract_features_from_csv(csv_file, config)
    
    # Verify results
    quaternion_cols = ['quaternion_x', 'quaternion_y', 'quaternion_z', 'quaternion_w']
    for col in quaternion_cols:
        assert col in features_df.columns, f"Missing quaternion column: {col}"
    
    print(f"✅ Quaternion features extracted. Shape: {features_df.shape}")
    print(f"✅ Quaternion columns: {quaternion_cols}")
    
    # Clean up
    os.remove(csv_file)


def test_combined_features():
    """Test combined displacement and quaternion features."""
    print("\n🧪 Testing combined feature extraction...")
    
    # Create sample data
    csv_file = create_sample_csv("test_combined.csv", num_frames=40)
    
    # Test configuration with both feature types
    config = {
        'selected_indices': [1, 2, 3],  # Nose area
        'displacement': {
            'enabled': True,
            'type': 'baseline',
            'baseline_frame_count': 5
        },
        'quaternion': {
            'enabled': True,
            'baseline_frame_count': 5
        },
        'pipeline': [
            {
                'type': 'rolling_average',
                'params': {'window_size': 3}
            },
            {
                'type': 'kabsch_alignment',
                'params': {'baseline_frame_count': 5}
            }
        ]
    }
    
    # Extract features
    features_df = DerivedFeatures.extract_features_from_csv(csv_file, config)
    
    # Verify results
    displacement_cols = [col for col in features_df.columns if col.startswith('displacement_')]
    quaternion_cols = [col for col in features_df.columns if col.startswith('quaternion_')]
    
    assert len(displacement_cols) == 3, f"Expected 3 displacement columns, got {len(displacement_cols)}"
    assert len(quaternion_cols) == 4, f"Expected 4 quaternion columns, got {len(quaternion_cols)}"
    
    print(f"✅ Combined features extracted. Shape: {features_df.shape}")
    print(f"✅ Displacement features: {len(displacement_cols)}")
    print(f"✅ Quaternion features: {len(quaternion_cols)}")
    
    # Save for inspection
    features_df.to_csv("test_output_features.csv", index=False)
    print(f"✅ Saved test output to: test_output_features.csv")
    
    # Clean up
    os.remove(csv_file)


def main():
    """Run all tests."""
    print("🚀 Starting feature extraction tests...")
    
    try:
        test_feature_parsing()
        test_displacement_features()
        test_quaternion_features()
        test_combined_features()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📋 Summary:")
        print("✅ Feature selection parsing works")
        print("✅ Displacement feature extraction works")
        print("✅ Quaternion feature extraction works")
        print("✅ Combined feature extraction works")
        print("✅ Processing pipeline works")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 