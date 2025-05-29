# Quick Reference Guide

**Type**: Index/Reference
**Context**: Immediate access to critical information for AI agents
**Tags**: quick-reference, cheat-sheet, agent-guide
**Related**: All memory components
**Updated**: 2025-01-28T15:35:00Z (Removed preview/export for simplification)

## Current System Status (At-a-Glance)

### ✅ System Health
- **Application**: Running on `localhost:8507`
- **Status**: Ultra-simplified UI, direct viewer launch
- **Branch**: `animation` (preview/export removed)
- **Latest Changes**: Removed animation preview and export buttons
- **UI Layout**: Import → Animation → Analysis (minimal features)

### 🔧 Recent Accomplishments
- Removed animation preview functionality
- Removed MP4 export button
- Simplified codebase (~100 lines removed)
- Direct launch to 3D viewer only
- Cleaner imports and session state
- Ultra-minimal interface

## Data Organization

### Experiment Structure
- **Input Directory**: `data/read/`
- **Organization**: Experiments → Tests
- **Naming**: Use numeric prefixes (e.g., "01_subject")
- **Baseline**: Append "-baseline" to baseline tests

### Example Structure
```
data/read/
├── 01_subject/
│   ├── test1-baseline.csv
│   └── test2.csv
└── 02_subject/
    ├── baseline.csv
    └── trial1.csv
```

## Critical File Locations

### Primary Application
- **Main Interface**: `source/streamlit_interface.py` (475 lines - refactored)
- **Animation Player**: `source/animation_player.py` (unchanged)
- **Entry Point**: `main.py` (unchanged)

### Data Organization
- **Input CSVs**: `data/read/` (place facial landmark CSVs here)
- **Output Files**: `data/write/` (animations, videos saved here)
- **Legacy Animations**: `animations/` (still compatible)

### Memory System
- **Refactor Plan**: `memory/development/ui_refactor_plan.md`
- **Refactor Details**: `memory/features/ui_refactoring.md` (NEW)
- **Architecture**: `memory/architecture/system_overview.md`
- **Components**: `memory/components/streamlit_interface.md`

## Essential Technical Knowledge

### Application Startup
```bash
# Standard launch
streamlit run source/streamlit_interface.py --server.port 8507
```

### Ultra-Simplified Workflow
1. **Import Tab**: Select experiment
2. **Animation Tab**: Select test → Create Animation
3. **Result**: Direct launch to interactive 3D viewer

### Key Session State Variables (Simplified)
```python
st.session_state.current_experiment  # Selected experiment path
st.session_state.csv_file_path       # Selected test file
st.session_state.csv_data            # Loaded dataframe
st.session_state.frames_data         # Animation frames
st.session_state.animation_created   # Animation ready flag
st.session_state.color_mode          # 'local_movement' or 'single'
st.session_state.baseline_frames     # Number of baseline frames
```

### Removed Features
- ❌ Web-based animation preview
- ❌ MP4 export functionality
- ❌ Frame slider controls
- ❌ Animation metrics display
- ✅ Only interactive 3D viewer remains

## User Preferences (SIMPLIFIED)

### New Workflow
- **Input**: Place CSVs in `data/read/`
- **Process**: 2 clicks to animation
- **Output**: Auto-saved to `data/write/`
- **Viewer**: Auto-launches interactive player

### Removed Features
- ❌ Shape generation (sphere, torus, etc.)
- ❌ Generic file upload
- ❌ User preferences system
- ❌ Multiple filter options
- ❌ Adjustable Z-scale
- ❌ Dual viewer choice

### Color Mode Naming
- **Old**: "post_filter_movement"
- **New**: "local_movement" (clearer for users)

## Common Issues and Solutions

### CSV Files Not Showing
**Problem**: No files in dropdown
**Solution**: Place CSV files in `data/read/` directory

### Animation Naming
**Old Pattern**: `facemesh_e26_session2_136frames`
**New Pattern**: `{source_filename}_{frames}frames_{timestamp}`
**Example**: `subject01_trial3_137frames_20250128_1240`

### Player Launch
**Change**: Now auto-launches interactive player
**No need**: To click separate viewer buttons

## Emergency Procedures

### If Application Won't Start
1. Check port availability: `netstat -ano | findstr :8507`
2. Ensure data directories exist: `data/read/` and `data/write/`
3. Restart: `python main.py`

### If Animation Fails
1. Verify CSV format (feat_0_x, feat_0_y, feat_0_z, ...)
2. Check for 478 landmarks
3. Ensure CSV is in `data/read/`
4. Check `data/write/` permissions

## Code Patterns to Follow

### Tab Structure
```python
# Three tabs only
tab1, tab2, tab3 = st.tabs(["Import", "Animation", "Analysis"])
```

### File Handling
```python
# Input files
csv_files = list(Path("data/read").glob("*.csv"))

# Output files
save_path = Path("data/write") / animation_name
```

### Simplified Animation Creation
```python
# No configuration needed - just create
frames_data = parse_csv_with_defaults()
frames_data = apply_kabsch_alignment(frames_data)
frames_data = apply_local_movement_colors(frames_data)
launch_interactive_player(frames_data)
```

## Memory System Updates

### New Documentation
- `memory/features/ui_refactoring.md` - Refactoring details
- `memory/development/ui_refactor_plan.md` - Planning document

### Updated Documentation
- This file (quick_reference.md)
- `memory/components/streamlit_interface.md` - Added refactor notice

## Success Metrics

### Refactoring Success
- ✅ 52% code reduction (985 → 475 lines)
- ✅ 2-click workflow (was 5-7 clicks)
- ✅ Clear focus on microexpressions
- ✅ Automatic optimal settings
- ✅ Better file organization

### Performance
- Same visualization quality
- Same export capabilities
- Faster workflow
- Less cognitive load

## Final Notes for Future Agents

⚠️ **BRANCH**: Currently on `dev` branch with major refactoring

📋 **FOCUS**: System now specifically for facial microexpression analysis

🎯 **SIMPLICITY**: Removed all non-essential features

🔧 **DEFAULTS**: Optimal settings are now hardcoded

📁 **ORGANIZATION**: Use data/read/ and data/write/ directories

## Metadata
- Created: 2025-01-24T18:15:00Z
- Updated: 2025-01-28T15:15:00Z
- Branch: dev
- Confidence: High
- Source: Complete refactoring implementation 