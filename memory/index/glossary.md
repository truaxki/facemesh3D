# Glossary of Terms

**Type**: Index/Reference
**Context**: Technical terminology used throughout the facemesh visualization system
**Tags**: glossary, terminology, definitions
**Related**: All documentation

## A

### Animation Frames
Point cloud data organized as a sequence of frames for playback. Each frame contains 3D points and optional color data.

### Auto Play
Feature that automatically advances through animation frames at a specified frame rate.

## C

### CSV Import
Feature supporting import of facial landmark data from CSV files with columns for x, y, z coordinates and optional movement data.

### Color Mode
Visualization coloring strategy:
- **single**: Uniform color for all points
- **movement**: Colors based on raw movement data from CSV
- **post_filter_movement**: Colors based on frame-to-frame displacement after filtering

## D

### Desktop Viewer
Native Open3D application window for high-performance 3D visualization, launched from the Streamlit interface.

## F

### Facial Landmarks
3D coordinate points representing facial features (478 points in standard MediaPipe face mesh).

### Frame Rate (FPS)
Frames per second for animation playback. Default is 15 FPS.

### Filtering
Data processing to remove unwanted motion or noise:
- **Kabsch Alignment**: Removes rigid body motion (head movement)
- **Smoothing**: Temporal filtering to reduce jitter

## G

### GLFW
Graphics Library Framework - OpenGL window and input handling library used by Open3D.

## K

### Kabsch Algorithm
Optimal rotation alignment algorithm that finds the best rigid transformation between two point sets. Used to remove head motion from facial data.

## M

### Movement Intensity
Magnitude of point displacement between frames, used for color visualization.

### MP4 Export
Video file generation from animation frames using matplotlib rendering and OpenCV encoding.

## N

### Normalization
Scaling of values to a standard range (0-1) for consistent visualization:
- **percentile_95**: Uses 95th percentile as maximum (recommended)
- **percentile_99**: Uses 99th percentile as maximum
- **std_dev**: Standard deviation based
- **max**: Simple min-max normalization

### Normals
Surface normal vectors estimated for point clouds to enable proper lighting and shading.

## O

### Open3D
Open-source library for 3D data processing and visualization.

### OpenGL
Graphics API used for hardware-accelerated 3D rendering.

## P

### PLY Format
Polygon File Format - standard 3D file format supporting points, colors, and other attributes.

### Point Cloud
Collection of 3D points representing a surface or volume in space.

### Post-Filter Movement
Frame-to-frame displacement calculated AFTER filters (like Kabsch alignment) have been applied.

## R

### Rigid Body Motion
Translation and rotation of an entire object without deformation. In facial data, this represents head movement.

### RMSD
Root Mean Square Deviation - measure of average distance between aligned point sets.

## S

### Session State
Streamlit's mechanism for maintaining state between interactions. Stores animation data, settings, and UI state.

### Streamlit
Python framework for creating web applications, used for the main interface.

## T

### Temporary Files
Files created in system temp directory for communication between Streamlit and desktop viewer.

## V

### Visualization Pipeline
1. Data Import → 2. Filtering → 3. Color Mapping → 4. Rendering

### VisualizerWithKeyCallback
Open3D class that supports keyboard input callbacks for interactive controls.

## W

### Web Interface
Browser-based Streamlit application for configuration and control (localhost:8507).

## Z

### Z-axis Scaling
Amplification factor for z-coordinates to enhance depth visualization. Default: 25.0x for facial data.

## Abbreviations

- **FPS**: Frames Per Second
- **UI**: User Interface
- **CSV**: Comma-Separated Values
- **RGB**: Red, Green, Blue color values
- **API**: Application Programming Interface
- **3D**: Three-Dimensional
- **MP4**: MPEG-4 video format
- **AVI**: Audio Video Interleave format

## Metadata
- Created: 2025-01-28T11:52:00Z
- Updated: 2025-01-28T11:52:00Z
- Confidence: High
- Source: Project documentation analysis 