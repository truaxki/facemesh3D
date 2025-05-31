# Feature Extraction System Guide

## 🎯 Overview

The new feature extraction system enables ML-ready data preparation from facial landmark point clouds. It extracts derived features for training models to predict Subject Name and Test Name from facial movements.

## 🏗️ System Architecture

### Core Components
- **`derived_features.py`**: Main feature extraction module
- **Modified Analysis Tab**: Unified file table + feature extraction UI
- **Processing Pipeline**: Configurable data transformation steps
- **Feature Types**: Displacement vectors + Quaternion rotations

### Key Features
- ✅ **Modular Pipeline**: Rolling average → Filtering → Feature extraction
- ✅ **Multiple Feature Types**: Point displacement + head rotation quaternions
- ✅ **Facial Cluster Integration**: Preset anatomical regions
- ✅ **Flexible Selection**: Single points, ranges, lists, or clusters
- ✅ **Baseline Configuration**: Configurable frame averaging (default: 5 frames)

## 🚀 Quick Start Guide

### 1. Launch Application
```bash
streamlit run source/streamlit_interface.py
```

### 2. Navigate to Analysis
1. **Import Tab**: Select your experiment folder
2. **Analysis Tab**: Go to "File Overview" 
3. **Feature Analysis**: Choose "Feature Extraction"

### 3. Basic Feature Extraction (Nose Tip Test)

#### Step 1: Feature Selection
- **Text Input**: Enter `1` (nose tip landmark)
- **Cluster Presets**: Optionally select facial regions
- **Preview**: See selected landmarks summary

#### Step 2: Processing Pipeline
- **Add Step**: `rolling_average` (window: 3-5 frames)
- **Add Step**: `kabsch_alignment` (baseline: 5 frames)
- **Order Matters**: Steps process sequentially

#### Step 3: Feature Configuration
- **Displacement Features**: ✅ Enable
  - Type: `previous_frame` or `baseline`
  - Baseline Count: 5 frames
- **Quaternion Features**: ✅ Enable (optional)
  - Baseline Count: 5 frames

#### Step 4: Extract Features
- **Select Files**: Choose CSV files to process
- **Extract**: Click "🔥 Extract Features"
- **Results**: View extracted features table

## 📊 Feature Types Explained

### 1. Displacement Features
**Purpose**: Measure local movement of selected facial landmarks

**Types**:
- `previous_frame`: Distance from previous frame
- `baseline`: Distance from baseline average

**Output**: `displacement_landmark_N` (one per selected landmark)

**Example**: For nose tip (landmark 1):
```
displacement_landmark_1: [0.0, 0.003, 0.007, 0.002, ...]
```

### 2. Quaternion Features
**Purpose**: Capture head rotation/orientation changes

**Source**: Rotation matrices from Kabsch alignment → Quaternion conversion

**Output**: 4 features per dataset
```
quaternion_x: [-0.002, 0.001, ...]
quaternion_y: [0.004, -0.001, ...]  
quaternion_z: [0.001, 0.002, ...]
quaternion_w: [0.999, 0.998, ...]
```

## ⚙️ Processing Pipeline Details

### Pipeline Steps
1. **CSV Parsing**: Convert to [478, 3] point cloud format
2. **Rolling Average**: Noise reduction (optional)
3. **Alignment**: Kabsch or Kabsch-Umeyama (optional)
4. **Feature Extraction**: Displacement + Quaternion calculation

### Order Dependency
```
# Different results:
A) displacement (no filter) → filter → different features
B) filter → displacement (filtered) → different features
```

### Configuration Example
```python
config = {
    'selected_indices': [1, 10, 20],  # Nose + others
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
        {'type': 'rolling_average', 'params': {'window_size': 3}},
        {'type': 'kabsch_alignment', 'params': {'baseline_frame_count': 5}}
    ]
}
```

## 🎭 Facial Cluster Presets

### Available Clusters
- **mouth**: Lip regions (upper/lower, inner/outer)
- **right_eye** / **left_eye**: Eye contours + iris
- **eyebrows**: Brow landmarks
- **nose**: Tip, bottom, corners
- **cheeks**: Cheek points
- **face_shape**: Silhouette/outline

### Usage
1. **UI Selection**: Check cluster boxes
2. **Text Append**: Clusters add to text input selection
3. **Example**: Select `lipsLowerInner` → adds landmarks [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]

## 📁 File Structure

