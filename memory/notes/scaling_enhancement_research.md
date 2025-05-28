# Scaling Enhancement for Baseline Alignment Pipeline

**Type**: Research Notes  
**Context**: Adding scaling capability to existing Kabsch alignment system  
**Tags**: kabsch-umeyama, scaling, procrustes, facial-normalization, size-differences  
**Date**: 2025-01-28  
**Status**: Research Phase

## Research Summary

Our current custom baseline functionality uses the **Kabsch algorithm** for rigid body alignment (rotation + translation). To handle **size differences** between subjects or sessions, we need to extend this to the **Kabsch-Umeyama algorithm** which adds **uniform scaling**.

## Why Add Scaling?

### Current Limitations
- Size differences between subjects affect comparison accuracy
- Cross-session analysis affected by distance-to-camera variations
- Population studies need size normalization
- Microexpression detection may be masked by size differences

### Benefits of Scaling
- **Subject normalization**: Remove size differences between individuals
- **Cross-session consistency**: Account for different camera distances
- **Population studies**: Enable meaningful cross-subject comparisons
- **Enhanced sensitivity**: Better detection of shape changes vs. size changes

## Mathematical Foundation

### Standard Kabsch Algorithm (Current)
```
Transformation: T(x) = R(x - μ_source) + μ_target
Where:
- R = rotation matrix (3x3)
- μ_source, μ_target = centroids
- No scaling factor
```

### Kabsch-Umeyama Algorithm (Enhanced)
```
Transformation: T(x) = μ_target + c * R * (x - μ_source)
Where:
- R = rotation matrix (3x3)  
- μ_source, μ_target = centroids
- c = uniform scale factor (scalar)
```

## Scale Factor Calculation

The scale factor `c` is computed as:

```python
# Step 1: Calculate variance of source points
sigma_source² = (1/n) * Σ ||x_i - μ_source||²

# Step 2: After SVD of covariance matrix H = U * S * V^T
# Step 3: Calculate scale factor
c = σ_source² / trace(S @ correction_matrix)

# Where correction_matrix handles reflection prevention:
d = sign(det(U) * det(V^T))
correction_matrix = diag([1, 1, ..., 1, d])  # d in last position
```

## Implementation Strategy

### Option 1: Extend Existing DataFilters Class
Add new methods to handle scaling:

```python
def align_frames_to_baseline_with_scaling(frames_data, baseline_frame_idx=0):
    """Kabsch-Umeyama alignment with scaling"""
    pass

def align_frames_to_statistical_baseline_with_scaling(frames_data, baseline):
    """Statistical baseline alignment with scaling"""
    pass

def calculate_scale_factor(source_points, target_points, R):
    """Calculate optimal uniform scale factor"""
    pass
```

### Option 2: New Scaling Module
Create dedicated scaling functionality:

```python
# In source/scaling_alignment.py
class ScalingAlignment:
    def kabsch_umeyama(self, source_points, target_points):
        """Full Procrustes analysis with scaling"""
        pass
    
    def estimate_scale_factor(self, source_points, target_points, R):
        """Estimate optimal scaling factor"""
        pass
```

## Clinical Applications

### Cross-Subject Normalization
```
Scenario: Compare facial expressions across different subjects
Baseline: Population average from multiple neutral expressions  
Analysis: Individual subject emotional expressions
Result: Size-normalized comparison focusing on shape changes
```

### Longitudinal Studies
```
Scenario: Patient progress over months/years
Baseline: Initial session neutral state
Analysis: Follow-up sessions (different camera distances)
Result: Consistent reference accounting for setup variations
```

### Microexpression Enhancement
```
Scenario: Detect subtle expression changes
Baseline: Subject-specific neutral with size normalization
Analysis: Expression sequences with size variations removed
Result: Enhanced sensitivity to actual expression changes
```

## Technical Implementation Details

