# 🚀 Open3D Point Cloud Visualization System

**The Perfect Hybrid: Web Configuration + Desktop Interactivity**

This system combines the best of both worlds:
- 🌐 **Web Interface**: Easy configuration, file uploads, parameter tweaking
- 🖥️ **Desktop Viewer**: Full Open3D interactivity with smooth rotation, professional lighting, and high-quality rendering

The version you liked from http://localhost:8501/!

## ✨ Features

### Web Control Panel
- 🎛️ **Interactive Configuration**: Shape types, point counts, colors
- 📁 **File Upload**: Support for PLY, PCD, XYZ, and CSV formats
- 👁️ **Live Preview**: Basic matplotlib visualization
- 🚀 **One-Click Launch**: Automatically opens desktop viewer
- 💾 **Export Options**: Download point clouds as PLY files

### Desktop Viewer
- 🎮 **Smooth Real-time Rotation**: Professional mouse controls
- 🎨 **Advanced Rendering**: Proper lighting and shading
- 📸 **Screenshot Capture**: Save high-quality images
- 🔍 **Multiple View Modes**: Zoom, pan, rotate with precision
- ⚡ **High Performance**: Native Open3D rendering speed

## 🚀 Quick Start

### 1. Launch the System
```bash
python main.py
```

This will:
- Start the web control panel
- Open your browser to the configuration interface
- Allow you to generate or upload point cloud data
- Launch the interactive desktop viewer with one click

### 2. Alternative Launch
```bash
streamlit run source/streamlit_open3d_launcher.py
```

### 3. Direct Desktop Viewer
```bash
python source/open3d_desktop_viewer.py --file your_pointcloud.ply
```

## 📊 Workflow

1. **Configure** your point cloud in the web interface
   - Choose from built-in shapes (Sphere, Torus, Helix, Cube)
   - Upload your own PLY/PCD/XYZ/CSV files
   - Adjust parameters with intuitive sliders

2. **Preview** (optional) with matplotlib in the browser

3. **Launch** the desktop viewer for full interactivity
   - Automatic file handling and viewer launch
   - Professional 3D visualization with Open3D

4. **Explore** your data with native desktop tools
   - Mouse controls for rotation, zoom, pan
   - Screenshot and export capabilities

## 📁 Project Structure

```
├── main.py                              # 🚀 Main launcher (START HERE)
├── source/
│   ├── streamlit_open3d_launcher.py     # 🌐 Web control panel  
│   ├── open3d_desktop_viewer.py         # 🖥️ Desktop viewer
│   └── point_cloud.py                   # 📊 Point cloud utilities
├── backup_apps/                         # 📦 Alternative/older apps
├── requirements.txt                     # 📋 Dependencies
└── README.md                           # 📖 This file
```

## 🔧 Installation

### Prerequisites
- Python 3.7+
- Open3D
- Streamlit
- NumPy, Pandas, Matplotlib

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 💡 Tips

### Web Interface (Control Panel)
- ✅ Easy to configure and experiment
- ✅ Great for file uploads and parameter tweaking
- ❌ Limited 3D interactivity (matplotlib-based)

### Desktop Viewer (Interactive)
- ✅ **Smooth real-time rotation and navigation**
- ✅ **Professional lighting and rendering quality**  
- ✅ **High-performance visualization**
- ✅ **Screenshot and export capabilities**

### Best Practices
- Use the web interface to **configure** your data
- Use the desktop viewer to **explore** and **interact**
- The hybrid approach gives you maximum flexibility!

## 🎯 Use Cases

- **Point Cloud Analysis**: Load and explore 3D datasets
- **Algorithm Visualization**: View results of 3D processing
- **Data Exploration**: Interactive investigation of point cloud structure
- **Presentation**: High-quality screenshots and demonstrations
- **Prototyping**: Quick testing of different point cloud configurations

## 🔍 Supported Formats

- **PLY**: Standard point cloud format with colors
- **PCD**: Point Cloud Data format  
- **XYZ**: Simple ASCII coordinates
- **CSV**: X,Y,Z[,R,G,B] columns (RGB optional)

## 🎛️ Controls

### Web Interface
- Sidebar configuration panels
- Interactive sliders and dropdowns
- File upload with drag-and-drop
- One-click desktop viewer launch

### Desktop Viewer  
- **Mouse Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Reset View**: R key
- **Screenshot**: S key
- **Exit**: ESC or close window

## 🚀 Getting Started

1. Run `python main.py`
2. Configure your point cloud in the web interface
3. Click "Launch Interactive Desktop Viewer"
4. Explore your data with full Open3D interactivity!

---

**The perfect combination of web-based ease and desktop power!** 🎉 

# Facemesh Point Cloud Visualization

A streamlined tool for analyzing facial microexpressions through 3D point cloud visualization, optimized for facial landmark CSV data processing.

## 🎯 Purpose

This application focuses on facial landmark visualization and microexpression analysis with:
- Automatic time-based sorting of frames
- Kabsch alignment for head motion removal  
- Local movement visualization
- 2-click workflow: Import → Animate

## 📁 Directory Organization

### Where Files Go:

| File Type | Location | Example |
|-----------|----------|---------|
| **Input CSV files** | `data/read/` | Your facial landmark CSVs |
| **Output animations** | `data/write/` | Generated animations with metadata |
| **Test scripts** | `cleanup_archive/test_files/` | test_*.py files |
| **Temporary files** | `cleanup_archive/temp_scripts/` | One-off scripts |
| **Old code versions** | `cleanup_archive/old_versions/` | Deprecated implementations |
| **Documentation** | `memory/*/` | Feature docs, dev notes |

### ⚠️ Important Rules:
- **NEVER** save new animations to `/animations/` (legacy folder)
- **NEVER** commit `__pycache__` directories
- **ALWAYS** keep the root directory clean
- **ALWAYS** use `data/write/` for outputs

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Your Data**
   - Place facial landmark CSV files in `data/read/`
   - Expected format: `feat_0_x, feat_0_y, feat_0_z, ...` for 478 landmarks
   - Must include `Time (s)` column

3. **Run the Application**
   ```bash
   cd source
   streamlit run streamlit_interface.py --server.port 8507
   ```

4. **Create Animation**
   - Select your CSV file
   - Click "Create Facial Animation"
   - Animation auto-launches in 3D viewer

## 📊 Features

- **Automatic Time Sorting**: Ensures correct frame order
- **Kabsch Alignment**: Removes head motion, isolates facial movement
- **Local Movement Coloring**: Highlights microexpressions
- **Interactive 3D Viewer**: Real-time playback with controls
- **Video Export**: Generate MP4 files
- **Metadata Tracking**: Every output includes processing details

## 🔧 Configuration

Default settings optimized for facial analysis:
- Z-scale: 25x (enhances depth perception)
- Kabsch alignment: Always enabled
- FPS: 15 (adjustable in sidebar)
- Color mode: Local movement (microexpressions)

## 📚 Documentation

Comprehensive documentation in `memory/`:
- `memory/README.md` - Documentation overview
- `memory/components/` - Component details
- `memory/features/` - Feature specifications
- `memory/workflows/` - Usage guides
- `memory/development/` - Development notes

## 🧹 Maintenance

To keep the project clean:
1. Run cleanup scripts periodically
2. Move old files to `cleanup_archive/`
3. Delete cache directories
4. Update documentation in `memory/`

## 🤝 Contributing

When adding new features:
1. Follow the directory structure
2. Update relevant documentation
3. Test files go in `cleanup_archive/test_files/`
4. Keep the streamlined workflow intact

## 📝 License

[Your license information here] 