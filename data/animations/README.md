# Legacy Animations Directory

This directory contains animations created with the pre-refactor version of the application.

## Important Note
**New animations should NOT be saved here!**

In the refactored application:
- Input CSV files go in: `data/read/`
- Output animations go in: `data/write/`

## Contents
These are facial landmark animations from various test sessions, created before the refactoring:
- `facemesh_*` - Facial landmark animations with Kabsch alignment
- `helix_*`, `sphere_*`, `torus_*` - Test shape animations (not facial data)
- `test_facial_animation_*` - Early test animations with different Z-scale factors

## Migration
If you need to use these animations:
1. They can be loaded with the animation player
2. Consider re-processing the source CSV files with the new interface
3. New outputs will be properly saved to `data/write/`

## Note on Directory Structure
These animations use the old naming convention and structure. The refactored application creates animations with better metadata tracking and consistent naming. 