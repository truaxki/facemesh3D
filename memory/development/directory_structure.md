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
- `/data/animations/` - Legacy animations from pre-refactor (read-only)

### `/memory/`
Documentation and knowledge base:
- `/memory/components/` - Component documentation
- `/memory/features/` - Feature documentation
- `/memory/development/` - Development notes
- `/memory/workflows/` - Workflow guides
- `/memory/architecture/` - System architecture
- `/memory/index/` - Quick references

### `/cleanup_archive/`
Archived old files and backups:
- `/cleanup_archive/test_files/` - Test scripts
- `/cleanup_archive/temp_scripts/` - Temporary scripts
- `/cleanup_archive/old_versions/` - Deprecated code
- `/cleanup_archive/backup_apps/` - Pre-refactor application backup

## Important Notes

1. **All new animations go to `/data/write/`**
2. The `/data/animations/` directory is legacy - don't use it for new outputs
3. Input CSV files should be placed in `/data/read/`
4. The refactored app uses a simplified 2-click workflow
5. Keep the root directory clean - no test files or captures 