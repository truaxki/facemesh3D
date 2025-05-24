# 🎬 Zoetrope Point Cloud Viewer

A clean, modular Streamlit application that generates random 3D point clouds, rotates them around the Y-axis, and creates zoetrope-like animations.

## Project Structure

```
facemesh/
├── data/                    # Generated PNG frames and videos
├── source/                  # Python source code
│   ├── point_cloud.py      # Core point cloud logic (89 lines)
│   ├── streamlit_ui.py     # Streamlit interface (140 lines)
│   ├── zoetrope_app.py     # Main entry point (14 lines)
│   └── example_usage.py    # Standalone examples (80 lines)
├── requirements.txt         # Python dependencies (5 lines)
├── run_app.py              # Simple launcher (20 lines)
└── README.md               # This file
```

## 🏗️ Clean Architecture

### 📊 `point_cloud.py` - Core Logic (89 lines)
- **`PointCloudZoetrope`**: Generates and manipulates 3D point clouds
- **`ZoetropeAnimator`**: Creates frames and videos from point clouds
- **Utility functions**: `create_point_cloud()`, `create_animation()`
- **Zero dependencies** on Streamlit

### 🖥️ `streamlit_ui.py` - Interface (140 lines)
- **`ZoetropeApp`**: Complete Streamlit interface
- **Clean separation**: UI logic separate from business logic
- **Progress callbacks**: Real-time updates during generation

### 🚀 `zoetrope_app.py` - Entry Point (14 lines)
- Simple entry point that imports and runs the UI

## Features

- **Random 3D Point Cloud Generation**: Spherical distributions using proper math
- **Y-axis Rotation**: Smooth rotation using rotation matrices
- **PNG Frame Generation**: High-quality images with depth-based coloring
- **Thumbnail Grid View**: Organized display of all frames
- **Animation Preview**: Browser-based playback
- **Video Export**: MP4 creation with customizable FPS
- **Modular Design**: Use core logic independently

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the app:**
```bash
python run_app.py
# OR
streamlit run source/zoetrope_app.py
```

3. **Use the controls** in the sidebar to customize your animation

## API Reference

### Core Classes

```python
# Point cloud generation and manipulation
class PointCloudZoetrope:
    def __init__(self, num_points=100, radius=5)
    def rotate_y(self, angle_degrees)           # Returns rotated points
    def create_frame(self, angle_degrees)       # Returns matplotlib figure
    def save_frame(self, angle_degrees, path)   # Saves PNG file

# Animation creation
class ZoetropeAnimator:
    def __init__(self, point_cloud)
    def generate_frames(self, num_frames=36, data_dir="data", progress_callback=None)
    def create_video(self, frame_paths, output_path, fps=1)
```

### Convenience Functions

```python
def create_point_cloud(num_points=100, radius=5)
def create_animation(num_points, radius, num_frames, data_dir, fps, progress_callback)
```

## Usage Examples

### 🐍 Python Module Usage

```python
from source.point_cloud import PointCloudZoetrope, ZoetropeAnimator

# Create a point cloud
cloud = PointCloudZoetrope(num_points=100, radius=5)

# Generate frames
animator = ZoetropeAnimator(cloud)
frame_paths = animator.generate_frames(num_frames=24)

# Create video
video_path = animator.create_video(frame_paths, fps=2)
```

### 📝 Run Examples

```bash
python source/example_usage.py
```

## How It Works

1. **Point Generation**: Random points distributed in a sphere using spherical coordinates
2. **Rotation**: Y-axis rotation using 3D rotation matrices
3. **Visualization**: 3D matplotlib plots with depth-based coloring
4. **Export**: PNG frames and MP4 video creation

## Customization

### Streamlit Parameters
- **Points**: 50-500 (density of the cloud)
- **Radius**: 1-10 (size of distribution)
- **Frames**: 12-72 (rotation angles)
- **FPS**: 1-10 (video playback speed)

### Programmatic Usage
```python
# Custom point cloud
cloud = PointCloudZoetrope(num_points=500, radius=10)

# Custom animation
frames, video = create_animation(
    num_points=200, radius=8, num_frames=60, fps=5
)
```

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- NumPy 1.24.0+
- Matplotlib 3.7.0+
- Pillow 10.0.0+
- OpenCV 4.8.0+

## Benefits of Clean Design

✅ **Simplicity**: Reduced from 600+ to 350 lines total  
✅ **Clarity**: Clear class names and method signatures  
✅ **Reusability**: Core logic usable anywhere  
✅ **Maintainability**: Single responsibility principle  
✅ **Testability**: Easy to unit test components  

## Tips

- Start with 24 frames for quick generation
- Use FPS=1 for classic zoetrope effect
- Higher point counts create more detailed visuals
- Black background enhances the rotating effect 