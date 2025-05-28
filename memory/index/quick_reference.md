# Quick Reference Guide

**Type**: Quick Reference  
**Context**: Essential information and workflow for facial microexpression analysis system  
**Tags**: reference, workflow, getting-started, kabsch-umeyama, scaling  
**Updated**: 2025-01-28  
**Version**: 3.1 - Kabsch-Umeyama Scaling Enhancement

## System Overview

This system provides **advanced facial microexpression analysis** using CSV landmark data with comprehensive alignment and visualization capabilities:

### Core Features
- **📊 CSV Import**: 478 facial landmarks (`feat_N_x`, `feat_N_y`, `feat_N_z`)
- **🎯 Dual Baseline Methods**: First-frame or statistical multi-frame baselines
- **🔍 Kabsch-Umeyama Alignment**: Rotation + Translation + **Scaling normalization**
- **🎨 Advanced Coloring**: Movement-based, statistical deviation, or single color
- **🎬 Interactive Animation**: Real-time 3D visualization with player controls
- **📹 Export**: MP4 video generation with high-quality rendering

### **NEW: Scaling Enhancement**
- **Size normalization** for cross-subject comparisons
- **Session consistency** across different camera setups
- **Population studies** with meaningful statistical comparisons
- **Legacy compatibility** with scaling disable option

## Quick Start Workflow

### 1. Launch Application
```bash
streamlit run source/streamlit_interface.py --server.port 8507
```

### 2. Import Data (Import Tab)
1. **Select CSV file** with facial landmark data
2. **Configure baseline method**:
   - **First Frame**: Quick analysis (default)
   - **Custom Statistical**: Multi-frame robust baseline
3. **Generate statistical baseline** (if using custom method)

### 3. Create Animation (Animation Tab)
1. **Choose color mode**:
   - **Local Movement**: Microexpression analysis
   - **Statistical Deviation**: Baseline comparison (if custom baseline)
   - **Single Color**: Simple visualization
2. **Configure alignment settings**:
   - ✅ **Enable Size Normalization**: Kabsch-Umeyama with scaling
   - ❌ **Disable**: Legacy Kabsch (rotation + translation only)
3. **Click "Create Facial Animation"**

### 4. View & Export
- **Interactive player** launches automatically
- **Frame-by-frame** navigation in web interface
- **Export to MP4** for presentations/analysis

## File Structure

```
facemesh/
├── source/                 # Application source code
├── data/
│   ├── read/              # Input CSV files
│   ├── write/             # Output animations & videos
│   └── animations/        # Legacy animations (read-only)
├── memory/                # Documentation & guides
└── cleanup_archive/       # Test files & archived code
```

## CSV Data Format

### Required Columns
- `feat_0_x`, `feat_0_y`, `feat_0_z` through `feat_477_x`, `feat_477_y`, `feat_477_z`
- Optional: `Time (s)` for temporal ordering

### Landmark Convention
- **478 facial landmarks** following MediaPipe/similar convention
- **Z-axis scaling**: Automatically applied (25x multiplier)
- **Coordinate system**: Standard computer vision conventions

## Baseline Methods Comparison

| Feature | First Frame | Statistical Baseline |
|---------|-------------|---------------------|
| **Setup** | Immediate | Requires separate CSV |
| **Robustness** | Single frame reference | Multi-frame averaging |
| **Noise Resistance** | Limited | High |
| **Cross-session** | Session-specific | Robust across sessions |
| **Use Case** | Quick analysis | Research, population studies |

## Alignment Methods Comparison

| Algorithm | Transformation | Best For |
|-----------|---------------|----------|
| **Kabsch-Umeyama** | Rotation + Translation + **Scaling** | Cross-subject, longitudinal studies |
| **Kabsch (Legacy)** | Rotation + Translation | Single subject, consistent setup |

### When to Enable Scaling
- ✅ **Cross-subject comparisons** (different face sizes)
- ✅ **Longitudinal studies** (camera distance may vary)
- ✅ **Population analysis** (focus on shape, not size)
- ✅ **Research applications** (normalize anatomical differences)

### When to Disable Scaling  
- ❌ **Size analysis** (preserve actual size information)
- ❌ **Single subject studies** (consistent setup)
- ❌ **Legacy compatibility** (match previous analysis)
- ❌ **Debugging purposes** (isolate scaling effects)

## Color Modes Explained

### 1. Local Movement (Microexpressions)
- **Blue**: Minimal movement (static regions)
- **Green**: Low movement
- **Yellow**: Medium movement  
- **Red**: High movement (active expressions)
- **Use**: Detect subtle facial micro-movements

### 2. Statistical Deviation (Baseline Comparison)
*Available only with custom statistical baseline*
- **🔵 Blue**: Within 1 standard deviation (normal)
- **🟡 Yellow**: 1-3 standard deviations (elevated)
- **🔴 Red**: Beyond 3 standard deviations (extreme)
- **Use**: Compare against expected baseline patterns

