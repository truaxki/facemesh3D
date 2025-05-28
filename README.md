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
- **NEVER** save new animations to `/data/animations/` (legacy folder)
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
   
   Or from project root:
   ```bash
   streamlit run source/streamlit_interface.py --server.port 8507
   ```

4. **Create Animation**
   - Select your CSV file in the Import tab
   - Click "Create Facial Animation" in the Animation tab
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

## 📊 Workflow

1. **Import** - Load your facial landmark CSV
   - Automatic time-based sorting
   - Preview with statistics

2. **Animate** - Create and play animations
   - One-click animation generation
   - Auto-launch interactive viewer
   - Frame-by-frame preview

3. **Analysis** (Future) - Extract features for ML
   - Coming soon!

## 🎛️ Controls

### Desktop Viewer Controls
- **Space**: Play/Pause animation
- **Left/Right Arrow**: Previous/Next frame
- **Mouse Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **R**: Reset view
- **V**: Export video
- **ESC**: Close viewer

## 📚 Documentation

Comprehensive documentation in `memory/`:
- `memory/README.md` - Documentation overview
- `memory/components/` - Component details
- `memory/features/` - Feature specifications
- `memory/workflows/` - Usage guides
- `memory/development/` - Development notes
- `memory/conversations/` - AI pair programming sessions

## 🧹 Maintenance

To keep the project clean:
1. Input files → `data/read/`
2. Outputs → `data/write/`
3. Test scripts → `cleanup_archive/test_files/`
4. Update docs → `memory/`

## 🤝 Contributing

When adding new features:
1. Work on `dev` branch
2. Follow the directory structure
3. Update relevant documentation
4. Test files go in `cleanup_archive/test_files/`
5. Keep the streamlined workflow intact

## 📝 Project Structure

```
facemesh-visualization/
├── source/                 # Application source code
├── data/                   # User data directory
│   ├── read/              # Input CSV files
│   ├── write/             # Output animations
│   └── animations/        # Legacy animations (read-only)
├── memory/                 # Documentation
├── cleanup_archive/        # Archived/test files
├── requirements.txt        # Python dependencies
├── SYSTEM_PROMPT.md       # AI system context
└── README.md              # This file
```

## 🚀 Remote Repository

Ready to push to GitHub/GitLab. See `memory/development/remote_repository_setup.md` for instructions.

## 📝 License

[Your license information here] 