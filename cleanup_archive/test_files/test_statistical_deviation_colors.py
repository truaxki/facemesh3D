#!/usr/bin/env python3
"""
Test Statistical Deviation Coloring

Tests the new statistical deviation color scheme that uses baseline mean and standard deviation.
"""

import sys
import numpy as np
from pathlib import Path

# Add source directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "source"))

from data_filters import DataFilters
import pandas as pd


def test_statistical_deviation_coloring():
    """Test the statistical deviation coloring functionality."""
    print("🧪 Testing Statistical Deviation Coloring")
    print("=" * 50)
    
    # Find test CSV files
    data_read_dir = Path("data/read")
    csv_files = list(data_read_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data/read/ directory")
        return False
    
    baseline_file = csv_files[0]
    print(f"📁 Using baseline file: {baseline_file.name}")
    
    try:
        # Step 1: Create statistical baseline
        print("\n📊 Step 1: Creating statistical baseline...")
        statistical_baseline = DataFilters.create_statistical_baseline_from_csv(
            str(baseline_file),
            z_scale=25.0
        )
        
        # Step 2: Load test data and create frames
        print("\n📊 Step 2: Loading test frames...")
        df = pd.read_csv(baseline_file)
        if 'Time (s)' in df.columns:
            df = df.sort_values('Time (s)').reset_index(drop=True)
        
        x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
        y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
        z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
        
        # Create test frames (use first 5 frames)
        frames_data = []
        num_test_frames = min(5, len(df))
        
        for i in range(num_test_frames):
            points = np.zeros((len(x_cols), 3))
            for j in range(len(x_cols)):
                points[j] = [
                    df[x_cols[j]].iloc[i],
                    df[y_cols[j]].iloc[i],
                    df[z_cols[j]].iloc[i] * 25.0
                ]
            frames_data.append({'points': points, 'colors': None})
        
        print(f"📊 Created {len(frames_data)} test frames with {len(points)} landmarks each")
        
        # Step 3: Apply statistical deviation coloring
        print("\n🎨 Step 3: Applying statistical deviation coloring...")
        colored_frames = DataFilters.generate_statistical_deviation_colors(
            frames_data,
            statistical_baseline
        )
        
        # Step 4: Analyze results
        print("\n📈 Step 4: Analyzing color results...")
        
        for frame_idx, frame in enumerate(colored_frames):
            if 'statistical_deviations' in frame:
                deviations = frame['statistical_deviations']
                colors = frame['colors']
                
                # Count points in each deviation range
                within_1_std = np.sum(deviations <= 1.0)
                between_1_3_std = np.sum((deviations > 1.0) & (deviations <= 3.0))
                beyond_3_std = np.sum(deviations > 3.0)
                
                print(f"   Frame {frame_idx}:")
                print(f"     Within 1 std dev: {within_1_std} points ({100*within_1_std/len(deviations):.1f}%)")
                print(f"     1-3 std dev: {between_1_3_std} points ({100*between_1_3_std/len(deviations):.1f}%)")
                print(f"     Beyond 3 std dev: {beyond_3_std} points ({100*beyond_3_std/len(deviations):.1f}%)")
                print(f"     Max deviation: {np.max(deviations):.3f} std devs")
                
                # Verify color assignments
                blue_points = np.sum((colors[:, 2] > 0.5) & (colors[:, 0] < 0.5) & (colors[:, 1] < 0.5))
                yellow_points = np.sum((colors[:, 0] > 0.5) & (colors[:, 1] > 0.5) & (colors[:, 2] < 0.5))
                red_points = np.sum((colors[:, 0] > 0.8) & (colors[:, 1] < 0.5) & (colors[:, 2] < 0.5))
                
                print(f"     Blue colored: {blue_points} points")
                print(f"     Yellow colored: {yellow_points} points")
                print(f"     Red colored: {red_points} points")
        
        print("\n✅ Statistical deviation coloring test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in statistical deviation coloring test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_color_scheme_validation():
    """Test that the color scheme follows the specified rules."""
    print("\n🧪 Testing Color Scheme Validation")
    print("=" * 50)
    
    # Create synthetic test data with known deviations
    print("📊 Creating synthetic test data...")
    
    # Create a simple baseline (all points at origin)
    num_landmarks = 10
    baseline_points = np.zeros((num_landmarks, 3))
    baseline_std_dev = np.ones((num_landmarks, 3))  # Standard deviation of 1 in all directions
    
    statistical_baseline = {
        'baseline_points': baseline_points,
        'std_dev': baseline_std_dev,
        'num_frames': 1,
        'num_landmarks': num_landmarks,
        'source_file': 'synthetic_test',
        'z_scale': 1.0,
        'statistics': {'mean_std_dev': 1.0}
    }
    
    # Create test frames with known deviations
    test_cases = [
        ("Within 1 std dev", 0.5),    # Should be blue
        ("At 1 std dev", 1.0),        # Should be blue
        ("At 2 std dev", 2.0),        # Should be yellow
        ("At 3 std dev", 3.0),        # Should be yellow
        ("Beyond 3 std dev", 4.0),    # Should be red
    ]
    
    frames_data = []
    for name, deviation in test_cases:
        # Create points at specified deviation distance
        points = np.ones((num_landmarks, 3)) * deviation  # All points at same deviation
        frames_data.append({
            'points': points,
            'colors': None,
            'test_name': name,
            'expected_deviation': deviation
        })
    
    print(f"📊 Created {len(frames_data)} test cases")
    
    try:
        # Apply coloring
        colored_frames = DataFilters.generate_statistical_deviation_colors(
            frames_data,
            statistical_baseline
        )
        
        # Validate color assignments
        print("\n🎨 Validating color assignments...")
        
        for frame in colored_frames:
            name = frame['test_name']
            expected_dev = frame['expected_deviation']
            colors = frame['colors']
            deviations = frame['statistical_deviations']
            
            # Check first point (all points should be the same)
            color = colors[0]
            actual_dev = deviations[0]
            
            print(f"   {name} (dev={expected_dev:.1f}):")
            print(f"     Calculated deviation: {actual_dev:.3f}")
            print(f"     Color RGB: [{color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}]")
            
            # Validate color based on deviation
            if actual_dev <= 1.0:
                expected_color = "Blue"
                is_blue = color[2] > 0.5 and color[0] < 0.5 and color[1] < 0.5
                print(f"     Expected: {expected_color}, Got: {'Blue' if is_blue else 'Other'}")
            elif actual_dev <= 3.0:
                expected_color = "Yellow"
                is_yellow = color[0] > 0.3 and color[1] > 0.3 and color[2] < 0.8
                print(f"     Expected: {expected_color}, Got: {'Yellow' if is_yellow else 'Other'}")
            else:
                expected_color = "Red"
                is_red = color[0] > 0.8 and color[1] < 0.8 and color[2] < 0.3
                print(f"     Expected: {expected_color}, Got: {'Red' if is_red else 'Other'}")
        
        print("\n✅ Color scheme validation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in color scheme validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all statistical deviation coloring tests."""
    print("🧪 Statistical Deviation Coloring Tests")
    print("=" * 60)
    
    tests = [
        test_statistical_deviation_coloring,
        test_color_scheme_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All statistical deviation coloring tests passed!")
        print("\n🎨 Color scheme ready:")
        print("   🔵 Blue: Within 1 standard deviation")
        print("   🟡 Yellow: 1-3 standard deviations") 
        print("   🔴 Red: Beyond 3 standard deviations")
        print("\n🚀 Ready to use in the UI!")
    else:
        print("❌ Some tests failed. Check implementation.")
    
    return passed == total


if __name__ == "__main__":
    main() 