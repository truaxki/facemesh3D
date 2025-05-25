#!/usr/bin/env python3
"""Test Kabsch Algorithm and Data Filtering

Test script to verify the new data filtering functionality with Kabsch algorithm.
"""

import sys
import numpy as np
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent / "source"))

from data_filters import DataFilters


def create_test_data():
    """Create test point cloud data with known transformations."""
    print("🧪 Creating test data...")
    
    # Create a simple 3D shape (cube vertices)
    base_points = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 1]
    ], dtype=float)
    
    # Create frames with known transformations
    frames_data = []
    
    # Frame 0: Original (baseline)
    frames_data.append({
        'points': base_points.copy(),
        'colors': np.ones((len(base_points), 3)) * [1, 0, 0],  # Red
        'timestamp': 0.0,
        'frame_index': 0
    })
    
    # Frame 1: Rotated 45 degrees around Z-axis
    angle = np.pi / 4  # 45 degrees
    R_z = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    rotated_points = (R_z @ base_points.T).T
    frames_data.append({
        'points': rotated_points,
        'colors': np.ones((len(base_points), 3)) * [0, 1, 0],  # Green
        'timestamp': 1.0,
        'frame_index': 1
    })
    
    # Frame 2: Rotated and translated
    translated_points = rotated_points + np.array([2, 1, 0.5])
    frames_data.append({
        'points': translated_points,
        'colors': np.ones((len(base_points), 3)) * [0, 0, 1],  # Blue
        'timestamp': 2.0,
        'frame_index': 2
    })
    
    # Frame 3: Scaled and rotated
    scaled_rotated_points = (R_z @ (base_points * 1.5).T).T
    frames_data.append({
        'points': scaled_rotated_points,
        'colors': np.ones((len(base_points), 3)) * [1, 1, 0],  # Yellow
        'timestamp': 3.0,
        'frame_index': 3
    })
    
    print(f"✅ Created {len(frames_data)} test frames")
    return frames_data


def test_kabsch_algorithm():
    """Test the Kabsch algorithm implementation."""
    print("\n🎯 Testing Kabsch Algorithm")
    print("=" * 50)
    
    # Create two point sets with known transformation
    P = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ], dtype=float)
    
    # Rotate P by 90 degrees around Z-axis
    angle = np.pi / 2
    R_true = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    
    Q = (R_true @ P.T).T
    
    print(f"Original points P:\n{P}")
    print(f"Rotated points Q:\n{Q}")
    print(f"True rotation matrix:\n{R_true}")
    
    # Apply Kabsch algorithm
    R_kabsch, t_kabsch, rmsd = DataFilters.kabsch_algorithm(P, Q)
    
    print(f"\nKabsch results:")
    print(f"Computed rotation matrix:\n{R_kabsch}")
    print(f"Translation vector: {t_kabsch}")
    print(f"RMSD: {rmsd:.6f}")
    
    # Verify the result
    Q_aligned = DataFilters.apply_transformation(Q, R_kabsch, t_kabsch)
    print(f"\nAligned points:\n{Q_aligned}")
    print(f"Difference from original:\n{P - Q_aligned}")
    
    # Check if RMSD is close to zero
    if rmsd < 1e-10:
        print("✅ Kabsch algorithm test PASSED!")
    else:
        print(f"❌ Kabsch algorithm test FAILED! RMSD too high: {rmsd}")


def test_frame_alignment():
    """Test frame alignment using Kabsch algorithm."""
    print("\n🔄 Testing Frame Alignment")
    print("=" * 50)
    
    frames_data = create_test_data()
    
    # Print original frame positions
    print("Original frame centroids:")
    for i, frame in enumerate(frames_data):
        centroid = np.mean(frame['points'], axis=0)
        print(f"  Frame {i}: {centroid}")
    
    # Apply Kabsch alignment
    aligned_frames = DataFilters.align_frames_to_baseline(frames_data, baseline_frame_idx=0)
    
    # Print aligned frame positions
    print("\nAligned frame centroids:")
    for i, frame in enumerate(aligned_frames):
        centroid = np.mean(frame['points'], axis=0)
        print(f"  Frame {i}: {centroid}")
        
        # Check if transformation info was stored
        if 'kabsch_transform' in frame:
            rmsd = frame['kabsch_transform']['rmsd']
            print(f"    RMSD: {rmsd:.6f}")
    
    print("✅ Frame alignment test completed!")
    return aligned_frames


