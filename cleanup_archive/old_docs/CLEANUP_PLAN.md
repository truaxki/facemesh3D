# Codebase Cleanup Plan

## 🎯 Goal
Move outdated, redundant, and test files to `cleanup_archive/` to keep the main codebase clean and understandable.

## 📁 Files to Archive

### 1. **Outdated Source Files** → `cleanup_archive/old_source/`
These are the old monolithic files replaced by our new modular architecture:

- `source/streamlit_open3d_launcher.py` (962 lines - replaced by modular components)
- `source/point_cloud.py` (134 lines - replaced by point_cloud_generator.py)  
- `source/open3d_desktop_viewer.py` (496 lines - replaced by viewer_core.py + simple viewer)

### 2. **PNG Test Files** → `cleanup_archive/old_source/`
Generated test images that clutter the source directory:

- `source/example_frame.png`
- `source/custom_frame_*.png` (7 files)

### 3. **Test Files** → `cleanup_archive/test_files/`
Standalone test scripts no longer needed:

- `test_export_fix.py`
- `test_mp4_export.py` 
- `test_troubleshooting.py`
- `create_sample_animations.py`

### 4. **Old Documentation** → `cleanup_archive/old_docs/`
Multiple versions of documentation from development iterations:

- `MEMORY_ARCHITECTURE.md`
- `NEW_SIDEBAR_LAYOUT.md`
- `LAYOUT_REORGANIZED.md` 
- `CLEAN_INTERFACE_APPLIED.md`
- `FINAL_FIX_STATUS.md`
- `MP4_EXPORT_FIX.md`
- `MP4_EXPORT_IMPROVEMENTS.md`
- `fix_summary.md`
- `README_ANIMATIONS.md` (replaced by new docs)

### 5. **Sample Data Files** → `cleanup_archive/sample_data/`
Test PLY files scattered in root directory:

- `quick_video_test.ply`
- `sample_helix.ply`
- `sample_torus.ply` 
- `sample_sphere.ply`
- `test_sphere.ply`
- `test_torus.ply`

### 6. **Test Directories** → `cleanup_archive/test_directories/`
Entire directories with test content:

- `video_test/` (12 test PLY files)
- `test_animation/` (if exists)
- `quick_test/` (if exists)
- `refactored/` (if exists)

## ✅ Files to KEEP in Root

### Core Application Files
- `main.py` - Main launcher
- `requirements.txt` - Dependencies
- `README.md` - Main project documentation

### New Clean Documentation  
- `README_NEW_ARCHITECTURE.md` - Architecture guide
- `REFACTOR_SUMMARY.md` - Refactoring details
- `ANIMATION_VIEWS_UPDATE.md` - Recent animation improvements

### Essential Directories
- `source/` - Clean modular source code (after removing old files)
- `backup_apps/` - Previous cleanup (keep as-is)
- `animations/` - User animation data
- `helix_animation/` - User animation data  
- `torus_animation/` - User animation data
- `memory/` - Memory system (if still used)
- `.git/` - Version control

### Essential Tools
- `rotate_pointcloud.py` - Active tool for generating animations

## 📊 Impact Summary

**Before Cleanup**: 30+ files in root, cluttered source/ directory
**After Cleanup**: ~8 essential files in root, clean source/ directory

### Root Directory - Before (30+ files)
```
├── Various .md files (12+ documentation versions)
├── Test scripts (4+ files)  
├── Sample .ply files (6+ files)
├── Test directories (4+ directories)
├── Essential files (8 files)
```

### Root Directory - After (8 essential files)
```
├── main.py
├── requirements.txt  
├── README.md
├── README_NEW_ARCHITECTURE.md
├── REFACTOR_SUMMARY.md
├── ANIMATION_VIEWS_UPDATE.md
├── rotate_pointcloud.py
├── Essential directories only
```

### Source Directory - Before (18 files)
```
├── New modular files (9 files) ✅ Keep
├── Old monolithic files (3 files) ❌ Archive
├── PNG test images (8 files) ❌ Archive  
```

### Source Directory - After (9 clean files)
```
├── __init__.py
├── streamlit_interface.py
├── point_cloud_generator.py
├── file_manager.py
├── video_exporter.py
├── desktop_launcher.py
├── visualization.py
├── viewer_core.py
├── open3d_desktop_viewer_simple.py
```

## 🎯 Expected Benefits

1. **Cleaner codebase** - Easy to navigate and understand
2. **Clear file purpose** - Every remaining file has a specific role
3. **Reduced confusion** - No duplicate or outdated functionality  
4. **Better maintainability** - Focus on current architecture
5. **Faster development** - Less clutter to wade through

## 📋 Execution Steps

1. Create `cleanup_archive/` with subdirectories
2. Move files systematically by category
3. Verify application still works
4. Update any broken relative paths (if needed)
5. Test the clean codebase

This cleanup will transform the project from a cluttered development workspace into a clean, production-ready codebase that's easy to understand and maintain. 