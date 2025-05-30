# Facial Clusters Documentation

## Overview
The facial clusters are defined based on MediaPipe Face Mesh 468 landmark model and are used to analyze microexpressions by tracking movement in specific facial regions.

## Cluster Categories

### Individual Clusters
- **Silhouette**: Face outline/shape (38 landmarks)
- **Lips**: Upper/lower, inner/outer contours (44 landmarks total)
- **Eyes**: Upper/lower lids, iris regions (70 landmarks per eye)
- **Eyebrows**: Upper/lower contours (12 landmarks per eyebrow)
- **Nose**: Tip, bottom, corners (5 landmarks)
- **Cheeks**: Left and right (2 landmarks)

### Cluster Groups
- **mouth**: All lip clusters combined
- **right_eye**: All right eye-related clusters
- **left_eye**: All left eye-related clusters
- **eyebrows**: Both eyebrows
- **nose**: All nose landmarks
- **cheeks**: Both cheeks
- **face_shape**: Silhouette cluster

### Expression Associations
- **smile**: mouth + cheeks
- **frown**: mouth + eyebrows
- **surprise**: mouth + eyebrows + eyes
- **squint**: eyes + cheeks
- **disgust**: nose + mouth
- **concentration**: eyebrows + eyes

## Head Movement Compensation

### Methods Available
1. **Off**: No compensation - raw landmark positions
2. **Kabsch**: Rotation and translation alignment
3. **Kabsch-Umeyama**: Rotation, translation, and uniform scaling

### Implementation
- Baseline computed from average of first N frames (default: 30)
- All frames aligned to this baseline
- Movement calculated after alignment to isolate facial expressions

## Analysis Features
- Frame-to-frame displacement calculation
- Per-cluster movement statistics
- Comparison between alignment methods
- Visualization through color mapping in 3D viewer

## Usage in Code
```python
from facial_clusters import FACIAL_CLUSTERS, get_cluster_indices
from data_filters import DataFilters

# Get indices for a specific cluster
lip_indices = get_cluster_indices('lipsUpperOuter')

# Analyze movement in all clusters
cluster_results = DataFilters.analyze_all_clusters(frames_data)

# Compare alignment methods
comparison = DataFilters.compare_alignment_methods(frames_data)
``` 