### 3. Single Color
- **Uniform coloring** for basic visualization
- **Use**: Simple point cloud display

## Key Session State Variables

```python
# File & Data
st.session_state.csv_data           # Loaded DataFrame
st.session_state.csv_file_path      # Selected file path

# Baseline Configuration  
st.session_state.baseline_mode      # 'first_frame' or 'custom_csv'
st.session_state.statistical_baseline  # Generated baseline data

# Animation Settings
st.session_state.color_mode         # Color visualization mode
st.session_state.enable_scaling     # NEW: Scaling enable/disable
st.session_state.z_scale            # Z-axis multiplier (25.0)

# Animation State
st.session_state.frames_data        # Processed animation frames
st.session_state.animation_created  # Creation status
```

## Interactive Animation Controls

**3D Window Keyboard Controls:**
- `SPACE`: ▶️⏸️ Play/pause animation
- `N/P`: ➡️⬅️ Next/previous frame  
- `R`: 🔄 Reverse direction
- `L`: 🔁 Toggle loop mode
- `0/9`: ⏮️⏭️ First/last frame
- `+/-`: ⚡🐌 Speed control
- `B`: 🎨 Change background
- `S`: 📸 Save screenshot
- `H`: ❓ Show help
- `Q`: 👋 Quit

## Technical Implementation

### Core Algorithms
```python
# Kabsch-Umeyama with scaling
R, t, c, rmsd = DataFilters.kabsch_umeyama_algorithm(
    target_points, source_points, enable_scaling=True
)

# Apply similarity transformation
aligned_points = DataFilters.apply_similarity_transformation(
    source_points, R, t, c
)

# Statistical baseline creation
baseline = DataFilters.create_statistical_baseline_from_csv(csv_path)

# Frame alignment with scaling
aligned_frames = DataFilters.align_frames_to_statistical_baseline(
    frames_data, baseline, enable_scaling=True
)
```

### Quality Metrics
- **RMSD**: Root Mean Square Deviation after alignment
- **Scale factors**: Size adjustment statistics (when scaling enabled)
- **Standard deviations**: Baseline variability measures
- **Coordinate ranges**: Spatial extent validation

## Common Use Cases

### 1. Single Subject Analysis
```
Data: One person's expression sequence
Baseline: First frame
Scaling: Optional (disable for size analysis)
Colors: Local movement
Result: Microexpression detection
```

### 2. Cross-Subject Comparison  
```
Data: Multiple subjects' expressions
Baseline: Population statistical baseline
Scaling: Enable (normalize face sizes)
Colors: Statistical deviation
Result: Normalized cross-subject analysis
```

### 3. Longitudinal Study
```
Data: Same subject across sessions
Baseline: Initial session statistical baseline  
Scaling: Enable (account for camera differences)
Colors: Local movement or statistical deviation
Result: Consistent tracking over time
```

### 4. Population Research
```
Data: Large cohort expressions
Baseline: Population-wide statistical baseline
Scaling: Enable (remove size variability)
Colors: Statistical deviation  
Result: Population-level expression patterns
```

## Troubleshooting

### Data Issues
- **CSV format**: Ensure `feat_N_x/y/z` columns exist
- **Missing data**: Check for NaN values
- **Point count**: Must be consistent (478 landmarks)

### Animation Issues  
- **No movement**: Check if baseline removes all variation
- **Extreme colors**: Adjust color mode normalization
- **Performance**: Reduce frame count for large datasets

### Scaling Issues
- **Unexpected results**: Check scale factor statistics
- **Legacy comparison**: Disable scaling to match old analysis
- **Extreme scaling**: Scale factors outside [0.01, 100] indicate data issues

## Recent Updates (v3.1)

### ✨ Kabsch-Umeyama Enhancement
- **Scaling normalization** for size differences
- **Enhanced UI controls** for scaling enable/disable
- **Scale factor reporting** in alignment statistics
- **Backward compatibility** with legacy Kabsch algorithm

### 🔧 Technical Improvements  
- **Performance optimization** (~0.24ms per alignment)
- **Robust parameter recovery** with constrained scaling
- **Comprehensive testing** suite for algorithm validation
- **Enhanced documentation** with scaling use cases

## Memory System Navigation

- **Features**: `memory/features/` - Detailed feature documentation
- **Notes**: `memory/notes/` - Technical reports and analysis
- **Workflows**: `memory/workflows/` - Step-by-step guides  
- **Architecture**: `memory/architecture/` - System design
- **Index**: `memory/index/` - Quick references and cross-references

**Key Documents**:
- `memory/notes/baseline_definition_report.md` - Complete baseline methodology
- `memory/notes/scaling_enhancement_research.md` - Scaling implementation details
- `memory/features/custom_baseline_functionality.md` - Baseline feature guide 