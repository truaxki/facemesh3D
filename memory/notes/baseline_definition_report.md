# Baseline Definition in Facial Microexpression Analysis

**Type**: Technical Report  
**Context**: Baseline calculation methodology for Kabsch alignment  
**Tags**: baseline, kabsch-alignment, methodology, technical-report  
**Date**: 2025-01-28  
**Status**: Active Implementation

## Executive Summary

Our facial microexpression analysis system employs **dual baseline methodologies** to establish reference frames for Kabsch alignment. Users select between first-frame baselines for immediate analysis or statistical baselines for robust, multi-frame references that reduce noise and improve cross-session consistency.

## Baseline Definition Methods

### Method 1: First Frame Baseline (Default)
**What we do**: Extract the first frame from the current dataset and use its 478 facial landmark coordinates as the reference.

**How we calculate**:
```python
baseline_points = frames_data[0]['points']  # Shape: (478, 3)
```

**When to use**: Quick analysis, single-session data, when the first frame represents a good neutral state.

**Advantages**: 
- Immediate availability
- No additional data required
- Preserves temporal relationship within dataset

### Method 2: Statistical Baseline (Custom)
**What we do**: Generate a statistical baseline by calculating the mean coordinates across multiple frames from a separate CSV file.

**How we calculate**:
```python
# Load baseline CSV with N frames
all_frames_points = np.zeros((N_frames, 478, 3))

# For each frame, extract all landmark coordinates
for frame_idx in range(N_frames):
    for landmark_idx in range(478):
        all_frames_points[frame_idx, landmark_idx] = [x, y, z]

# Calculate statistical baseline
baseline_points = np.mean(all_frames_points, axis=0)  # Mean across frames
std_dev = np.std(all_frames_points, axis=0)          # Standard deviation
```

**When to use**: Cross-session analysis, neutral expression references, population studies, noise reduction.

**Advantages**:
- Robust to individual frame noise
- Consistent reference across sessions
- Enables statistical deviation analysis
- Supports population-level comparisons

## Kabsch Alignment Process

**Objective**: Remove rigid body motion (head movement) while preserving facial expression changes.

**Implementation**:
```python
# For each frame in the analysis dataset
for frame in frames_data:
    current_points = frame['points']
    
    # Apply Kabsch algorithm
    R, t, rmsd = kabsch_algorithm(baseline_points, current_points)
    
    # Transform current frame to align with baseline
    aligned_points = (R @ current_points.T).T + t
    
    # Store transformation metadata
    frame['kabsch_transform'] = {
        'rotation_matrix': R,
        'translation_vector': t,
        'rmsd': rmsd
    }
```

## Statistical Baseline Generation Details

### Data Requirements
- **Input**: CSV file with facial landmark data (`feat_N_x`, `feat_N_y`, `feat_N_z` columns)
- **Landmarks**: 478 facial landmarks per frame
- **Frames**: Multiple frames (typically 20-100 for robust statistics)

### Calculation Pipeline
1. **Load and validate** CSV format
2. **Extract coordinates** for all landmarks across all frames
3. **Apply Z-scaling** (25x multiplier for depth visualization)
4. **Calculate statistics**:
   - Mean coordinates per landmark
   - Standard deviation per landmark
   - Coordinate ranges (min/max)
   - Quality metrics

### Quality Metrics
```python
statistics = {
    'mean_std_dev': np.mean(std_dev),           # Overall variability
    'max_std_dev': np.max(std_dev),             # Maximum instability
    'min_std_dev': np.min(std_dev),             # Minimum variability
    'coordinate_range': {                        # Spatial extent
        'x': [x_min, x_max],
        'y': [y_min, y_max], 
        'z': [z_min, z_max]
    }
}
```

## Baseline Selection Strategy

### Choose First Frame When:
- Analyzing single recording sessions
- First frame represents good neutral state
- Quick exploratory analysis needed
- No separate baseline data available

### Choose Statistical Baseline When:
- Comparing across multiple sessions
- Need robust reference against noise
- Analyzing emotional expressions vs. neutral state
- Conducting population studies
- Require statistical deviation analysis

## Technical Implementation

### Core Methods
```python
# Generate statistical baseline
DataFilters.create_statistical_baseline_from_csv(csv_path, z_scale=25.0)

# Align to statistical baseline
DataFilters.align_frames_to_statistical_baseline(frames_data, baseline)

# Align to first frame (default)
DataFilters.align_frames_to_baseline(frames_data, baseline_frame_idx=0)
```

### Session State Management
```python
st.session_state.baseline_mode          # 'first_frame' or 'custom_csv'
st.session_state.baseline_csv_path      # Path to baseline CSV
st.session_state.statistical_baseline   # Generated baseline dictionary
```

## Validation and Quality Control

### RMSD Analysis
We track Root Mean Square Deviation (RMSD) for each aligned frame:
- **First Frame Baseline**: RMSD = 0.0 for baseline frame, varies for others
- **Statistical Baseline**: All frames show non-zero RMSD, indicating alignment quality

### Statistical Validation
For statistical baselines, we provide:
- Frame count used in baseline generation
- Mean standard deviation across landmarks
- Coordinate range validation
- Stability metrics

## Use Cases in Practice

### Neutral Expression Baseline
```
Baseline CSV: 50 frames of subject at rest
Analysis CSV: Emotional expression sequence
Result: Pure emotional movement without head motion
```

### Cross-Subject Normalization
```
Baseline CSV: Population average from multiple neutral expressions
Analysis CSV: Individual subject data
Result: Normalized comparison across subjects
```

### Longitudinal Studies
```
Baseline CSV: Session 1 neutral state
Analysis CSV: Session 2 data (weeks later)
Result: Consistent reference across time
```

## Future Enhancements

### Planned Improvements
- **Adaptive baselines**: Update baseline during long sequences
- **Region-specific baselines**: Different baselines for facial regions
- **Quality scoring**: Automatic baseline quality assessment
- **Baseline library**: Save/load common baseline configurations

### Research Applications
- **Microexpression detection**: Enhanced sensitivity to subtle changes
- **Clinical assessment**: Standardized references for patient evaluation
- **Cross-cultural studies**: Population-specific baseline development

## Conclusion

Our dual baseline approach provides flexibility for different analysis scenarios while maintaining scientific rigor. The statistical baseline method particularly excels in research applications requiring robust, noise-resistant references, while the first-frame method serves immediate analysis needs effectively.

**Key Innovation**: The combination of Kabsch alignment with statistical baselines enables precise isolation of facial expression changes from head motion, supporting advanced microexpression analysis across diverse research and clinical applications. 