# Environment Setup and Dependency Management

**Type**: Development Guide  
**Context**: Setting up development environment for the facemesh3D project  
**Tags**: `environment`, `uv`, `dependencies`, `setup`, `python`  
**Related**: `development/coding_standards.md`, `user_interactions/current_session.md`  
**Updated**: 2025-01-27

## 📋 Overview

The facemesh3D project uses **UV** as the modern Python package and environment manager, replacing traditional pip/conda workflows. UV provides fast, reliable dependency resolution and virtual environment management.

## 🛠️ Environment Manager: UV

### Why UV?
- **Fast**: 10-100x faster than pip for dependency resolution
- **Modern**: Uses latest Python packaging standards (PEP 621, pyproject.toml)
- **Reliable**: Deterministic builds with lock files
- **Compatible**: Works with existing Python ecosystem

### Installation
```bash
# Install UV
pip install uv

# Verify installation
uv --version
```

## 🐍 Python Version

**Current Standard**: Python 3.12
- **Requirement**: `>=3.12` (specified in pyproject.toml)
- **Reason**: Full Open3D wheel support and modern Python features
- **Compatibility**: All dependencies tested with Python 3.12

```bash
# Install Python 3.12 via UV
uv python install 3.12

# Verify version
uv python list
```

## 📦 Project Structure

### Modern Configuration: pyproject.toml
```toml
[project]
name = "facemesh3d"
version = "0.1.0"
description = "Facial microexpression analysis tool with 3D point cloud visualization."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "streamlit>=1.28.0",
    "numpy>=1.24.0",
    "matplotlib>=3.7.0",
    "pillow>=10.0.0",
    "open3d>=0.17.0",        # Key: 3D point cloud visualization
    "pandas>=2.0.0",
    "opencv-python>=4.8.0",
    "scipy>=1.10.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "black>=23.0.0", "ruff>=0.1.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["source"]
```

## 🚀 Setup Workflow

### 1. Initial Setup
```bash
# Navigate to project directory
cd /path/to/facemesh3D

# Create virtual environment with Python 3.12
uv venv .venv --python 3.12

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install all dependencies
uv sync
```

### 2. Daily Development
```bash
# Activate environment
.venv\Scripts\Activate.ps1

# Update dependencies (if pyproject.toml changed)
uv sync

# Add new dependency
uv add package_name

# Install dev dependencies
uv sync --extra dev
```

## 📋 Key Dependencies

### Core Dependencies
- **Streamlit** (`>=1.28.0`): Web interface framework
- **Open3D** (`>=0.17.0`): 3D point cloud visualization 🎯
- **NumPy** (`>=1.24.0`): Numerical computing
- **OpenCV** (`>=4.8.0`): Computer vision operations
- **Pandas** (`>=2.0.0`): Data manipulation
- **Matplotlib** (`>=3.7.0`): 2D plotting
- **SciPy** (`>=1.10.0`): Scientific computing

### Critical: Open3D Compatibility
- **Version**: 0.19.0 (successfully installed)
- **Python Support**: Works with Python 3.12
- **Windows Wheels**: Available for x86_64
- **Alternative**: Previous attempts with Python 3.13 failed (no wheels)

### Development Tools (Optional)
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Fast Python linter

## 🔧 Environment Commands

### UV Command Reference
```bash
# Environment Management
uv venv .venv --python 3.12    # Create environment
uv sync                        # Install dependencies
uv sync --extra dev           # Include optional dependencies

# Package Management
uv add package_name           # Add dependency
uv remove package_name        # Remove dependency
uv pip list                   # List installed packages
uv pip freeze                 # Export requirements

# Python Management
uv python install 3.12       # Install Python version
uv python list               # List available Python versions
```

### Activation Scripts
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

## ✅ Verification

### Test Installation
```bash
# Test critical imports
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import open3d; print('Open3D:', open3d.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"

# Expected Output:
# Streamlit: 1.45.1
# Open3D: 0.19.0
# NumPy: 2.2.6
# OpenCV: 4.11.0.86
```

### Launch Application
```bash
# Start Streamlit app
streamlit run source/streamlit_interface.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Open3D Installation Failed
- **Symptom**: `Distribution open3d can't be installed`
- **Cause**: Python version incompatibility
- **Solution**: Use Python 3.12 (not 3.13)

#### 2. NumPy Build Errors
- **Symptom**: `ModuleNotFoundError: No module named 'distutils'`
- **Cause**: Old NumPy version with Python 3.12
- **Solution**: Use `numpy>=1.25.0`

#### 3. Dependency Conflicts
- **Symptom**: `No solution found when resolving dependencies`
- **Cause**: Incompatible version constraints
- **Solution**: Adjust `requires-python` range

### Environment Reset
```bash
# Clean slate
rm -rf .venv uv.lock
uv venv .venv --python 3.12
uv sync
```

## 📝 Migration Notes

### From Previous Setup
- **Previous**: Conda/pip-based environment
- **Current**: UV-based with pyproject.toml
- **Benefits**: Faster installs, deterministic builds, modern standards

### File Changes
- **Added**: `pyproject.toml` (replaces requirements.txt)
- **Added**: `uv.lock` (dependency lock file)
- **Maintained**: `.venv/` directory structure

## 🔄 Maintenance

### Regular Tasks
1. **Weekly**: `uv sync` to update dependencies
2. **Monthly**: Check for UV updates (`pip install --upgrade uv`)
3. **Release**: Generate fresh lock file (`rm uv.lock && uv sync`)

### Version Updates
```bash
# Update specific package
uv add package_name@latest

# Update all packages (modify pyproject.toml)
uv sync
```

## 📊 Environment Status

**Current State** (2025-01-27):
- ✅ UV installed and configured
- ✅ Python 3.12.8 active
- ✅ Open3D 0.19.0 successfully installed
- ✅ All core dependencies resolved
- ✅ Virtual environment working
- ✅ Streamlit app launches successfully

**Performance**:
- Dependency resolution: ~0.7s (was minutes with pip)
- Environment creation: ~3s
- Full sync: ~45s (including builds)

---

*This environment setup provides a modern, fast, and reliable development foundation for the facemesh3D project.* 