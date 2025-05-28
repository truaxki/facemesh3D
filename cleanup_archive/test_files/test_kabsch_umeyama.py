#!/usr/bin/env python3
"""
Test script for Kabsch-Umeyama algorithm implementation.

This script tests:
1. Backward compatibility with legacy Kabsch algorithm
2. Scaling functionality in Kabsch-Umeyama
3. Accuracy of similarity transformation
4. Integration with existing alignment methods
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'source'))

import numpy as np
from data_filters import DataFilters
import time


def create_test_data():
    """Create test point clouds with known transformations."""
    # Original points (478 landmarks, 3D)
    np.random.seed(42)
    n_points = 478
    original_points = np.random.randn(n_points, 3) * 10
    
    # Define known transformation
    # Rotation: 30 degrees around Z-axis
    angle = np.pi / 6  # 30 degrees
    R_true = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    
    # Translation
    t_true = np.array([5.0, -3.0, 2.0])
    
    # Scale factor
    c_true = 1.5
    
    # Apply known transformation
    transformed_points = c_true * (R_true @ original_points.T).T + t_true
    
    return original_points, transformed_points, R_true, t_true, c_true


def test_kabsch_umeyama_accuracy():
    """Test accuracy of Kabsch-Umeyama algorithm recovery."""
    print("🧪 Testing Kabsch-Umeyama accuracy...")
    
    original, transformed, R_true, t_true, c_true = create_test_data()
    
    # Test with scaling enabled
    R_recovered, t_recovered, c_recovered, rmsd = DataFilters.kabsch_umeyama_algorithm(
        original, transformed, enable_scaling=True
    )
    
    # Check transformation quality by applying it
    aligned_points = DataFilters.apply_similarity_transformation(
        transformed, R_recovered, t_recovered, c_recovered
    )
    alignment_error = np.mean(np.linalg.norm(original - aligned_points, axis=1))
    
    print(f"   Recovered rotation matrix determinant: {np.linalg.det(R_recovered):.6f}")
    print(f"   Recovered scale factor: {c_recovered:.6f}")
    print(f"   RMSD after alignment: {rmsd:.6f}")
    print(f"   Mean point alignment error: {alignment_error:.6f}")
    
    # Test that the transformation achieves perfect alignment
    assert alignment_error < 1e-10, f"Point alignment failed: {alignment_error}"
    assert rmsd < 1e-10, f"RMSD too high: {rmsd}"
    
    # Check that rotation matrix is orthogonal
    assert np.allclose(R_recovered @ R_recovered.T, np.eye(3), atol=1e-10), "Rotation matrix not orthogonal"
    
    # Check that determinant is +1 (proper rotation)
    assert abs(np.linalg.det(R_recovered) - 1.0) < 1e-10, f"Rotation determinant not 1: {np.linalg.det(R_recovered)}"
    
    # Check that scale factor is reasonable
    assert c_recovered > 0, f"Scale factor must be positive: {c_recovered}"
    
    print("   ✅ Kabsch-Umeyama accuracy test passed!")


def test_exact_recovery():
    """Test exact parameter recovery with a simpler case."""
    print("\n🎯 Testing exact parameter recovery...")
    
    # Create simple test case with no rotation, only scaling and translation
    np.random.seed(42)
    n_points = 10
    original_points = np.random.randn(n_points, 3) * 5
    
    # Apply only scaling and translation (no rotation)
    scale_true = 2.0
    translation_true = np.array([3.0, -1.0, 4.0])
    
    transformed_points = scale_true * original_points + translation_true
    
    # Recover transformation (Q -> P means transformed_points -> original_points)
    R_recovered, t_recovered, c_recovered, rmsd = DataFilters.kabsch_umeyama_algorithm(
        original_points, transformed_points, enable_scaling=True
    )
    
    # Expected values: to transform Q back to P, we need the inverse transformation
    expected_scale = 1.0 / scale_true  # Inverse of the applied scale
    expected_translation = -translation_true / scale_true  # Inverse transformation
    
    print(f"   Applied scale: {scale_true:.6f}")
    print(f"   Expected recovery scale (1/applied): {expected_scale:.6f}")
    print(f"   Actual recovered scale: {c_recovered:.6f}")
    print(f"   Applied translation: {translation_true}")
    print(f"   Expected recovery translation: {expected_translation}")
    print(f"   Actual recovered translation: {t_recovered}")
    print(f"   Rotation should be identity: {np.allclose(R_recovered, np.eye(3), atol=1e-6)}")
    print(f"   RMSD: {rmsd:.10f}")
    
    # For this simple case, we should get exact recovery
    assert abs(c_recovered - expected_scale) < 1e-6, f"Scale recovery failed: {c_recovered} vs {expected_scale}"
    assert np.allclose(R_recovered, np.eye(3), atol=1e-6), "Rotation should be identity"
    assert rmsd < 1e-10, f"RMSD too high: {rmsd}"
    
    # Most importantly, check that the transformation works perfectly
    aligned_points = DataFilters.apply_similarity_transformation(
        transformed_points, R_recovered, t_recovered, c_recovered
    )
    alignment_error = np.mean(np.linalg.norm(original_points - aligned_points, axis=1))
    assert alignment_error < 1e-10, f"Alignment failed: {alignment_error}"
    
    print("   ✅ Exact recovery test passed!")


def test_scaling_vs_no_scaling():
    """Test difference between scaled and unscaled alignment."""
    print("\n🔍 Testing scaling vs no-scaling behavior...")
    
    # Create data with significant scale difference
    np.random.seed(123)
    n_points = 100
    source_points = np.random.randn(n_points, 3) * 5  # Smaller cloud
    
    # Target is scaled up, rotated, and translated
    angle = np.pi / 4  # 45 degrees
    R = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    scale_factor = 3.0
    translation = np.array([10, -5, 7])
    
    target_points = scale_factor * (R @ source_points.T).T + translation
    
    # Test with scaling enabled
    R1, t1, c1, rmsd1 = DataFilters.kabsch_umeyama_algorithm(
        target_points, source_points, enable_scaling=True
    )
    
    # Test with scaling disabled
    R2, t2, c2, rmsd2 = DataFilters.kabsch_umeyama_algorithm(
        target_points, source_points, enable_scaling=False
    )
    
    print(f"   With scaling: c={c1:.4f}, RMSD={rmsd1:.4f}")
    print(f"   Without scaling: c={c2:.4f}, RMSD={rmsd2:.4f}")
    
    # With scaling should recover the scale factor
    expected_scale = 1.0 / scale_factor  # Because we're aligning source to target
    scale_error = abs(c1 - expected_scale)
    print(f"   Expected scale factor: {expected_scale:.4f}")
    print(f"   Scale recovery error: {scale_error:.4f}")
    
    # Without scaling should have c=1.0
    assert abs(c2 - 1.0) < 1e-10, f"No-scaling should give c=1.0, got {c2}"
    
    # With scaling should have better RMSD
    assert rmsd1 < rmsd2, f"Scaling should improve RMSD: {rmsd1} vs {rmsd2}"
    
    print("   ✅ Scaling vs no-scaling test passed!")


def test_backward_compatibility():
    """Test that legacy kabsch_algorithm works correctly."""
    print("\n🔄 Testing backward compatibility...")
    
    original, transformed, R_true, t_true, c_true = create_test_data()
    
    # Remove scaling from transformed points for fair comparison
    transformed_no_scale = (transformed - t_true) / c_true
    
    # Test legacy method
    R_legacy, t_legacy, rmsd_legacy = DataFilters.kabsch_algorithm(
        original, transformed_no_scale
    )
    
    # Test new method with scaling disabled
    R_new, t_new, c_new, rmsd_new = DataFilters.kabsch_umeyama_algorithm(
        original, transformed_no_scale, enable_scaling=False
    )
    
    # Should give same results
    rotation_diff = np.linalg.norm(R_legacy - R_new, 'fro')
    translation_diff = np.linalg.norm(t_legacy - t_new)
    rmsd_diff = abs(rmsd_legacy - rmsd_new)
    
    print(f"   Rotation difference: {rotation_diff:.6f}")
    print(f"   Translation difference: {translation_diff:.6f}")
    print(f"   RMSD difference: {rmsd_diff:.6f}")
    print(f"   Scale factor (should be 1.0): {c_new:.6f}")
    
    assert rotation_diff < 1e-12, f"Rotation mismatch: {rotation_diff}"
    assert translation_diff < 1e-12, f"Translation mismatch: {translation_diff}"
    assert rmsd_diff < 1e-12, f"RMSD mismatch: {rmsd_diff}"
    assert abs(c_new - 1.0) < 1e-12, f"Scale should be 1.0: {c_new}"
    
    print("   ✅ Backward compatibility test passed!")


def test_frame_alignment():
    """Test frame alignment methods with scaling."""
    print("\n📋 Testing frame alignment methods...")
    
    # Create sample frames data
    np.random.seed(456)
    n_frames = 5
    n_points = 50
    
    frames_data = []
    for i in range(n_frames):
        # Create points with some variation and scaling
        base_points = np.random.randn(n_points, 3) * 5
        scale = 1.0 + 0.1 * i  # Gradually increasing scale
        points = base_points * scale + np.random.randn(3) * 2  # Add translation
        
        frames_data.append({
            'points': points,
            'colors': np.random.rand(n_points, 3)
        })
    
    # Test with scaling enabled
    print("   Testing with scaling enabled...")
    aligned_frames_scaled = DataFilters.align_frames_to_baseline(
        frames_data, baseline_frame_idx=0, enable_scaling=True
    )
    
    # Test with scaling disabled
    print("   Testing with scaling disabled...")
    aligned_frames_no_scale = DataFilters.align_frames_to_baseline(
        frames_data, baseline_frame_idx=0, enable_scaling=False
    )
    
    # Check that scaling was applied correctly
    for i, frame in enumerate(aligned_frames_scaled):
        if i > 0:  # Skip baseline frame
            transform_info = frame['kabsch_transform']
            assert 'scale_factor' in transform_info, "Scale factor missing"
            assert 'algorithm' in transform_info, "Algorithm info missing"
            assert transform_info['algorithm'] == 'kabsch_umeyama', f"Wrong algorithm: {transform_info['algorithm']}"
            assert transform_info['scaling_enabled'] == True, "Scaling not marked as enabled"
            
            print(f"      Frame {i}: scale={transform_info['scale_factor']:.4f}, RMSD={transform_info['rmsd']:.4f}")
    
    # Check no-scaling frames
    for i, frame in enumerate(aligned_frames_no_scale):
        if i > 0:  # Skip baseline frame
            transform_info = frame['kabsch_transform']
            assert abs(transform_info['scale_factor'] - 1.0) < 1e-10, f"Scale should be 1.0: {transform_info['scale_factor']}"
            assert transform_info['algorithm'] == 'kabsch', f"Wrong algorithm: {transform_info['algorithm']}"
            assert transform_info['scaling_enabled'] == False, "Scaling should be marked as disabled"
    
    print("   ✅ Frame alignment test passed!")


def test_performance():
    """Test performance comparison."""
    print("\n⚡ Testing performance...")
    
    # Large dataset
    np.random.seed(789)
    n_points = 478  # Realistic facial landmark count
    n_trials = 100
    
    source = np.random.randn(n_points, 3) * 10
    target = np.random.randn(n_points, 3) * 10
    
    # Time legacy Kabsch
    start_time = time.time()
    for _ in range(n_trials):
        DataFilters.kabsch_algorithm(source, target)
    legacy_time = time.time() - start_time
    
    # Time Kabsch-Umeyama without scaling
    start_time = time.time()
    for _ in range(n_trials):
        DataFilters.kabsch_umeyama_algorithm(source, target, enable_scaling=False)
    no_scale_time = time.time() - start_time
    
    # Time Kabsch-Umeyama with scaling
    start_time = time.time()
    for _ in range(n_trials):
        DataFilters.kabsch_umeyama_algorithm(source, target, enable_scaling=True)
    with_scale_time = time.time() - start_time
    
    print(f"   Legacy Kabsch: {legacy_time:.4f}s ({legacy_time/n_trials*1000:.2f}ms per call)")
    print(f"   Kabsch-Umeyama (no scale): {no_scale_time:.4f}s ({no_scale_time/n_trials*1000:.2f}ms per call)")
    print(f"   Kabsch-Umeyama (with scale): {with_scale_time:.4f}s ({with_scale_time/n_trials*1000:.2f}ms per call)")
    
    # Should be reasonably fast
    assert with_scale_time < 10.0, f"Too slow: {with_scale_time}s"
    
    print("   ✅ Performance test passed!")


def main():
    """Run all tests."""
    print("🧪 Testing Kabsch-Umeyama Implementation")
    print("=" * 50)
    
    test_kabsch_umeyama_accuracy()
    test_exact_recovery()
    test_scaling_vs_no_scaling()
    test_backward_compatibility()
    test_frame_alignment()
    test_performance()
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Kabsch-Umeyama implementation is working correctly.")
    print("\n🎯 Key features verified:")
    print("   • Accurate recovery of rotation, translation, and scaling")
    print("   • Backward compatibility with legacy Kabsch algorithm")
    print("   • Proper integration with frame alignment methods")
    print("   • Scaling normalization capability")
    print("   • Reasonable performance characteristics")


if __name__ == "__main__":
    main() 