### Algorithm Steps
1. **Center both point sets** at origin
2. **Calculate source variance** for scaling estimation
3. **Compute covariance matrix** H = source^T @ target
4. **Perform SVD** on H: H = U @ S @ V^T
5. **Handle reflection** prevention with correction matrix
6. **Calculate optimal rotation** R = V @ correction @ U^T
7. **Calculate optimal scale** c = variance_ratio / trace(S @ correction)
8. **Apply transformation** with scaling

### Code Structure
```python
def kabsch_umeyama(source_points, target_points):
    """
    Kabsch-Umeyama algorithm for similarity transformation
    
    Args:
        source_points: (N, 3) array of source coordinates
        target_points: (N, 3) array of target coordinates
        
    Returns:
        R: (3, 3) rotation matrix
        c: scalar scale factor  
        t: (3,) translation vector
        rmsd: root mean square deviation
    """
    # Implementation details follow research papers
    pass
```

## Validation Strategy

### Synthetic Data Testing
- Generate known transformations with scaling
- Verify algorithm recovers correct scale factors
- Test with various scale ranges (0.5x to 2.0x)

### Real Data Validation  
- Compare same subject at different camera distances
- Verify scale factors match expected distance ratios
- Test with statistical baseline scaling

### Clinical Evaluation
- Compare scaled vs unscaled alignment quality
- Measure improvement in cross-subject consistency
- Evaluate microexpression detection enhancement

## User Interface Integration

### New UI Controls
```python
# In streamlit_interface.py
scaling_enabled = st.checkbox("Enable Scaling Normalization")
scaling_mode = st.radio("Scaling Method", [
    "Automatic (Variance-based)",
    "Manual Scale Factor", 
    "Distance-based Estimation"
])
```

### Visual Feedback
- Display calculated scale factors in metadata
- Show before/after scaling comparisons
- Provide scaling quality metrics

## Quality Metrics

### Scale Factor Analysis
- **Range validation**: Reasonable scale factors (0.5-2.0)
- **Consistency check**: Similar subjects should have similar scales
- **Stability test**: Repeated measurements should yield consistent scales

### Alignment Quality
- **RMSD improvement**: Compare scaled vs unscaled alignment error
- **Variance reduction**: Lower variance in population studies
- **Feature preservation**: Ensure scaling doesn't distort key features

## Research References

### Key Papers
1. **Umeyama (1991)**: "Least-squares estimation of transformation parameters between two point patterns" - Original Kabsch-Umeyama formulation
2. **Procrustes Analysis papers**: Foundation for statistical shape analysis with scaling
3. **Facial morphometrics studies**: Application to facial landmark normalization

### Implementation Examples
- **Python libraries**: scikit-learn's Procrustes analysis
- **R packages**: shapes package for morphometric analysis  
- **MATLAB**: Computer Vision Toolbox procrustes function

## Future Enhancements

### Adaptive Scaling
- **Region-specific scaling**: Different scale factors for facial regions
- **Anisotropic scaling**: Non-uniform scaling in x, y, z directions
- **Temporal scaling**: Scale factor evolution over time sequences

### Advanced Applications
- **Scale-invariant features**: Develop features robust to scaling
- **Multi-scale analysis**: Analysis at multiple scale levels
- **Scale-aware baselines**: Baselines that adapt to subject scale

## Implementation Priority

### Phase 1: Core Algorithm
- Implement basic Kabsch-Umeyama algorithm
- Add scale factor calculation
- Integrate with existing baseline methods

### Phase 2: UI Integration  
- Add scaling controls to interface
- Implement scaling quality visualization
- Add scale factor reporting

### Phase 3: Advanced Features
- Region-specific scaling options
- Automated scale validation
- Performance optimization

## Conclusion

Adding scaling to the rotation and displacement correction pipeline will significantly enhance the system's ability to:

1. **Normalize size differences** between subjects and sessions
2. **Improve cross-subject comparison** accuracy
3. **Enable population-level studies** with meaningful averages
4. **Enhance microexpression detection** by removing size variations

The Kabsch-Umeyama algorithm provides a mathematically sound foundation for this enhancement, with clear implementation paths and measurable benefits for facial expression analysis applications. 