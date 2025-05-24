# Point Cloud Animation System 🎬

This system provides tools to create and view animated point cloud sequences, including 360-degree rotations from a single point cloud.

## Quick Start

### 1. Create Sample Animations
```bash
# Create 4 sample animations automatically
python create_sample_animations.py

# Or create individual animations
python rotate_pointcloud.py --sample torus sample_torus.ply torus_anim/ --frames 36
```

### 2. View Animations
```bash
# Launch web interface
python main.py

# In Streamlit: Select "🎬 Animation Folder" and paste path
```

## Tools Overview

### `rotate_pointcloud.py` - Main Animation Creator
Creates 360-degree rotation animations from any point cloud.

**Basic Usage:**
```bash
# Rotate existing PLY file
python rotate_pointcloud.py input.ply output_folder/

# With custom settings
python rotate_pointcloud.py input.ply output/ --frames 60 --axis z
```

**Create Sample + Animate:**
```bash
# Create sample torus and animate it
python rotate_pointcloud.py --sample torus sample.ply output/ --frames 24

# Available samples: torus, helix, sphere
python rotate_pointcloud.py --sample helix sample.ply output/ --frames 72 --axis x
```

**Options:**
- `--frames N`: Number of animation frames (default: 36)
- `--axis {x,y,z}`: Rotation axis (default: y)  
- `--points N`: Points in sample shapes (default: 2000)
- `--no-center`: Don't center at origin before rotation
- `--sample {torus,helix,sphere}`: Create sample shape

### `create_sample_animations.py` - Batch Creator
Creates multiple sample animations for testing.

```bash
python create_sample_animations.py
```

Creates:
- `animations/torus_y_24/` - 24-frame torus rotating on Y-axis
- `animations/helix_z_36/` - 36-frame helix rotating on Z-axis  
- `animations/sphere_x_30/` - 30-frame sphere rotating on X-axis
- `animations/torus_z_48/` - 48-frame high-res torus on Z-axis

## Animation Formats

### Frame Files
Each animation creates sequentially numbered PLY files:
```
frame_000_000.0deg.ply
frame_001_010.0deg.ply
frame_002_020.0deg.ply
...
frame_035_350.0deg.ply
```

### Folder Structure
```
animations/
├── torus_y_24/
│   ├── frame_000_000.0deg.ply
│   ├── frame_001_015.0deg.ply
│   └── ...
├── helix_z_36/
│   ├── frame_000_000.0deg.ply
│   └── ...
└── sphere_x_30/
    └── ...
```

## Viewing Animations

### Web Interface (Streamlit)
1. Run: `python main.py`
2. Select "🎬 Animation Folder" in sidebar
3. Enter folder path (e.g., `C:\path\to\animations\torus_y_24`)
4. Use frame slider or auto-play
5. Export MP4 videos

### Desktop Viewer (Interactive)
The desktop viewer provides full Open3D interactivity:
```bash
# Auto-launch from web interface (recommended)
# Or manual launch:
python source/open3d_desktop_viewer.py --animation config.json --fps 10
```

**Animation Controls:**
- **Spacebar**: Play/Pause
- **Arrow Keys**: Next/Previous frame
- **R**: Reset to first frame
- **Mouse**: Rotate view while animating

## Creating Custom Animations

### From Existing Point Cloud
```bash
# Rotate your own PLY file
python rotate_pointcloud.py my_pointcloud.ply my_animation/

# Different axes create different effects:
python rotate_pointcloud.py my_cloud.ply output/ --axis x  # Tumbling
python rotate_pointcloud.py my_cloud.ply output/ --axis y  # Spinning (default)
python rotate_pointcloud.py my_cloud.ply output/ --axis z  # Rolling
```

### Frame Count Guidelines
- **24 frames**: Smooth rotation (15° steps)
- **36 frames**: Very smooth (10° steps) 
- **48+ frames**: Ultra-smooth (7.5° steps)
- **72 frames**: Cinema-quality (5° steps)