### Input Files (READ)
```
data/read/experiment_name/
├── subject1_baseline.csv
├── subject1_test1.csv
├── subject1_test2.csv
└── ...
```

### Output Files (WRITE)
```
data/write/experiment_name/
├── extracted_features_20241028_1430.csv
├── merged_features_20241028_1400.csv
└── ...
```

### Output Format
```csv
source_file,frame_index,time_seconds,displacement_landmark_1,displacement_landmark_10,quaternion_x,quaternion_y,quaternion_z,quaternion_w
subject1_test1.csv,0,0.0,0.0,0.0,0.0,0.0,0.0,1.0
subject1_test1.csv,1,0.033,0.003,0.007,-0.002,0.001,0.004,0.999
...
```

## 🧪 Testing & Validation

### Demo Script
```bash
python demo_feature_extraction.py
```

### Expected Output
```
🚀 Feature Extraction System Demo
✅ DerivedFeatures module imported successfully  
✅ Feature selection parsing works
✅ Facial cluster integration works
✅ Configuration validation works
🎉 Demo completed successfully!
```

### Test Configuration
- **Start Simple**: Use landmark 1 (nose tip) only
- **Single Feature**: Enable displacement, disable quaternions
- **No Pipeline**: Test basic extraction first
- **Verify Output**: Check CSV structure and values

## 🔬 Machine Learning Preparation

### Target Prediction
- **Subject Name**: Extract from filename (e.g., "subject1" from "subject1_test2.csv")
- **Test Name**: Extract from filename (e.g., "test2" from "subject1_test2.csv")

### Model Types (Planned)
1. **Displacement Only**: Frame-to-frame movement patterns
2. **Quaternion Only**: Head rotation/orientation patterns  
3. **Combined**: Both displacement + quaternion features

### Cross-Validation Setup
- **Training/Test Split**: By subject or by trial
- **Feature Selection**: Correlation analysis + dropout
- **Evaluation**: Subject prediction accuracy

## ⚠️ Common Issues & Solutions

### Import Errors
```python
# Ensure proper path
sys.path.append('source')
from derived_features import DerivedFeatures
```

### CSV Format Issues
- **Required**: `feat_N_x`, `feat_N_y`, `feat_N_z` columns (N = 0-477)
- **Optional**: `Time (s)` column for temporal info
- **MediaPipe**: Standard 478 landmark format

### Pipeline Errors
- **Order Matters**: Rolling average before/after alignment gives different results
- **Baseline Count**: Must be ≤ total frames in CSV
- **Invalid Indices**: Landmarks must be 0-477 range

### Memory Issues
- **Large Files**: Process in batches if memory limited
- **Feature Count**: 478 landmarks × multiple features = large output
- **Optimization**: Select specific landmarks vs. all landmarks

## 🎯 Advanced Usage

### Custom Pipeline
```python
# Complex pipeline example
pipeline = [
    {'type': 'rolling_average', 'params': {'window_size': 5}},
    {'type': 'kabsch_umeyama_alignment', 'params': {'baseline_frame_count': 10}},
]
```

### Batch Processing
```python
# Process multiple experiments
for experiment in experiments:
    features = DerivedFeatures.extract_features_from_csv(file, config)
    save_features(features, experiment)
```

### Custom Feature Selection
```python
# Combine manual + cluster selection
manual_indices = DerivedFeatures.parse_feature_selection("1,10,20", [])
cluster_indices = DerivedFeatures.parse_feature_selection("", ["mouth", "nose"])
all_indices = list(set(manual_indices + cluster_indices))
```

## 📈 Performance Optimization

### Feature Selection Strategy
- **Start Small**: Test with 1-5 landmarks
- **Anatomical Groups**: Use facial clusters for logical grouping
- **Correlation Analysis**: Remove redundant features post-extraction
- **Domain Knowledge**: Focus on expressive regions (mouth, eyes, brows)

### Processing Optimization
- **Baseline Frames**: 5-10 frames usually sufficient
- **Rolling Average**: 3-5 frame window for noise reduction
- **Batch Size**: Process 50-100 files at once
- **Memory Management**: Clear session state between large extractions

## 🔄 Workflow Summary

1. **Setup**: Launch Streamlit → Select experiment
2. **Configure**: Choose landmarks + pipeline + features
3. **Extract**: Process selected CSV files
4. **Validate**: Check output format and values
5. **Iterate**: Refine feature selection based on results
6. **Export**: Save features for ML training

**Status**: ✅ Fully implemented and ready for testing! 