# Legacy Animations Directory

This directory contains animations created with the pre-refactor version of the application.

## Important Note
**New animations should NOT be saved here!**

In the refactored application:
- Input CSV files go in: `data/read/`
- Output animations go in: `data/write/`

## Contents
These are facial landmark animations from various test sessions, created before the refactoring.
They use the old naming convention and structure.

## Migration
If you need to use these animations:
1. They can be loaded with the animation player
2. Consider re-processing the source CSV files with the new interface
3. New outputs will be properly saved to `data/write/` 