### Time Series Data
For your own time series data, organize as:
```
my_timeseries/
├── frame_001.ply
├── frame_002.ply
├── frame_003.ply
└── ...
```

Then load directly in Streamlit animation viewer.

## Technical Details

### Rotation Mathematics
The system uses standard 3D rotation matrices:

**Y-axis rotation (spinning):**
```
[cos(θ)  0  sin(θ)]
[  0     1    0   ]
[-sin(θ) 0  cos(θ)]
```

**X-axis rotation (tumbling):**
```
[1    0       0   ]
[0  cos(θ) -sin(θ)]
[0  sin(θ)  cos(θ)]
```

**Z-axis rotation (rolling):**
```
[cos(θ) -sin(θ)  0]
[sin(θ)  cos(θ)  0]
[  0       0     1]
```

### Point Cloud Processing
1. **Load**: Read PLY file with Open3D
2. **Center**: Move centroid to origin (optional)
3. **Rotate**: Apply rotation matrix to all points
4. **Save**: Write new PLY with estimated normals

### File Compatibility
- **Input**: PLY, PCD, XYZ formats
- **Output**: PLY format (universally supported)
- **Colors**: Preserved through rotation
- **Normals**: Automatically estimated for better rendering

## Performance Tips

### Memory Usage
- **2,000 points**: ~100KB per frame
- **10,000 points**: ~500KB per frame  
- **48 frames**: ~5-25MB total per animation

### Speed Optimization
- Use fewer frames for testing (`--frames 12`)
- Reduce point count for samples (`--points 1000`)
- Center at origin for faster rotation (`--center` is default)

## Troubleshooting

### Common Issues

**"File not found" errors:**
```bash
# Check file exists
ls my_pointcloud.ply

# Use absolute paths
python rotate_pointcloud.py /full/path/to/input.ply output/
```

**Empty point clouds:**
```bash
# Verify PLY file has points
python -c "import open3d as o3d; pcd=o3d.io.read_point_cloud('file.ply'); print(len(pcd.points))"
```

**Unicode encoding issues (Windows):**
- Script automatically uses ASCII text (no emojis)
- If issues persist, set: `set PYTHONIOENCODING=utf-8`

### Animation Playback Issues

**Frames out of order:**
- Files are naturally sorted alphabetically
- Script names ensure proper order: `frame_000_`, `frame_001_`, etc.

**Choppy animation:**
- Increase frame count: `--frames 48`
- Check FPS setting in viewer
- Use desktop viewer for smoother playback

## Examples Gallery

### Basic Rotations
```bash
# Gentle torus spin (Y-axis)
python rotate_pointcloud.py --sample torus sample.ply gentle/ --frames 24 --axis y

# Fast helix roll (Z-axis) 
python rotate_pointcloud.py --sample helix sample.ply fast/ --frames 12 --axis z

# Sphere tumble (X-axis)
python rotate_pointcloud.py --sample sphere sample.ply tumble/ --frames 36 --axis x
```

### High-Quality Animations
```bash
# Cinema-quality torus (72 frames, 5° steps)
python rotate_pointcloud.py --sample torus sample.ply cinema/ --frames 72 --points 5000

# Ultra-smooth helix (60 frames, 6° steps)
python rotate_pointcloud.py --sample helix sample.ply smooth/ --frames 60 --points 3000
```

### Custom Point Clouds
```bash
# Rotate your mesh data
python rotate_pointcloud.py mesh_export.ply mesh_rotation/ --frames 48

# Keep original position (no centering)
python rotate_pointcloud.py my_cloud.ply output/ --no-center --frames 36
```

## Integration with Your Workflow

This animation system integrates perfectly with:
- **Face mesh data**: Rotate facial point clouds
- **Time series**: Load frame sequences  
- **3D scanning**: Animate scan results
- **Research**: Create publication-quality animations
- **Visualization**: Interactive exploration with Open3D

Happy animating! 🎭 