# Final Directory Structure Summary

## Clean Root Directory
The root now contains only essential files and directories:

```
facemesh3D/
├── cleanup_archive/        # Archived old files
├── data/                   # All user data
├── source/                 # Application source code
├── memory/                 # Documentation and memory system
├── .venv/                  # UV-managed virtual environment
├── .git/                   # Git repository
├── SYSTEM_PROMPT.md        # AI system prompt
├── README.md               # Project readme
├── pyproject.toml          # Modern Python project configuration (UV-managed)
├── uv.lock                 # Dependency lock file for reproducible builds
└── .gitignore             # Git ignore rules
```

## Key Changes Made

### 1. **Environment Modernization (2025-01-27)**
- **Replaced** `requirements.txt` → `pyproject.toml` (PEP 621 compliant)
- **Added** `uv.lock` for reproducible dependency resolution
- **Migrated** from conda/pip → UV package manager
- **Upgraded** to Python 3.12 for Open3D 0.19.0 support

### 2. **Moved animations/ → data/animations/**
- All legacy animations now in `data/animations/`
- Updated `file_manager.py` to use new path
- Created README explaining these are legacy files

### 3. **Moved backup_apps/ → cleanup_archive/backup_apps/**
- Pre-refactor code now properly archived
- Keeps root directory clean

### 4. **Organized cleanup_archive/**
```
cleanup_archive/
├── backup_apps/           # Pre-refactor application
├── test_files/            # Test scripts go here
├── temp_scripts/          # Temporary work files
└── old_versions/          # Deprecated code versions
```

### 5. **Data Directory Structure**
```
data/
├── read/                  # Input CSV files
├── write/                 # New animation outputs
└── animations/            # Legacy animations (read-only)
```

### 6. **Environment Structure**
```
.venv/                     # UV-managed virtual environment
├── Scripts/               # Windows activation scripts
├── Lib/                   # Python packages
└── pyvenv.cfg            # Environment configuration
```

## Modern Development Workflow

### Environment Setup
```bash
# Create environment
uv venv .venv --python 3.12

# Activate environment
.venv\Scripts\Activate.ps1

# Install dependencies
uv sync
```

### Key Files
- **`pyproject.toml`**: Project metadata and dependencies (PEP 621)
- **`uv.lock`**: Locked dependency versions for reproducibility
- **`.venv/`**: Isolated Python environment

## Benefits
1. **Clear Separation**: User data vs source code vs archives
2. **Clean Root**: Only essential directories visible
3. **Future-Proof**: Clear rules for where new files go
4. **Git-Friendly**: .gitignore prevents accidental commits
5. **Modern Standards**: UV + pyproject.toml follows current Python best practices
6. **Fast Dependencies**: UV provides 10-100x faster dependency resolution
7. **Reproducible Builds**: Lock file ensures consistent environments

## Environment Commands
- **Setup**: `uv venv .venv --python 3.12 && uv sync`
- **Activate**: `.venv\Scripts\Activate.ps1`
- **Install**: `uv add package_name`
- **Update**: `uv sync`
- **Run App**: `streamlit run source/streamlit_interface.py`

## Remember
- **New animations** → `data/write/`
- **Test scripts** → `cleanup_archive/test_files/`
- **Input CSVs** → `data/read/`
- **Dependencies** → Update `pyproject.toml` then `uv sync`
- **Environment** → Always activate `.venv` before development
- **Never** save to root or `/animations/` 