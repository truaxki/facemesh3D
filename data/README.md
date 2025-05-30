# Data Directory

This directory contains all user data for the facial microexpression analysis tool.

## Structure

### `/read/`
Input directory for CSV files containing facial landmark data.
- Place your CSV files here for processing
- Expected format: `feat_0_x, feat_0_y, feat_0_z, ...` for facial landmarks
- Must include `Time (s)` column

### `/write/`
Output directory for generated animations and exports.
- All new animations are saved here with timestamps
- Each animation includes metadata.json
- MP4 exports also saved here

### `/animations/` (Legacy)
Contains animations created with pre-refactor version.
- These are from the old workflow
- New animations should NOT be saved here
- Use `/write/` for all new outputs

## Important Notes
- Keep input files in `/read/`
- All outputs go to `/write/`
- The `/animations/` folder is legacy - for reference only

## Input Format (data/read/)

Place your facial landmark CSV files in the `read/` directory. Expected format:

- **Columns**: `feat_0_x, feat_0_y, feat_0_z, feat_1_x, ...` up to `feat_477_z`
- **Rows**: Each row represents one frame of facial landmark data
- **Values**: Floating point coordinates in 3D space

Example CSV structure:
```
feat_0_x,feat_0_y,feat_0_z,feat_1_x,feat_1_y,feat_1_z,...
-0.123,0.456,0.789,-0.234,0.567,0.890,...
-0.124,0.457,0.788,-0.235,0.568,0.891,...
```

## Output Format (data/write/)

The system automatically saves all outputs to the `write/` directory:

- **Animation Folders**: `{source_filename}_{frames}frames_{timestamp}/`
  - Contains individual PLY files for each frame
  - Metadata JSON file with animation properties
  
- **Video Exports**: `{animation_name}_export_{timestamp}.mp4`
  - High-quality MP4 videos of animations
  
- **Future**: Feature extraction data for ML training

## Usage

1. Place your CSV files in `data/read/`
2. Launch the application: `python main.py`
3. Select your CSV in the Import tab
4. Create animation in the Animation tab
5. Find outputs in `data/write/`

## Notes

- The system expects 478 facial landmarks (MediaPipe face mesh standard)
- Z-axis values are automatically scaled by 25x for better visualization
- Kabsch alignment is applied to remove head motion
- All timestamps use format: YYYYMMDD_HHMM 