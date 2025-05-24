# 🎬 Zoetrope Point Cloud Viewer

A Streamlit application that generates random 3D point clouds, rotates them around the Y-axis, and creates zoetrope-like animations with PNG thumbnails.

## Project Structure

```
facemesh/
├── data/           # Generated PNG frames and videos
├── source/         # Python source code
│   └── zoetrope_app.py
├── requirements.txt
└── README.md
```

## Features

- **Random 3D Point Cloud Generation**: Creates spherical distributions of points in 3D space
- **Y-axis Rotation**: Rotates the point cloud around the Y-axis at customizable speeds
- **PNG Frame Generation**: Saves each rotation angle as a high-quality PNG image
- **Thumbnail Grid View**: Displays all generated frames in an organized grid
- **Animation Preview**: Play the rotation sequence directly in the browser
- **Video Export**: Combine frames into MP4 video with customizable FPS
- **Zoetrope Effect**: Creates smooth optical illusion of motion like classic zoetrope toys

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run source/zoetrope_app.py
```

2. Open your browser and navigate to the displayed URL (usually `http://localhost:8501`)

3. Use the sidebar controls to:
   - Adjust the number of points (50-500)
   - Set the cloud radius (1-10)
   - Choose number of frames (12-72)
   - Set video FPS (1-10)

4. Click "Generate New Point Cloud & Frames" to create a new animation

5. Explore the three tabs:
   - **Thumbnails**: View all generated PNG frames in a grid
   - **Animation Preview**: Play the rotation sequence
   - **Video**: Create and download an MP4 video

## How It Works

1. **Point Cloud Generation**: Random points are distributed within a sphere using spherical coordinates
2. **Rotation**: Each frame rotates the point cloud by a specific angle around the Y-axis
3. **Visualization**: 3D matplotlib plots with depth-based coloring for better visual perception
4. **Frame Export**: Each rotation is saved as a PNG file in the `data/` directory
5. **Video Creation**: OpenCV combines all frames into a smooth video file

## Customization

You can modify the following parameters in the sidebar:
- **Number of Points**: Controls the density of the point cloud
- **Cloud Radius**: Determines the size of the spherical distribution
- **Number of Frames**: Sets how many rotation angles to generate (more frames = smoother animation)
- **Video FPS**: Controls the playback speed of the final video

## Output Files

- PNG frames are saved in `data/frame_XXX_YYY.Ydeg.png` format
- Videos are saved as `data/zoetrope_video.mp4`
- All files can be downloaded directly from the web interface

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- NumPy 1.24.0+
- Matplotlib 3.7.0+
- Pillow 10.0.0+
- OpenCV 4.8.0+

## Tips

- Start with fewer frames (12-24) for faster generation
- Higher point counts create more detailed visualizations
- Use FPS=1 for the classic zoetrope effect (1 frame per second)
- The black background enhances the visual effect of the rotating points 