def test_filter_chain():
    """Test applying multiple filters in sequence."""
    print("\n🔧 Testing Filter Chain")
    print("=" * 50)
    
    frames_data = create_test_data()
    
    # Define filter chain
    filter_chain = [
        {
            'filter': 'kabsch_alignment',
            'params': {'baseline_frame_idx': 0}
        },
        {
            'filter': 'center_frames',
            'params': {}
        },
        {
            'filter': 'scale_frames',
            'params': {'scale_factor': 2.0}
        }
    ]
    
    # Apply filter chain
    filtered_frames = DataFilters.apply_filter_chain(frames_data, filter_chain)
    
    # Verify results
    print("Filter chain results:")
    for i, frame in enumerate(filtered_frames):
        points = frame['points']
        centroid = np.mean(points, axis=0)
        scale = np.mean(np.linalg.norm(points, axis=1))
        
        print(f"  Frame {i}:")
        print(f"    Centroid: {centroid}")
        print(f"    Average distance from origin: {scale:.4f}")
        
        # Check applied filters
        if 'applied_filters' in frame:
            filter_names = [f['filter'] for f in frame['applied_filters']]
            print(f"    Applied filters: {filter_names}")
    
    print("✅ Filter chain test completed!")


def test_outlier_removal():
    """Test outlier removal filter."""
    print("\n🧹 Testing Outlier Removal")
    print("=" * 50)
    
    # Create data with outliers
    normal_points = np.random.normal(0, 1, (100, 3))
    outliers = np.array([[10, 10, 10], [-10, -10, -10], [15, 0, 0]])
    all_points = np.vstack([normal_points, outliers])
    
    frames_data = [{
        'points': all_points,
        'colors': np.ones((len(all_points), 3)) * [0.5, 0.5, 0.5],
        'timestamp': 0.0,
        'frame_index': 0
    }]
    
    print(f"Original points: {len(all_points)}")
    
    # Apply outlier removal
    filtered_frames = DataFilters.remove_outliers(frames_data, std_threshold=2.0)
    
    filtered_points = filtered_frames[0]['points']
    outlier_info = filtered_frames[0]['outlier_filter']
    
    print(f"Filtered points: {len(filtered_points)}")
    print(f"Removed points: {outlier_info['removed_count']}")
    print(f"Distance threshold: {outlier_info['distance_threshold']:.4f}")
    
    if outlier_info['removed_count'] > 0:
        print("✅ Outlier removal test PASSED!")
    else:
        print("⚠️ No outliers removed - check threshold")


def test_available_filters():
    """Test getting available filters."""
    print("\n📋 Testing Available Filters")
    print("=" * 50)
    
    filters = DataFilters.get_available_filters()
    
    print("Available filters:")
    for filter_name, filter_info in filters.items():
        print(f"  {filter_name}:")
        print(f"    Name: {filter_info['name']}")
        print(f"    Description: {filter_info['description']}")
        print(f"    Parameters: {filter_info['parameters']}")
        print(f"    Use case: {filter_info['use_case']}")
        print()
    
    print(f"✅ Found {len(filters)} available filters")


def main():
    """Main test function."""
    print("🧪 Data Filters and Kabsch Algorithm Tests")
    print("=" * 60)
    
    try:
        test_kabsch_algorithm()
        test_frame_alignment()
        test_filter_chain()
        test_outlier_removal()
        test_available_filters()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 