#!/usr/bin/env python3
"""
Test Custom Baseline Functionality

Tests the new statistical baseline generation and alignment features.
"""

import sys
import numpy as np
from pathlib import Path

# Add source directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "source"))

from data_filters import DataFilters
import pandas as pd


def test_statistical_baseline_creation():
    """Test creating a statistical baseline from CSV data."""
    print("🧪 Testing Statistical Baseline Creation")
    print("=" * 50)
    
    # Find a test CSV file
    data_read_dir = Path("data/read")
    csv_files = list(data_read_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data/read/ directory")
        return False
    
    test_file = csv_files[0]
    print(f"📁 Using test file: {test_file.name}")
    
    try:
        # Create statistical baseline
        statistical_baseline = DataFilters.create_statistical_baseline_from_csv(
            str(test_file),
            z_scale=25.0
        )
        
        print(f"✅ Statistical baseline created successfully!")
        print(f"   Source frames: {statistical_baseline['num_frames']}")
        print(f"   Landmarks: {statistical_baseline['num_landmarks']}")
        print(f"   Mean std dev: {statistical_baseline['statistics']['mean_std_dev']:.4f}")
        print(f"   Coordinate ranges:")
        stats = statistical_baseline['statistics']
        print(f"     X: {stats['coordinate_range']['x'][0]:.3f} to {stats['coordinate_range']['x'][1]:.3f}")
        print(f"     Y: {stats['coordinate_range']['y'][0]:.3f} to {stats['coordinate_range']['y'][1]:.3f}")
        print(f"     Z: {stats['coordinate_range']['z'][0]:.3f} to {stats['coordinate_range']['z'][1]:.3f}")
        
        return statistical_baseline
        
    except Exception as e:
        print(f"❌ Error creating statistical baseline: {str(e)}")
        return False


def test_statistical_baseline_alignment():
    """Test aligning frames to a statistical baseline."""
    print("\n🧪 Testing Statistical Baseline Alignment")
    print("=" * 50)
    
    # Create statistical baseline first
    statistical_baseline = test_statistical_baseline_creation()
    if not statistical_baseline:
        return False
    
    # Find another CSV file for testing alignment
    data_read_dir = Path("data/read")
    csv_files = list(data_read_dir.glob("*.csv"))
    
    if len(csv_files) < 1:
        print("❌ Need at least one CSV file for alignment testing")
        return False
    
    # Use the same file for testing (in real use, would be different)
    test_file = csv_files[0]
    print(f"📁 Aligning frames from: {test_file.name}")
    
    try:
        # Load CSV data and create frames
        df = pd.read_csv(test_file)
        
        # Sort by time if available
        if 'Time (s)' in df.columns:
            df = df.sort_values('Time (s)').reset_index(drop=True)
        
        # Get coordinate columns
        x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
        y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
        z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
        
        # Create frames data (use first 5 frames for testing)
        frames_data = []
        num_test_frames = min(5, len(df))
        
        for i in range(num_test_frames):
            points = np.zeros((len(x_cols), 3))
            for j in range(len(x_cols)):
                points[j] = [
                    df[x_cols[j]].iloc[i],
                    df[y_cols[j]].iloc[i],
                    df[z_cols[j]].iloc[i] * 25.0  # Apply z-scale
                ]
            
            frames_data.append({
                'points': points,
                'colors': None
            })
        
        print(f"📊 Created {len(frames_data)} test frames with {len(points)} landmarks each")
        
        # Test statistical baseline alignment
        aligned_frames = DataFilters.align_frames_to_statistical_baseline(
            frames_data,
            statistical_baseline
        )
        
        print(f"✅ Statistical baseline alignment completed!")
        print(f"   Aligned {len(aligned_frames)} frames")
        
        # Check alignment results
        for i, frame in enumerate(aligned_frames):
            if 'kabsch_transform' in frame:
                transform = frame['kabsch_transform']
                print(f"   Frame {i}: RMSD = {transform['rmsd']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in statistical baseline alignment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_with_first_frame():
    """Compare statistical baseline vs first frame baseline alignment."""
    print("\n🧪 Comparing Statistical vs First Frame Baseline")
    print("=" * 50)
    
    # Find test CSV files
    data_read_dir = Path("data/read")
    csv_files = list(data_read_dir.glob("*.csv"))
    
    if len(csv_files) < 2:
        print("⚠️ Need at least 2 CSV files for comparison (using same file for both)")
        if len(csv_files) < 1:
            print("❌ No CSV files found")
            return False
        baseline_file = csv_files[0]
        test_file = csv_files[0]
    else:
        baseline_file = csv_files[0]
        test_file = csv_files[1]
    
    print(f"📁 Baseline file: {baseline_file.name}")
    print(f"📁 Test file: {test_file.name}")
    
    try:
        # Create statistical baseline
        statistical_baseline = DataFilters.create_statistical_baseline_from_csv(
            str(baseline_file),
            z_scale=25.0
        )
        
        # Load test data
        df = pd.read_csv(test_file)
        if 'Time (s)' in df.columns:
            df = df.sort_values('Time (s)').reset_index(drop=True)
        
        x_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_x')])
        y_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_y')])
        z_cols = sorted([col for col in df.columns if col.startswith('feat_') and col.endswith('_z')])
        
        # Create test frames (first 3 frames)
        frames_data = []
        for i in range(min(3, len(df))):
            points = np.zeros((len(x_cols), 3))
            for j in range(len(x_cols)):
                points[j] = [
                    df[x_cols[j]].iloc[i],
                    df[y_cols[j]].iloc[i],
                    df[z_cols[j]].iloc[i] * 25.0
                ]
            frames_data.append({'points': points, 'colors': None})
        
        # Test both alignment methods
        print("\n📊 First Frame Baseline Alignment:")
        first_frame_aligned = DataFilters.align_frames_to_baseline(
            [frame.copy() for frame in frames_data],
            baseline_frame_idx=0
        )
        
        print("\n📊 Statistical Baseline Alignment:")
        statistical_aligned = DataFilters.align_frames_to_statistical_baseline(
            [frame.copy() for frame in frames_data],
            statistical_baseline
        )
        
        # Compare results
        print("\n📈 Comparison Results:")
        print("Frame | First Frame RMSD | Statistical RMSD | Difference")
        print("-" * 55)
        
        for i in range(len(frames_data)):
            first_rmsd = 0.0
            stat_rmsd = 0.0
            
            if 'kabsch_transform' in first_frame_aligned[i]:
                first_rmsd = first_frame_aligned[i]['kabsch_transform']['rmsd']
            
            if 'kabsch_transform' in statistical_aligned[i]:
                stat_rmsd = statistical_aligned[i]['kabsch_transform']['rmsd']
            
            diff = abs(first_rmsd - stat_rmsd)
            print(f"  {i:2d}  |     {first_rmsd:8.4f}     |     {stat_rmsd:8.4f}     |  {diff:8.4f}")
        
        print("\n✅ Comparison completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in comparison test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all custom baseline tests."""
    print("🧪 Custom Baseline Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_statistical_baseline_creation,
        test_statistical_baseline_alignment,
        test_comparison_with_first_frame
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
        print("✅ All custom baseline functionality tests passed!")
        print("\n🚀 Ready to use custom baseline features in the UI!")
    else:
        print("❌ Some tests failed. Check implementation.")
    
    return passed == total


if __name__ == "__main__":
    main() 