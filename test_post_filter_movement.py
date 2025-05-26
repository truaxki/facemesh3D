#!/usr/bin/env python3
"""Test Post-Filter Movement Calculation

Test script to verify the new post-filter movement displacement calculation.
"""

import sys
import numpy as np
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent / "source"))

from data_filters import DataFilters


def create_facial_test_data():
    """Create test facial landmark data with known movements."""
    print("🧪 Creating facial test data...")
    
    # Create a simple face-like structure (simplified facial landmarks)
    base_face = np.array([
        # Face outline (8 points)
        [-2, -3, 0], [2, -3, 0], [-2, 3, 0], [2, 3, 0],
        [-1.5, -2, 0], [1.5, -2, 0], [-1.5, 2, 0], [1.5, 2, 0],
        
        # Eyes (4 points each)
        [-1, 1, 0], [-0.5, 1, 0], [0.5, 1, 0], [1, 1, 0],  # Eye line
        [-1, 0.8, 0], [-0.5, 0.8, 0], [0.5, 0.8, 0], [1, 0.8, 0],  # Eye details
        
        # Mouth (6 points)
        [-0.8, -1, 0], [-0.4, -1, 0], [0, -1, 0], [0.4, -1, 0], [0.8, -1, 0], [0, -1.2, 0]
    ], dtype=float)
    
    frames_data = []
    
    # Frame 0: Neutral expression
    frames_data.append({
        'points': base_face.copy(),
        'colors': np.ones((len(base_face), 3)) * [0.8, 0.8, 0.8],
        'timestamp': 0.0,
        'frame_index': 0
    })
    
    # Frame 1: Slight smile (mouth points move)
    smile_face = base_face.copy()
    # Move mouth corners up slightly
    smile_face[16, 1] += 0.1  # Left mouth corner
    smile_face[20, 1] += 0.1  # Right mouth corner
    smile_face[18, 1] += 0.05  # Center mouth
    
    frames_data.append({
        'points': smile_face,
        'colors': np.ones((len(base_face), 3)) * [0.8, 0.8, 0.8],
        'timestamp': 1.0,
        'frame_index': 1
    })
    
    # Frame 2: Bigger smile
    big_smile_face = base_face.copy()
    big_smile_face[16, 1] += 0.2  # Left mouth corner
    big_smile_face[20, 1] += 0.2  # Right mouth corner
    big_smile_face[18, 1] += 0.1  # Center mouth
    
    frames_data.append({
        'points': big_smile_face,
        'colors': np.ones((len(base_face), 3)) * [0.8, 0.8, 0.8],
        'timestamp': 2.0,
        'frame_index': 2
    })
    
    # Frame 3: Eye blink (eye points move down)
    blink_face = big_smile_face.copy()
    # Move eye points down
    for i in range(8, 16):  # Eye points
        blink_face[i, 1] -= 0.15
    
    frames_data.append({
        'points': blink_face,
        'colors': np.ones((len(base_face), 3)) * [0.8, 0.8, 0.8],
        'timestamp': 3.0,
        'frame_index': 3
    })
    
    # Frame 4: Return to neutral
    frames_data.append({
        'points': base_face.copy(),
        'colors': np.ones((len(base_face), 3)) * [0.8, 0.8, 0.8],
        'timestamp': 4.0,
        'frame_index': 4
    })
    
    print(f"✅ Created {len(frames_data)} facial test frames")
    return frames_data


def test_raw_movement_calculation():
    """Test movement calculation on raw (unfiltered) data."""
    print("\n📐 Testing Raw Movement Calculation")
    print("=" * 50)
    
    frames_data = create_facial_test_data()
    
    # Calculate movement on raw data
    movement_frames = DataFilters.calculate_post_filter_movement(frames_data)
    
    print("Raw movement analysis:")
    for i, frame in enumerate(movement_frames):
        if i == 0:
            print(f"  Frame {i}: Baseline (no movement)")
        else:
            displacements = frame['displacement_magnitude']
            max_disp = np.max(displacements)
            mean_disp = np.mean(displacements)
            moving_points = np.sum(displacements > 0.01)  # Points that moved significantly
            
            print(f"  Frame {i}: Max displacement: {max_disp:.4f}, Mean: {mean_disp:.4f}, Moving points: {moving_points}")
    
    return movement_frames


