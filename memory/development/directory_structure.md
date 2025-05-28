# Directory Structure - Refactored Application

## Core Directories

### `/source/`
Contains all application source code:
- `streamlit_interface.py` - Main UI (refactored)
- `file_manager.py` - File I/O operations
- `animation_player.py` - Animation playback
- `visualization.py` - Point cloud visualization
- `data_filters.py` - Data processing filters
- `desktop_launcher.py` - Desktop app launcher
- `viewer_core.py` - Core 3D viewer
- `video_exporter.py` - Video export functionality
- `__init__.py` - Package initialization

### `/data/`
**This is where all user data should be stored:**
- `/data/read/` - Input CSV files for processing
- `/data/write/` - Output animations and exports

### `/memory/`
Documentation and knowledge base:
- `/memory/components/` - Component documentation
- `/memory/features/` - Feature documentation
- `/memory/development/` - Development notes
- `/memory/workflows/` - Workflow guides
- `/memory/architecture/` - System architecture
- `/memory/index/` - Quick references

### `/animations/` (LEGACY)
Contains animations from pre-refactor version. 
**Do NOT save new animations here!**
See `animations/README.md` for details.

### `/backup_apps/`
Backup of pre-refactor code for reference

### `/cleanup_archive/`
Archived old files from cleanup

## Important Notes

1. **All new animations go to `/data/write/`**
2. The `/animations/` directory is legacy - don't use it
3. Input CSV files should be placed in `/data/read/`
4. The refactored app uses a simplified 2-click workflow 