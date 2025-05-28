# UI Refactoring Plan - Dev Branch

**Type**: Development Documentation
**Context**: Major UI simplification for microexpression analysis focus
**Tags**: refactoring, ui-simplification, development
**Related**: components/streamlit_interface.md, user_interactions/current_session.md
**Created**: 2025-01-28T12:40:00Z

## Objective

Refactor the Streamlit interface to focus specifically on facial microexpression visualization and analysis, removing unnecessary complexity while maintaining core functionality.

## Key Changes

### 1. Tab Structure Simplification
**Current**: Single page with multiple expandable sections
**New**: 3 tabs: Import, Animation, Analysis
- Import: File selection and data preview
- Animation: Animation creation and playback
- Analysis: (Future - for feature identification)

### 2. Data Directory Structure
```
data/
├── read/    # Input CSV files
└── write/   # All system outputs
```

### 3. Streamlined Workflow

#### Import Tab
- File picker defaulting to `data/read/`
- CSV preview (keep existing functionality)
- Automatic progression to Animation tab

#### Animation Tab
- Simplified controls with smart defaults:
  - Color mode: "post_filter_movement" → rename to "local_movement"
  - Z-scale: 25 (default, hidden)
  - Filtering: Always ON with Kabsch only
  - Auto-generate animation name from source file
- One-click animation creation
- Auto-launch interactive player on completion

### 4. Features to Remove
- [ ] Data source dropdown (keep only Facial Landmark CSV)
- [ ] Generate options (sphere, torus, helix, etc.)
- [ ] Upload file option (use file picker only)
- [ ] Animation folder picker (use data/write/)
- [ ] Extra filter options (scale, center, outliers, custom)
- [ ] Orientation comparison checkbox
- [ ] Dual viewer buttons (auto-launch interactive only)
- [ ] "Orientation Fixed" message

### 5. Features to Retain
- [x] CSV file preview with statistics
- [x] Movement intensity visualization
- [x] Frame slider and preview
- [x] Export to MP4 functionality
- [x] Interactive animation player

### 6. Naming Convention
**Current**: `facemesh_e26_session2_136frames`
**New**: `{source_filename}_{num_frames}frames_{timestamp}`
Example: `subject01_trial3_137frames_20250128_1240`

## Implementation Steps

1. **Backup current interface**
   - Copy streamlit_open3d_launcher.py to backup_apps/

2. **Create new streamlined interface**
   - Start with tab structure
   - Implement Import tab
   - Implement Animation tab
   - Stub out Analysis tab

3. **Update file handling**
   - Default paths to data/read/ and data/write/
   - Clean up temporary files

4. **Simplify animation creation**
   - Remove extra options
   - Set smart defaults
   - Auto-launch player

5. **Test core functionality**
   - CSV import
   - Animation creation
   - Player launch
   - Export functionality

6. **Update memory system**
   - Document changes
   - Update component docs
   - Add migration guide

## Code Size Reduction Goals
- Remove ~40% of UI code
- Eliminate unused data generation functions
- Consolidate filter options
- Simplify state management

## User Experience Improvements
- Fewer clicks to animation (goal: 3 clicks)
- Clear workflow progression
- No confusing options
- Automatic optimal settings

## Migration Notes
- Existing animations in `animations/` remain compatible
- User preferences for removed features will be ignored
- Core visualization functionality unchanged 