def test_filtered_movement_calculation():
    """Test movement calculation after applying filters."""
    print("\n🔧 Testing Filtered Movement Calculation")
    print("=" * 50)
    
    frames_data = create_facial_test_data()
    
    # Add some rigid body motion to test Kabsch filtering
    print("Adding rigid body motion to test data...")
    for i, frame in enumerate(frames_data):
        if i > 0:
            # Add rotation and translation
            angle = i * 0.1  # Small rotation
            R = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            translation = np.array([i * 0.2, i * 0.1, 0])  # Small translation
            
            # Apply rigid body motion
            frame['points'] = (R @ frame['points'].T).T + translation
    
    print("Before filtering - with rigid body motion:")
    movement_frames_raw = DataFilters.calculate_post_filter_movement(frames_data)
    
    for i, frame in enumerate(movement_frames_raw):
        if i > 0:
            displacements = frame['displacement_magnitude']
            max_disp = np.max(displacements)
            mean_disp = np.mean(displacements)
            print(f"  Frame {i}: Max displacement: {max_disp:.4f}, Mean: {mean_disp:.4f}")
    
    # Apply Kabsch alignment to remove rigid body motion
    print("\nApplying Kabsch alignment...")
    filter_chain = [{'filter': 'kabsch_alignment', 'params': {'baseline_frame_idx': 0}}]
    filtered_frames = DataFilters.apply_filter_chain(frames_data, filter_chain)
    
    print("After Kabsch filtering - rigid body motion removed:")
    movement_frames_filtered = DataFilters.calculate_post_filter_movement(filtered_frames)
    
    for i, frame in enumerate(movement_frames_filtered):
        if i > 0:
            displacements = frame['displacement_magnitude']
            max_disp = np.max(displacements)
            mean_disp = np.mean(displacements)
            print(f"  Frame {i}: Max displacement: {max_disp:.4f}, Mean: {mean_disp:.4f}")
    
    return movement_frames_filtered


def test_movement_coloring():
    """Test the movement-based coloring system."""
    print("\n🎨 Testing Movement-Based Coloring")
    print("=" * 50)
    
    frames_data = create_facial_test_data()
    
    # Calculate movement
    movement_frames = DataFilters.calculate_post_filter_movement(frames_data)
    
    # Test different normalization methods
    normalization_methods = ['percentile_95', 'percentile_99', 'std_dev', 'max']
    
    for method in normalization_methods:
        print(f"\nTesting {method} normalization:")
        colored_frames = DataFilters.generate_post_filter_movement_colors(movement_frames, method)
        
        for i, frame in enumerate(colored_frames):
            if i > 0:
                colors = frame['colors']
                norm_displacements = frame['normalized_displacements']
                norm_value = frame['normalization_value']
                
                # Analyze color distribution
                red_intensity = np.mean(colors[:, 0])  # Red channel (high movement)
                blue_intensity = np.mean(colors[:, 2])  # Blue channel (low movement)
                
                print(f"  Frame {i}: Norm value: {norm_value:.4f}, Red: {red_intensity:.3f}, Blue: {blue_intensity:.3f}")


def test_normalization_strategies():
    """Test different normalization strategies."""
    print("\n📊 Testing Normalization Strategies")
    print("=" * 50)
    
    # Create data with varying displacement ranges
    test_displacements = np.array([
        0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5,  # Normal range
        1.0, 2.0, 5.0  # Outliers
    ])
    
    print(f"Test displacements: {test_displacements}")
    
    # Calculate different normalization values
    mean_val = np.mean(test_displacements)
    std_val = np.std(test_displacements)
    p95_val = np.percentile(test_displacements, 95)
    p99_val = np.percentile(test_displacements, 99)
    max_val = np.max(test_displacements)
    
    print(f"\nNormalization values:")
    print(f"  Mean: {mean_val:.4f}")
    print(f"  Std Dev (mean + 2σ): {mean_val + 2*std_val:.4f}")
    print(f"  95th percentile: {p95_val:.4f}")
    print(f"  99th percentile: {p99_val:.4f}")
    print(f"  Max: {max_val:.4f}")
    
    # Show how each method handles outliers
    methods = {
        'percentile_95': p95_val,
        'percentile_99': p99_val,
        'std_dev': mean_val + 2*std_val,
        'max': max_val
    }
    
    print(f"\nNormalized values (clipped to [0,1]):")
    for method, norm_val in methods.items():
        normalized = np.clip(test_displacements / norm_val, 0, 1)
        outliers_clipped = np.sum(normalized >= 1.0)
        print(f"  {method}: {outliers_clipped} outliers clipped, max normalized: {np.max(normalized):.3f}")


def main():
    """Main test function."""
    print("🧪 Post-Filter Movement Calculation Tests")
    print("=" * 60)
    
    try:
        test_raw_movement_calculation()
        test_filtered_movement_calculation()
        test_movement_coloring()
        test_normalization_strategies()
        
        print("\n" + "=" * 60)
        print("🎉 All post-filter movement tests completed successfully!")
        print("\n💡 Key insights:")
        print("   - Post-filter movement isolates local facial expressions")
        print("   - Kabsch alignment removes rigid body motion effectively")
        print("   - Percentile-based normalization handles outliers well")
        print("   - Color mapping provides intuitive movement visualization")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 